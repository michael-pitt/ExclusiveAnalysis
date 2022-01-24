def getEraConfiguration(era,isData):
    
    """ defines global tags, depending on the era """

    globalTags = {
        'era2016preVFP':('106X_mcRun2_asymptotic_preVFP_v11',    '106X_dataRun2_v35'),
        'era2016':('106X_mcRun2_asymptotic_v17',                 '106X_dataRun2_v35'),
        'era2017':('auto:phase1_2017_realistic',                 '106X_dataRun2_v35'),
        'era2018':('auto:phase1_2018_realistic',                 '106X_dataRun2_v35')
        }
                    
    globalTag = globalTags[era][isData]

    return globalTag

    