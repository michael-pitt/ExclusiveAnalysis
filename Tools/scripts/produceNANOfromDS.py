import os
import sys
import optparse
import shutil
import random

def buildCondorFile(opt,FarmDirectory):

    """ builds the condor file to submit the MC production """

    cmssw=os.environ['CMSSW_BASE']
    rand='{:03d}'.format(random.randint(0,123456))
	
    datasets=opt.datasets.split(',')
    if(len(datasets)<2): print('INFO: Process %s'%(datasets[0]))
    else: print('INFO: Processing the following %d datasets:\n%s'%(len(datasets),datasets))

    #condor submission file
    condorFile='%s/condor_generator_%s.sub'%(FarmDirectory,rand)
    print '\nWrites: ',condorFile
    with open (condorFile,'w') as condor:
        condor.write('executable = {0}/worker_{1}.sh\n'.format(FarmDirectory,rand))
        condor.write('output     = {0}/output{1}.out\n'.format(FarmDirectory,rand))
        condor.write('error      = {0}/output{1}.err\n'.format(FarmDirectory,rand))
        condor.write('log        = {0}/output{1}.log\n'.format(FarmDirectory,rand))
        condor.write('+JobFlavour = "testmatch"\n')
        OpSysAndVer = str(os.system('cat /etc/redhat-release'))
        if 'SLC' in OpSysAndVer:
            OpSysAndVer = "SLCern6"
        else:
            OpSysAndVer = "CentOS7"
        condor.write('requirements = (OpSysAndVer =?= "{0}")\n\n'.format(OpSysAndVer))
        condor.write('should_transfer_files = YES\n')
        condor.write('transfer_input_files = %s\n\n'%os.environ['X509_USER_PROXY'])
        for dataset in datasets:
            dataset_name = '_'.join(dataset.split('/')[1:3])
            era = 'era20'+dataset.split('UL')[-1].split('MiniAOD')[0]
			
            #get list of files:
            file_list=os.popen('dasgoclient --query=\"file dataset={} status=*\"'.format(dataset)).read().split()

            #prepare output
            output=opt.output+'/'+dataset_name
            os.system('mkdir -p {}'.format(output))
			
            for file in file_list:
              outfile='%s/%s'%(output,os.path.basename(file))
              if os.path.isfile(outfile): continue
              condor.write('arguments = %s %s %s\n'%(file,output,era))
              condor.write('queue 1\n')
    cmsRunArg='inputFiles=${input} era=${era} outFilename=miniAOD_withProtons.root maxEvents=%d'%(opt.Nevents)
    if opt.nopu: cmsRunArg+=' doSignalOnly=True'
    workerFile='%s/worker_%s.sh'%(FarmDirectory,rand)
    with open(workerFile,'w') as worker:
        worker.write('#!/bin/bash\n')
        worker.write('startMsg="Job started on "`date`\n')
        worker.write('echo $startMsg\n')
        worker.write('export HOME=%s\n'%os.environ['HOME']) #otherwise, 'dasgoclient' won't work on condor
        worker.write('export X509_USER_PROXY=%s\n'%os.environ['X509_USER_PROXY'])
        worker.write('########### INPUT SETTINGS ###########\n')
        worker.write('input=${1}\n')
        worker.write('output=${2}\n')
        worker.write('era=${3}\n')
        worker.write('filename=`echo ${1} | rev | cut -d"/" -f1 | rev`\n')
        worker.write('######################################\n')
        worker.write('WORKDIR=`pwd`/${filename}; mkdir -pv $WORKDIR\n')
        worker.write('echo "Working directory is ${WORKDIR}"\n')
        worker.write('cd %s\n'%cmssw)
        worker.write('eval `scram r -sh`\n')
        worker.write('cd ${WORKDIR}\n')
        worker.write('echo "INFO: starting MINIAOD -> MINIAOD+Protons"\n')
        worker.write('cmsRun $CMSSW_BASE/src/CMSDASTools/AODTools/test/addProtons_miniaod.py %s\n'%cmsRunArg)
        worker.write('[[ ! -f miniAOD_withProtons.root ]] && echo ERROR with addProtons_miniaod.py && exit 1\n')
        worker.write('echo "INFO: starting MINIAOD+Protons -> NANOAOD"\n')
        worker.write('cmsRun $CMSSW_BASE/src/CMSDASTools/AODTools/test/produceNANO.py inputFiles=file:miniAOD_withProtons.root era=${era} outFilename=nano.root\n')
        worker.write('cp nano.root ${output}/${filename}\n')
        worker.write('\necho clean output\ncd ../\nrm -rf ${WORKDIR}\n')
        worker.write('echo ls; ls -l $PWD\n')
        worker.write('echo $startMsg\n')
        worker.write('echo job finished on `date`\n')
    os.system('chmod u+x %s'%(workerFile))

    return condorFile

def main():

    if not os.environ.get('CMSSW_BASE'):
      print('ERROR: CMSSW not set')
      sys.exit(0)
    
    cmssw=os.environ['CMSSW_BASE']

    #configuration
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    parser.add_option('-d', '--datasets', dest='datasets', help='[REQUIRED] input datasets',    type='string')
    parser.add_option('-o', '--out',      dest='output',   help='output directory',  default='/eos/home-m/mpitt/CMSDAS/Samples', type='string')
    parser.add_option('-n', '--nevents',  dest='Nevents',  help='number of events to process',  default=-1, type='int')
    parser.add_option('-s', '--submit',   dest='submit',   help='submit jobs',       action='store_true')
    parser.add_option('-p', '--nopu',     dest='nopu',     help='dont process pileup protons',      action='store_true')
    (opt, args) = parser.parse_args()
     
    if not opt.datasets: parser.error('dataset not given')

    #prepare directory with scripts
    FarmDirectory=os.environ['PWD']+'/FarmLocalNtuple'
    if not os.path.exists(FarmDirectory):  os.system('mkdir -vp '+FarmDirectory)
    print('\nINFO: IMPORTANT MESSAGE: RUN THE FOLLOWING SEQUENCE:')
    print('voms-proxy-init --voms cms --valid 72:00 --out %s/myproxy509\n'%FarmDirectory)
    os.environ['X509_USER_PROXY']='%s/myproxy509'%FarmDirectory

    #build condor submission script and launch jobs
    condor_script=buildCondorFile(opt,FarmDirectory)

    #submit to condor
    if opt.submit:
        os.system('condor_submit {}'.format(condor_script))
    else:
        print('condor_submit {}\n'.format(condor_script))
		

if __name__ == "__main__":
    sys.exit(main())
