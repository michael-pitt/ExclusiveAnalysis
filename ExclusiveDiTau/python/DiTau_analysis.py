#!/usr/bin/env python
import os, sys, math
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module

from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection

### Proton selector be replaced by preprocessing module
from CMSDASTools.Analysis.objectSelector import ProtonSelector
from CMSDASTools.Analysis.objectSelector import ElectronSelector, MuonSelector

class Analysis(Module):
    def __init__(self, channel, isMC):
        self.channel = channel
        self.isMC    = isMC
        pass

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    
        self.out = wrappedOutputTree
        self.out.branch("EventNum",          "I");
        self.out.branch("nLepCand",          "I");
        self.out.branch("LepCand_id",        "I",  lenVar = "nLepCand");
        self.out.branch("LepCand_pt",        "F",  lenVar = "nLepCand");
        self.out.branch("LepCand_eta",       "F",  lenVar = "nLepCand");
        self.out.branch("LepCand_phi",       "F",  lenVar = "nLepCand");
        self.out.branch("LepCand_charge",    "I",  lenVar = "nLepCand");
        self.out.branch("LepCand_dxy",       "F",  lenVar = "nLepCand");
        self.out.branch("LepCand_dz",        "F",  lenVar = "nLepCand");
        self.out.branch("nRecoProtCand",     "I");
        self.out.branch("ProtCand_xi",       "F",  lenVar = "nRecoProtCand");
        self.out.branch("ProtCand_t",        "F",  lenVar = "nRecoProtCand");
        self.out.branch("ProtCand_ThX",      "F",  lenVar = "nRecoProtCand");
        self.out.branch("ProtCand_ThY",      "F",  lenVar = "nRecoProtCand");
        self.out.branch("ProtCand_rpid",     "I",  lenVar = "nRecoProtCand");
        self.out.branch("ProtCand_arm",      "I",  lenVar = "nRecoProtCand");
        self.out.branch("ProtCand_ismultirp","I",  lenVar = "nRecoProtCand");
        self.out.branch("ProtCand_rpid",     "I",  lenVar = "nRecoProtCand");
        self.out.branch("nJets",             "I");
        self.out.branch("Lep0Pt",            "F");
        self.out.branch("Lep1Pt",            "F");
        self.out.branch("Lep0Eta",           "F");
        self.out.branch("Lep1Eta",           "F");
        self.out.branch("Lep0Phi",           "F");
        self.out.branch("Lep1Phi",           "F");
        self.out.branch("InvMass",           "F");
        self.out.branch("Yll",               "F");
        self.out.branch("pTll",              "F");
        self.out.branch("Acopl",             "F");
        if self.isMC:
            self.out.branch("gen_mpp",           "F");
            self.out.branch("gen_Ypp",           "F");
 
        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass


    def selectElectrons(self, event, elSel):

        event.selectedElectrons = []
        electrons = Collection(event, "Electron")
        for el in electrons:
            if not elSel.evalElectron(el): continue
            setattr(el, 'id', 11)
            event.selectedElectrons.append(el)
        event.selectedElectrons.sort(key=lambda x: x.pt, reverse=True)
        

    def selectMuons(self, event, muSel):
        ## access a collection in nanoaod and create a new collection based on this

        event.selectedMuons = []
        muons = Collection(event, "Muon")
        for mu in muons:
            if not muSel.evalMuon(mu): continue
            setattr(mu, 'id', 13)
            event.selectedMuons.append(mu)

        event.selectedMuons.sort(key=lambda x: x.pt, reverse=True)


    def selectAK4Jets(self, event):
        ## Selected jets: pT>30, |eta|<4.7, pass tight ID
        
        event.selectedAK4Jets = []
        ak4jets = Collection(event, "Jet")
        for j in ak4jets:

            if j.pt<30 : 
                continue

            if abs(j.eta) > 4.7:
                continue
            
            #require tight (2^1) or tightLepVeto (2^2) [https://twiki.cern.ch/twiki/bin/view/CMS/JetID#nanoAOD_Flags]
            if j.jetId<2: 
                continue
                
            #check overlap with selected leptons 
            deltaR_to_leptons=[ j.p4().DeltaR(lep.p4()) for lep in event.selectedMuons+event.selectedElectrons ]
            hasLepOverlap=sum( [dR<0.4 for dR in deltaR_to_leptons] )
            if hasLepOverlap>0: continue

            event.selectedAK4Jets.append(j)
            
        event.selectedAK4Jets.sort(key=lambda x: x.pt, reverse=True)

    def selectProtons(self, event, prSel):
        ## access a collection of protons and create a new collection based on this
        
        event.selectedProtonsS = []
        protonsS = Collection(event, "Proton_singleRP")

        for idx, pr in enumerate(protonsS):
            
            #store accepted protons
            setattr(pr, 'method', 0)
            setattr(pr, 't', -1)
            setattr(pr, 'ThX', 999)
            setattr(pr, 'ThY', pr.thetaY)
            setattr(pr, 'rpid', pr.decRPId)
            setattr(pr, 'arm', pr.decRPId // 100)
            if prSel.evalProton(pr): event.selectedProtonsS.append(pr)
        event.selectedProtonsS.sort(key=lambda x: x.xi, reverse=True)

        event.selectedProtonsM = []
        protonsM = Collection(event, "Proton_multiRP")
        for idx, pr in enumerate(protonsM):
            
            #store accepted protons
            setattr(pr, 'method', 1)
            setattr(pr, 'ThX', pr.thetaX)
            setattr(pr, 'ThY', pr.thetaY)
            setattr(pr, 'rpid', -1)
            setattr(pr, 'arm', pr.arm)
            if prSel.evalProton(pr): event.selectedProtonsM.append(pr)        
        event.selectedProtonsM.sort(key=lambda x: x.xi, reverse=True)
		
		# combine SingleRP and MultiRP protons
        event.selectedProtons = event.selectedProtonsS + event.selectedProtonsM

    def selectGenProtons(self, event):
        ## access a collection of generator protons and create a new collection based on this
        
        event.selectedGenProtons = []
		
        if self.isMC:
            genprotons = Collection(event, "GenProton")

            for idx, pr in enumerate(genprotons):
              if pr.isPU: continue
              event.selectedGenProtons.append(pr)

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        
        #initiate proton selector tools:
        prSel = ProtonSelector('2018C')
        elSel = ElectronSelector()
        muSel = MuonSelector(minPt=20, ID='medium')
        
        # apply object selection
        self.selectMuons(event, muSel)
        self.selectElectrons(event, elSel)
        self.selectAK4Jets(event)
        self.selectProtons(event, prSel)
        self.selectGenProtons(event)
        
        #apply event selection depending on the channel:
        if self.channel=="mu":

            # Select events with exactly 2 muons and 0 electrons
            if len(event.selectedElectrons): return False
            if not len(event.selectedMuons)==2: return False
            
            if event.selectedMuons[0].charge==event.selectedMuons[1].charge: return False

        if self.channel=="el":

            # Select events with exactly 2 electrons and 0 muons
            if len(event.selectedMuons): return False
            if not len(event.selectedElectrons)==2: return False
            
            if event.selectedElectrons[0].charge==event.selectedElectrons[1].charge: return False

        if self.channel=='emu':
            nmu=len(event.selectedMuons)
            nele=len(event.selectedElectrons)
            if nmu!=1 or nele!=1 : return False

            if event.selectedMuons[0].charge==event.selectedElectrons[0].charge : return False
       
        ######################################################
        ##### HIGH LEVEL VARIABLES FOR SELECTED EVENTS   #####
        ######################################################
        
        event.selectedLeptons=event.selectedElectrons+event.selectedMuons
        event.selectedLeptons.sort(key=lambda x: x.pt, reverse=True)
        
        lep_id     = [lep.id for lep in event.selectedLeptons]
        lep_pt     = [lep.pt for lep in event.selectedLeptons]
        lep_eta    = [lep.eta for lep in event.selectedLeptons]
        lep_phi    = [lep.phi for lep in event.selectedLeptons]
        lep_charge = [lep.charge for lep in event.selectedLeptons]
        lep_dxy    = [lep.dxy for lep in event.selectedLeptons]
        lep_dz     = [lep.dz for lep in event.selectedLeptons]
        

        #di-lepton 4-vector
        lepSum = ROOT.TLorentzVector()
        for lep in event.selectedLeptons:
            lepSum+=lep.p4()
		
		# compute acolpanarity
        lep1 = event.selectedLeptons[0].p4()
        lep2 = event.selectedLeptons[1].p4()
        acol = 1.0-lep1.DeltaPhi(lep2)/math.pi
	
        #protons
        proton_xi     = [p.xi for p in event.selectedProtons]
        proton_t      = [p.t for p in event.selectedProtons]
        proton_method = [p.method for p in event.selectedProtons]
        proton_ThX    = [p.ThX for p in event.selectedProtons]
        proton_ThY    = [p.ThY for p in event.selectedProtons]
        proton_rpid   = [p.rpid for p in event.selectedProtons]
        proton_arm    = [p.arm for p in event.selectedProtons]
  
        gen_mpp = -1; gen_Ypp = 999;
        if len(event.selectedGenProtons)==2:
            pz1= event.selectedGenProtons[0].pz
            pz2= event.selectedGenProtons[1].pz
            if pz1/pz2<0:
              xi1=1-abs(pz1)/6500.
              xi2=1-abs(pz2)/6500.
              gen_mpp = 13000*math.sqrt(xi1*xi2)
              gen_Ypp = 0.5*math.log(xi1/xi2)
	    
        ## store branches
        self.out.fillBranch("EventNum",           int(abs(lep_eta[0])*800000000))
        self.out.fillBranch("nLepCand",           len(event.selectedLeptons))
        self.out.fillBranch("LepCand_id" ,        lep_id)
        self.out.fillBranch("LepCand_pt" ,        lep_pt)
        self.out.fillBranch("LepCand_eta" ,       lep_eta)
        self.out.fillBranch("LepCand_phi" ,       lep_phi)
        self.out.fillBranch("LepCand_charge",     lep_charge)
        self.out.fillBranch("LepCand_dxy",        lep_dxy)
        self.out.fillBranch("LepCand_dz",         lep_dz)
        self.out.fillBranch("nRecoProtCand",      len(event.selectedProtons))
        self.out.fillBranch("ProtCand_xi",        proton_xi)
        self.out.fillBranch("ProtCand_t",         proton_t)
        self.out.fillBranch("ProtCand_ThX",       proton_ThX)
        self.out.fillBranch("ProtCand_ThY",       proton_ThY)
        self.out.fillBranch("ProtCand_rpid",      proton_rpid)
        self.out.fillBranch("ProtCand_arm",       proton_arm)
        self.out.fillBranch("ProtCand_ismultirp", proton_method)
        self.out.fillBranch("nJets" ,             len(event.selectedAK4Jets))
        self.out.fillBranch("Lep0Pt" ,            lep_pt[0])
        self.out.fillBranch("Lep1Pt" ,            lep_pt[1])
        self.out.fillBranch("Lep0Eta" ,           lep_eta[0])
        self.out.fillBranch("Lep1Eta" ,           lep_eta[1])
        self.out.fillBranch("Lep0Phi" ,           lep_phi[0])
        self.out.fillBranch("Lep1Phi" ,           lep_phi[1])
        self.out.fillBranch("InvMass",            lepSum.M())
        self.out.fillBranch("Yll",                lepSum.Rapidity())
        self.out.fillBranch("pTll",               lepSum.Pt())
        self.out.fillBranch("Acopl",              acol)	
        if self.isMC:
            self.out.fillBranch("gen_mpp",            gen_mpp)
            self.out.fillBranch("gen_Ypp",            gen_Ypp)

        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed
analysis_mumc    = lambda : Analysis(channel="mu", isMC=True)
analysis_elmc    = lambda : Analysis(channel="el", isMC=True)
analysis_emumc   = lambda : Analysis(channel="emu",isMC=True)

analysis_mudata  = lambda : Analysis(channel="mu", isMC=False)
analysis_eldata  = lambda : Analysis(channel="el", isMC=False)
analysis_emudata = lambda : Analysis(channel="emu",isMC=False)
