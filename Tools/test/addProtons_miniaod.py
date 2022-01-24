import FWCore.ParameterSet.Config as cms
'''
An example file taken from:
https://github.com/forthommel/cmssw/blob/47b387a9ce910fc84b75c08c059f789a48675db3/SimPPS/Configuration/test/test_miniAOD_cfg.py
'''
from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing ('python')

options.register('era', 'era2017',
                 VarParsing.multiplicity.singleton,
                 VarParsing.varType.string,
                 "choose era"
                 )			 
options.register('doSignalOnly', False,
                 VarParsing.multiplicity.singleton,
                 VarParsing.varType.bool,
                 "Exclude PU protons"
                 )	                 
options.register('outFilename', 'miniAOD_withProtons.root',
                 VarParsing.multiplicity.singleton,
                 VarParsing.varType.string,
                 "Output file name"
                 )                 
options.parseArguments()


#start process
from Configuration.StandardSequences.Eras import eras
if '2016preVFP' in options.era:
    process = cms.Process('PPS',eras.Run2_2016_HIPM)
elif '2016' in options.era:
    process = cms.Process('PPS',eras.Run2_2016)
elif '2017' in options.era:
    process = cms.Process('PPS',eras.Run2_2017)
elif '2018' in options.era:
    process = cms.Process('PPS',eras.Run2_2018)

process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
if '2016preVFP' in options.era:
    process.GlobalTag = GlobalTag(process.GlobalTag, '106X_mcRun2_asymptotic_preVFP_v11', '')
elif '2016' in options.era:
    process.GlobalTag = GlobalTag(process.GlobalTag, '106X_mcRun2_asymptotic_v17', '')
elif '2017' in options.era:
    process.GlobalTag = GlobalTag(process.GlobalTag, '106X_mc2017_realistic_v9', '')
elif '2018' in options.era:
    process.GlobalTag = GlobalTag(process.GlobalTag, '106X_upgrade2018_realistic_v16_L1v1', '')

 
# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')

# PPS simulation and reconstruction chains with standard settings
process.load('Validation.CTPPS.PPS_config_cff')
process.load('SimPPS.Configuration.directSimPPS_cff')
process.load('RecoPPS.Configuration.recoCTPPS_cff')

#message logger
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.threshold = cms.untracked.string('')
process.MessageLogger.cerr.FwkReport.reportEvery = 500

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(options.maxEvents)
)

process.RandomNumberGeneratorService = cms.Service("RandomNumberGeneratorService",
    beamDivergenceVtxGenerator = cms.PSet(initialSeed = cms.untracked.uint32(3849)),
    ppsDirectProtonSimulation = cms.PSet(initialSeed = cms.untracked.uint32(4981))
)

# Input source
process.source = cms.Source("PoolSource",
                            fileNames = cms.untracked.vstring(options.inputFiles),
                            duplicateCheckMode = cms.untracked.string('noDuplicateCheck') 
                            )

from SimPPS.DirectSimProducer.profile_base_cff import matchDirectSimOutputs
matchDirectSimOutputs(process, miniAOD=True)

# for multiRP fit, set if you want to use x* and y* as free parameters or set them to zero
process.ctppsProtons.fitVtxY = True
#if false then ndof=1 and chi2 values will be big (filteredProton container will be empty)
                          
#If interested in the reconstruction of signal protons only (no PU), uncomment this line:
if options.doSignalOnly:
  print('INFO: reconstruct only signal protons (from hard process)')
  process.beamDivergenceVtxGenerator.srcGenParticle = cms.VInputTag(cms.InputTag("prunedGenParticles"))

# Output definition
process.MINIAODSIMoutput = cms.OutputModule("PoolOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(4),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string(''),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string(options.outFilename),
    outputCommands = process.MINIAODSIMEventContent.outputCommands
)

# Path and EndPath definitions
process.p = cms.Path(
    process.directSimPPS
  * process.recoDirectSimPPS
)
process.outpath = cms.EndPath(process.MINIAODSIMoutput)
