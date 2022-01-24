# Tools

Contains scripts to produce nanoAOD files with PPS content.

## CMSSW setup
```
cmsrel CMSSW_12_3_0_pre1
cd CMSSW_12_3_0_pre1/src
cmsenv

#Add direct simulation and genProton content (not in release yet)
git cms-merge-topic michael-pitt:ppsSim_fix
scram b -j

#This package
git clone git@github.com:michael-pitt/ExclusiveAnalysis.git
scram b -j
```

## Making NANOAOD (with proton info)

The current version of NanoAOD MC samples doesn't include simulated protons. Recently a proton simulation module has been developed, and it is being tested. We will use this new module to add protons to the MC simulation sample and produce nanoAOD with corresponding proton content.

To produce NANOAODs the following sequence should be executed: MINIAOD->MINIAOD+Protons->NANOAOD:

   1. Proton simulation: the code will propagate all final state protons within the RP acceptance, simulate PPS hits, and run the proton reconstruction module.
```
cmsRun $CMSSW_BASE/src/ExclusiveAnalysis/Tools/test/addProtons_miniaod.py inputFiles=file:miniAOD.root era="era2018" instance=""
```
NOTE: Check the input file which collection is used to store the pileup protons.
   2. MINIAOD->NANOAOD step
To produce nanoAOD from miniAOD run:
```
cmsRun $CMSSW_BASE/src/ExclusiveAnalysis/Tools/test/produceNANO.py inputFiles=file:miniAOD_withProtons.root era="era2018" outFilename=output_nano.root
```

### Submitting to condor
To produce all steps in one shot, you can run the following script:
```
python scripts/produceNANOfromDS.py -d /DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1_ext1-v1/MINIAODSIM
```
   - add `-s` if you wish to submit the code to condor.
   - add `-o` to set the output folder (EOS)
   - add `-n` to set the number of events per job.
   

