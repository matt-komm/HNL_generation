from CRABClient.UserUtilities import config
import datetime,sys,os
import copy
import math
import urllib, json
#from CRABClient.UserUtilities import getUsernameFromSiteDB, getLumiListInValidFiles

requestName = "miniaod18_200625"
#requestName = "test18"

gridpacks = [
    'HNL_dirac_all_ctau1p0e-01_massHNL10p0_Vall5p262e-03_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e-01_massHNL12p0_Vall3p272e-03_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e-01_massHNL16p0_Vall1p551e-03_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e-01_massHNL1p5_Vall8p442e-01_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e-01_massHNL20p0_Vall8p709e-04_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e-01_massHNL2p0_Vall4p066e-01_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e-01_massHNL3p0_Vall1p388e-01_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e-01_massHNL4p5_Vall4p549e-02_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e-01_massHNL6p0_Vall2p054e-02_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e-01_massHNL8p0_Vall9p475e-03_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e-02_massHNL10p0_Vall1p664e-02_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e-02_massHNL12p0_Vall1p035e-02_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e-02_massHNL16p0_Vall4p905e-03_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e-02_massHNL20p0_Vall2p754e-03_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e-02_massHNL3p0_Vall4p390e-01_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e-02_massHNL4p5_Vall1p438e-01_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e-02_massHNL6p0_Vall6p496e-02_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e-02_massHNL8p0_Vall2p996e-02_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e00_massHNL10p0_Vall1p664e-03_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e00_massHNL12p0_Vall1p035e-03_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e00_massHNL16p0_Vall4p905e-04_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e00_massHNL1p0_Vall7p460e-01_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e00_massHNL1p5_Vall2p670e-01_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e00_massHNL20p0_Vall2p754e-04_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e00_massHNL2p0_Vall1p286e-01_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e00_massHNL3p0_Vall4p390e-02_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e00_massHNL4p5_Vall1p438e-02_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e00_massHNL6p0_Vall6p496e-03_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e00_massHNL8p0_Vall2p996e-03_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e01_massHNL10p0_Vall5p262e-04_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e01_massHNL12p0_Vall3p272e-04_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e01_massHNL16p0_Vall1p551e-04_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e01_massHNL1p0_Vall2p359e-01_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e01_massHNL1p5_Vall8p442e-02_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e01_massHNL20p0_Vall8p709e-05_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e01_massHNL2p0_Vall4p066e-02_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e01_massHNL3p0_Vall1p388e-02_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e01_massHNL4p5_Vall4p549e-03_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e01_massHNL6p0_Vall2p054e-03_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e01_massHNL8p0_Vall9p475e-04_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e02_massHNL10p0_Vall1p664e-04_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e02_massHNL12p0_Vall1p035e-04_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e02_massHNL1p0_Vall7p460e-02_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e02_massHNL1p5_Vall2p670e-02_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e02_massHNL2p0_Vall1p286e-02_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e02_massHNL3p0_Vall4p390e-03_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e02_massHNL4p5_Vall1p438e-03_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e02_massHNL6p0_Vall6p496e-04_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e02_massHNL8p0_Vall2p996e-04_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e03_massHNL1p0_Vall2p359e-02_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e03_massHNL1p5_Vall8p442e-03_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e03_massHNL2p0_Vall4p066e-03_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e03_massHNL3p0_Vall1p388e-03_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e03_massHNL4p5_Vall4p549e-04_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e03_massHNL6p0_Vall2p054e-04_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e03_massHNL8p0_Vall9p475e-05_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e04_massHNL1p0_Vall7p460e-03_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e04_massHNL1p5_Vall2p670e-03_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e04_massHNL2p0_Vall1p286e-03_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e04_massHNL3p0_Vall4p390e-04_tarball.tar.xz',
    'HNL_dirac_all_ctau1p0e04_massHNL4p5_Vall1p438e-04_tarball.tar.xz',
]

'''
gridpacks = [
    'HNL_majorana_all_ctau1p0e-01_massHNL10p0_Vall3p721e-03_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e-01_massHNL12p0_Vall2p314e-03_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e-01_massHNL16p0_Vall1p097e-03_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e-01_massHNL1p5_Vall5p965e-01_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e-01_massHNL20p0_Vall6p165e-04_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e-01_massHNL2p0_Vall2p871e-01_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e-01_massHNL3p0_Vall9p825e-02_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e-01_massHNL4p5_Vall3p213e-02_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e-01_massHNL6p0_Vall1p454e-02_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e-01_massHNL8p0_Vall6p702e-03_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e-02_massHNL10p0_Vall1p177e-02_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e-02_massHNL12p0_Vall7p319e-03_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e-02_massHNL16p0_Vall3p470e-03_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e-02_massHNL20p0_Vall1p950e-03_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e-02_massHNL3p0_Vall3p107e-01_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e-02_massHNL4p5_Vall1p016e-01_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e-02_massHNL6p0_Vall4p597e-02_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e-02_massHNL8p0_Vall2p119e-02_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e00_massHNL10p0_Vall1p177e-03_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e00_massHNL12p0_Vall7p319e-04_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e00_massHNL16p0_Vall3p470e-04_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e00_massHNL1p0_Vall5p274e-01_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e00_massHNL1p5_Vall1p886e-01_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e00_massHNL20p0_Vall1p950e-04_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e00_massHNL2p0_Vall9p078e-02_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e00_massHNL3p0_Vall3p107e-02_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e00_massHNL4p5_Vall1p016e-02_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e00_massHNL6p0_Vall4p597e-03_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e00_massHNL8p0_Vall2p119e-03_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e01_massHNL10p0_Vall3p721e-04_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e01_massHNL12p0_Vall2p314e-04_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e01_massHNL16p0_Vall1p097e-04_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e01_massHNL1p0_Vall1p668e-01_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e01_massHNL1p5_Vall5p965e-02_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e01_massHNL20p0_Vall6p165e-05_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e01_massHNL2p0_Vall2p871e-02_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e01_massHNL3p0_Vall9p825e-03_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e01_massHNL4p5_Vall3p213e-03_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e01_massHNL6p0_Vall1p454e-03_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e01_massHNL8p0_Vall6p702e-04_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e02_massHNL10p0_Vall1p177e-04_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e02_massHNL12p0_Vall7p319e-05_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e02_massHNL1p0_Vall5p274e-02_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e02_massHNL1p5_Vall1p886e-02_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e02_massHNL2p0_Vall9p078e-03_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e02_massHNL3p0_Vall3p107e-03_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e02_massHNL4p5_Vall1p016e-03_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e02_massHNL6p0_Vall4p597e-04_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e02_massHNL8p0_Vall2p119e-04_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e03_massHNL1p0_Vall1p668e-02_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e03_massHNL1p5_Vall5p965e-03_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e03_massHNL2p0_Vall2p871e-03_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e03_massHNL3p0_Vall9p825e-04_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e03_massHNL4p5_Vall3p213e-04_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e03_massHNL6p0_Vall1p454e-04_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e03_massHNL8p0_Vall6p702e-05_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e04_massHNL1p0_Vall5p274e-03_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e04_massHNL1p5_Vall1p886e-03_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e04_massHNL2p0_Vall9p078e-04_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e04_massHNL3p0_Vall3p107e-04_tarball.tar.xz',
    'HNL_majorana_all_ctau1p0e04_massHNL4p5_Vall1p016e-04_tarball.tar.xz',
]
'''

#gridpacks = gridpacks[0:30]
myJobs = {}
for gridpack in gridpacks:
    myJobs[gridpack.replace('+','').replace('_tarball.tar.xz','')] = [
        lambda cfg,gridpack=gridpack: cfg.JobType.pyCfgParams.append('gridpack=root://gfe02.grid.hep.ph.ic.ac.uk//pnfs/hep.ph.ic.ac.uk/data/cms/store/user/mkomm/HNL/gridpacksv3/'+gridpack)
    ]

userName = 'mkomm'#getUsernameFromSiteDB() 
configTmpl = config()

configTmpl.section_('General')
configTmpl.General.transferOutputs = True
configTmpl.General.transferLogs = False

configTmpl.section_('JobType')
configTmpl.JobType.psetName = "lhe2pu_2018.py"
configTmpl.JobType.pluginName = 'PrivateMC'
configTmpl.JobType.outputFiles = []
configTmpl.JobType.allowUndistributedCMSSW = True
configTmpl.JobType.maxJobRuntimeMin= 18*60
configTmpl.JobType.scriptExe = 'LHE2PAT.sh'
configTmpl.JobType.pyCfgParams = []
configTmpl.JobType.inputFiles = ['LHE2PAT.sh']
configTmpl.JobType.maxMemoryMB = 3500
configTmpl.section_('Data')
configTmpl.Data.splitting = 'EventBased'
configTmpl.Data.unitsPerJob = 1000
configTmpl.Data.totalUnits = configTmpl.Data.unitsPerJob*300
configTmpl.Data.publication = True
configTmpl.section_('Site')
configTmpl.Site.storageSite = 'T2_UK_London_IC'
configTmpl.Site.blacklist = ['T2_IT_Pisa','T2_US_Vanderbilt','T2_BR_SPRACE','T2_UK_SGrid_RALPP','T2_ES_IFCA']

if __name__ == '__main__':

    from CRABAPI.RawCommand import crabCommand
    from CRABClient.ClientExceptions import ClientException
    from httplib import HTTPException
    from multiprocessing import Process

    def submit(config):
        try:
            crabCommand('submit',  config = config)
        except HTTPException as hte:
            print "Failed submitting task: %s" % (hte.headers)
        except ClientException as cle:
            print "Failed submitting task: %s" % (cle)


    for i,jobName in enumerate(sorted(myJobs.keys())):

        isData = False
        myJob = myJobs[jobName]
        i=i+1
        config = copy.deepcopy(configTmpl)
        config.General.requestName = jobName+"_"+requestName
        config.General.workArea = "crab/"+requestName+"/"+jobName
        config.Data.outputDatasetTag = requestName
        config.Data.outLFNDirBase = "/store/user/"+userName+"/HNL/"+requestName
        config.Data.outputPrimaryDataset = jobName
        for mod in myJob:
            mod(config)
            
        if not os.path.exists(configTmpl.JobType.psetName):
            print "\nConfiguration file ", pSet, "does not exist.  Aborting..."
            sys.exit(1)

        if os.path.isdir(os.path.join(os.getcwd(),config.General.workArea)):
            print "Output directory ",os.path.join(os.getcwd(),config.General.workArea)," exists -> skipping"
            print
            continue
            
        print config,
            
        print "Submitting job ",i," of ",len(myJobs.keys()),":",config.General.workArea
        
        
        p = Process(target=submit, args=(config,))
        p.start()
        p.join()
        

        print
        print
        
