# Auto generated configuration file
# using: 
# cmsDriver.py -s NANO --mc --eventcontent NANOAODSIM --datatier NANOAODSIM --filein file:miniAOD_withProtons.root --conditions auto:phase1_2017_realistic -n 100 --era Run2_2018,run2_nanoAOD_106Xv2 --python_filename PPS-RunIISummer20UL18NanoAODv9-00007_1_cfg.py --fileout file:test.root
import FWCore.ParameterSet.Config as cms

# https://gitlab.cern.ch/cms-nanoAOD/nanoaod-doc/-/wikis/Releases/NanoAODv9
from Configuration.Eras.Era_Run2_2016_HIPM_cff import Run2_2016_HIPM
from Configuration.Eras.Era_Run2_2016_cff import Run2_2016
from Configuration.Eras.Era_Run2_2017_cff import Run2_2017
from Configuration.Eras.Era_Run2_2018_cff import Run2_2018
from Configuration.Eras.Modifier_run2_nanoAOD_106Xv2_cff import run2_nanoAOD_106Xv2

from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing ('python')

options.register('isData', False,
                 VarParsing.multiplicity.singleton,
                 VarParsing.varType.bool,
                 "is data"
                 )
options.register('era', 'era2017',
                 VarParsing.multiplicity.singleton,
                 VarParsing.varType.string,
                 "choose era"
                 )			                  
options.register('outFilename', 'output_nano.root',
                 VarParsing.multiplicity.singleton,
                 VarParsing.varType.string,
                 "Output file name"
                 )                 
options.parseArguments()

print("INFO: Era set to", options.era)
print("INFO: isData set to", options.isData)


if '2016preVFP' in options.era:
    process = cms.Process('NANO',Run2_2016_HIPM,run2_nanoAOD_106Xv2)
elif '2016' in options.era:
    process = cms.Process('NANO',Run2_2016,run2_nanoAOD_106Xv2)
elif '2017' in options.era:
    process = cms.Process('NANO',Run2_2017,run2_nanoAOD_106Xv2)
elif '2018' in options.era:
    process = cms.Process('NANO',Run2_2018,run2_nanoAOD_106Xv2)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('PhysicsTools.NanoAOD.nano_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(options.maxEvents),
	output = cms.optional.untracked.allowed(cms.int32,cms.PSet)
)

# process stdout
process.MessageLogger.cerr.threshold = cms.untracked.string('')
process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(500)

# Input source
process.source = cms.Source("PoolSource",
                            fileNames = cms.untracked.vstring(options.inputFiles),
                            inputCommands = cms.untracked.vstring('keep *', 
                            # drop the old event content, since it is empty
                            'drop recoForwardProtons_ctppsProtons_multiRP_RECO', 
                            'drop recoForwardProtons_ctppsProtons_singleRP_RECO'),
                            duplicateCheckMode = cms.untracked.string('noDuplicateCheck'),
							secondaryFileNames = cms.untracked.vstring()
                            )

process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(False) 
)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('--python_filename nevts:-1'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.NANOAODSIMoutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('NANOAODSIM'),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string('file:'+options.outFilename),
    outputCommands = process.NANOAODSIMEventContent.outputCommands
)

# Additional output definition

# Other statements
# global tag
from Configuration.AlCa.GlobalTag import GlobalTag
from CMSDASTools.AODTools.EraConfig import getEraConfiguration
globalTag = getEraConfiguration(era=options.era,isData=options.isData)
print("INFO: globalTag set to "+globalTag)
process.GlobalTag = GlobalTag(process.GlobalTag, globalTag, '')

# Need these modifications to use fitVtxY=False option (not recommended by POG)
#process.filteredProtons.protons_multi_rp.chi_sq_max=1e-4 # modify it properly
#print('FIXME MultiRP proton reco: filteredProtons->ctppsProtons')
#process.protonTable.tagRecoProtonsMulti=cms.InputTag("ctppsProtons", "multiRP")
#process.multiRPTable.src=cms.InputTag("ctppsProtons","multiRP")


# Path and EndPath definitions
process.nanoAOD_step = cms.Path(process.nanoSequenceMC)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.NANOAODSIMoutput_step = cms.EndPath(process.NANOAODSIMoutput)

# Schedule definition
process.schedule = cms.Schedule(process.nanoAOD_step,process.endjob_step,process.NANOAODSIMoutput_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# customisation of the process.

# Automatic addition of the customisation function from Configuration.DataProcessing.Utils
from PhysicsTools.NanoAOD.nano_cff import nanoAOD_customizeMC 

#call to customisation function addMonitoring imported from Configuration.DataProcessing.Utils
process = nanoAOD_customizeMC(process)
process.genProtonTable.srcPUProtons = cms.InputTag('genPUProtons', 'genPUProtons')

# End of customisation functions

# Customisation from command line

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
