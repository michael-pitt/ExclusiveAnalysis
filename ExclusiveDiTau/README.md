# ExclusiveDiTau
Production of small ntuples from nanoAODs. These ntuples are used in the measurement of the exclusive di-tau production cross-section

## CMSSW setup
```
cmsrel CMSSW_10_6_29
cd CMSSW_10_6_29/src
cmsenv

#setup nanoAOD-tools
git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools
scram b -j

#This package
git clone https://github.com/michael-pitt/ExclusiveAnalysis.git
scram b -j
```

## Analysis


Analysis code is in [DiTau_analysis.py](https://github.com/michael-pitt/ExclusiveAnalysis/blob/main/ExclusiveDiTau/python/DiTau_analysis.py), which select events, compute high level variables and write a skimmed output tree

TAU POG recomendation of tau objects in nanoAODs: https://github.com/cms-tau-pog/TauFW/tree/master/PicoProducer/python/analysis

Three analysis modules can be executed:
- `analysis_hadhad`: 2 tight hadronic taus with opposite charge, tau_pt>50GeV 
- `analysis_lephad`: 1 tight hadronic taus and 1 light lepton, with opposite charge, tau_pt>50GeV, lep_pt>30GeV. 
- `analysis_leplep`: 2 leptons with opposite charge, lep_pt>50GeV

For each event selection:
- An appropriate `keep_and_drop` files can be chosen (see list of files [here](https://github.com/michael-pitt/ExclusiveAnalysis/tree/main/ExclusiveDiTau/scripts))
- A corresponding trigger should be set

json file are stored in [data](https://github.com/michael-pitt/ExclusiveAnalysis/tree/main/ExclusiveDiTau/data) folder

### Running on a single file:

example of running on a file from `SingleMuon` stream
```
python $CMSSW_BASE/src/PhysicsTools/NanoAODTools/scripts/nano_postproc.py \
output root://cms-xrd-global.cern.ch//store/data/Run2018A/DoubleMuon/NANOAOD/UL2018_MiniAODv2_NanoAODv9-v1/270000/C218937D-A2AC-9949-8E65-D14C50F824AF.root \
--json ${CMSSW_BASE}/src/ExclusiveAnalysis/ExclusiveDiTau/data/CMSgolden_2RPGood_anyarms.json \
--bi $CMSSW_BASE/src/ExclusiveAnalysis/ExclusiveDiTau/scripts/keep_in.txt \
--bo $CMSSW_BASE/src/ExclusiveAnalysis/ExclusiveDiTau/scripts/keep_out.txt \
-c "HLT_IsoMu24" -I ExclusiveAnalysis.ExclusiveDiTau.DiLep_analysis analysis_mudata
```

example of running on a MC (`nano.root` can be replaced by any NANOAOD file)
```
python $CMSSW_BASE/src/PhysicsTools/NanoAODTools/scripts/nano_postproc.py \
output nano.root \
--bi $CMSSW_BASE/src/ExclusiveAnalysis/ExclusiveDiTau/scripts/keep_in.txt \
--bo $CMSSW_BASE/src/ExclusiveAnalysis/ExclusiveDiTau/scripts/keep_out.txt \
-c "1" -I ExclusiveAnalysis.ExclusiveDiTau.DiTau_analysis analysis_hadhad
```

### Submitting to condor

To submit condor jobs for an entire data set:

You can use [runNtuplizer.py](https://github.com/michael-pitt/ExclusiveAnalysis/blob/main/ExclusiveDiTau/scripts/runNtuplizer.py) script to submit jobs from a list of datasets.
The list of datasets should be provided as a `txt` file, for example [listSamples.txt](https://github.com/michael-pitt/ExclusiveAnalysis/blob/main/ExclusiveDiTau/data/listSamples.txt).

Run the following command
```
python $CMSSW_BASE/src/ExclusiveAnalysis/ExclusiveDiTau/scripts/runNtuplizer.py --in $CMSSW_BASE/src/ExclusiveAnalysis/Analysis/data/listSamples.txt
```
with options
- `--out`: Output folder (for example */eos/home-X/$USER/...*)
- `--in`: Input *txt* file with list of datasets or folders where NANOAOD are stored

NOTE: When executing the script, you will be requested to create a `proxy` in the submission foder:

```
voms-proxy-init --voms cms --valid 72:00 --out $PWD/FarmLocalNtuple/myproxy509
```

### Merging results

To merge the output files, run [haddnano.py](https://github.com/cms-nanoAOD/nanoAOD-tools/blob/master/scripts/haddnano.py) script:
```
python $CMSSW_BASE/src/PhysicsTools/NanoAODTools/scripts/haddnano.py output.root ListOfROOTFiles
```
