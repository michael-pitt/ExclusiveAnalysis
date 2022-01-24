class ObjectSelector:
    def __init__(self, _year = "None" ):
        self.year = _year


class ProtonSelector(ObjectSelector):
    def __init__(self, _era = "2017H"):
        self.era = _era

                      
    def evalProton(self, proton ):
        
        # skip aperture cuts for now
        return True
        

class ElectronSelector(ObjectSelector):
    def __init__(self, _minPt = 35):
        self.minPt = _minPt

    def evalElectron(self, el):
        
        isEBEE = True if abs(el.eta)>1.4442 and abs(el.eta)<1.5660 else False
        
        if isEBEE: return False
        if el.pt < self.minPt: return False
        if abs(el.eta) > 2.4: return False
        if abs(el.dxy) > 0.05 or abs(el.dz) > 0.2: return False
        if not el.mvaFall17V2Iso_WP80: return False

        return True
        
class MuonSelector(ObjectSelector):
    def __init__(self, minPt = 35, ID = 'tight'):
        self.minPt = minPt
        self.id = ID

    def evalMuon(self, mu):
        if mu.pt < self.minPt: return False
        if abs(mu.eta) > 2.4: return False
        if mu.pfRelIso04_all>0.15: return False
        #if abs(mu.dxybs) > 0.05 or abs(mu.dz) > 1.0: return False
        if abs(mu.dxybs) > 0.05: return False
        if self.id == 'tight' and not mu.tightId: return False
        elif self.id == 'medium' and not mu.mediumId: return False
        elif self.id == 'loose' and not mu.looseId: return False
        return True
        
