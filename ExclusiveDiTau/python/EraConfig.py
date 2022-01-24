import os
""" Year dependent configurations / files """

ANALYSISTRIGGER = {
    '2017': {'mu':'HLT_IsoMu24','el':'HLT_Ele32_WPTight_Gsf'},
    '2018': {'mu':'HLT_IsoMu27','el':'HLT_Ele35_WPTight_Gsf'}
}

ANALYSISCHANNELCUT = {
    'mu':'nMuon>1',
	'el':'nElectron>1'
}

ANALYSISGRL = {
    #'2017': 'combined_RPIN_CMS.json', # /eos/project/c/ctpps/Operations/DataExternalConditions/2017/combined_RPIN_CMS.json
    '2017': 'combined_multiRPIN_CMS.json', # /eos/cms/store/group/phys_top/TTbarCentralExclProd/Code/combined_multiRPIN_CMS.json
    '2018': 'CMSgolden_2RPGood_anyarms.json' # /eos/project/c/ctpps/Operations/DataExternalConditions/2018/CMSgolden_2RPGood_anyarms.json
}

cmssw=os.environ['CMSSW_BASE']
ANALYSISCUT={'': {'mu' : '-c "%s"'%ANALYSISCHANNELCUT['mu'], 'el' : '-c "%s"'%ANALYSISCHANNELCUT['el']}}
for y in ANALYSISTRIGGER:
  ANALYSISCUT[y]={}
  for c in ANALYSISTRIGGER[y]:
    ANALYSISCUT[y][c]='--cut %s&&%s --json %s'%(ANALYSISTRIGGER[y][c],ANALYSISCHANNELCUT[c],cmssw+'/src/CMSDASTools/Analysis/data/'+ANALYSISGRL[y])
