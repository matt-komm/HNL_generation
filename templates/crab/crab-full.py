from WMCore.Configuration import Configuration
import datetime,sys,os
import copy
import math
import urllib, json
from CRABClient.UserUtilities import getUsernameFromSiteDB, getLumiListInValidFiles

requestName = "miniaod16v3_200512"


gridpacks = [
    "HNL_dirac_all_ctau1p0e+00_massHNL10p0_Vall1p675e-03_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+00_massHNL14p0_Vall7p016e-04_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+00_massHNL1p0_Vall7p461e-01_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+00_massHNL1p5_Vall2p666e-01_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+00_massHNL20p0_Vall2p831e-04_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+00_massHNL2p0_Vall1p292e-01_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+00_massHNL3p0_Vall4p692e-02_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+00_massHNL4p5_Vall1p472e-02_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+00_massHNL6p0_Vall6p573e-03_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+00_massHNL8p0_Vall3p018e-03_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e-01_massHNL10p0_Vall5p295e-03_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+01_massHNL10p0_Vall5p295e-04_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e-01_massHNL14p0_Vall2p219e-03_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+01_massHNL14p0_Vall2p219e-04_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+01_massHNL1p0_Vall2p359e-01_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e-01_massHNL1p5_Vall8p431e-01_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+01_massHNL1p5_Vall8p431e-02_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e-01_massHNL20p0_Vall8p952e-04_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+01_massHNL20p0_Vall8p952e-05_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e-01_massHNL2p0_Vall4p085e-01_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+01_massHNL2p0_Vall4p085e-02_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e-01_massHNL3p0_Vall1p484e-01_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+01_massHNL3p0_Vall1p484e-02_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e-01_massHNL4p5_Vall4p656e-02_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+01_massHNL4p5_Vall4p656e-03_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e-01_massHNL6p0_Vall2p079e-02_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+01_massHNL6p0_Vall2p079e-03_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e-01_massHNL8p0_Vall9p544e-03_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+01_massHNL8p0_Vall9p544e-04_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e-02_massHNL10p0_Vall1p675e-02_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+02_massHNL10p0_Vall1p675e-04_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e-02_massHNL14p0_Vall7p016e-03_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+02_massHNL14p0_Vall7p016e-05_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+02_massHNL1p0_Vall7p461e-02_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+02_massHNL1p5_Vall2p666e-02_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e-02_massHNL20p0_Vall2p831e-03_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e-02_massHNL2p0_Vall1p292e+00_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+02_massHNL2p0_Vall1p292e-02_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e-02_massHNL3p0_Vall4p692e-01_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+02_massHNL3p0_Vall4p692e-03_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e-02_massHNL4p5_Vall1p472e-01_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+02_massHNL4p5_Vall1p472e-03_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e-02_massHNL6p0_Vall6p573e-02_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+02_massHNL6p0_Vall6p573e-04_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e-02_massHNL8p0_Vall3p018e-02_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+02_massHNL8p0_Vall3p018e-04_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+03_massHNL10p0_Vall5p295e-05_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+03_massHNL1p0_Vall2p359e-02_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+03_massHNL1p5_Vall8p431e-03_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+03_massHNL2p0_Vall4p085e-03_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+03_massHNL3p0_Vall1p484e-03_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+03_massHNL4p5_Vall4p656e-04_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+03_massHNL6p0_Vall2p079e-04_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+03_massHNL8p0_Vall9p544e-05_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+04_massHNL1p0_Vall7p461e-03_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+04_massHNL1p5_Vall2p666e-03_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+04_massHNL2p0_Vall1p292e-03_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+04_massHNL3p0_Vall4p692e-04_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+04_massHNL4p5_Vall1p472e-04_tarball.tar.xz",
    "HNL_dirac_all_ctau1p0e+04_massHNL6p0_Vall6p573e-05_tarball.tar.xz",
]


#gridpacks = ["HNL_dirac_all_ctau1p0e+03_massHNL2p0_Vall4p085e-03_tarball.tar.xz"]

myJobs = {}
for gridpack in gridpacks:
    myJobs[gridpack.replace('+','').replace('_tarball.tar.xz','')] = [
        lambda cfg,gridpack=gridpack: cfg.JobType.pyCfgParams.append('gridpack=root://gfe02.grid.hep.ph.ic.ac.uk//pnfs/hep.ph.ic.ac.uk/data/cms/store/user/mkomm/HNL/gridpacks/HNL_dirac_all/'+gridpack)
    ]

userName = 'mkomm'#getUsernameFromSiteDB() 
configTmpl = Configuration()

configTmpl.section_('General')
configTmpl.General.transferOutputs = True
configTmpl.General.transferLogs = False

configTmpl.section_('JobType')
configTmpl.JobType.psetName = "lhe2pu_2016.py"
configTmpl.JobType.pluginName = 'PrivateMC'
configTmpl.JobType.outputFiles = []
configTmpl.JobType.allowUndistributedCMSSW = True
configTmpl.JobType.maxJobRuntimeMin= 16*60
configTmpl.JobType.scriptExe = 'LHE2PAT.sh'
configTmpl.JobType.pyCfgParams = []
configTmpl.JobType.inputFiles = ['LHE2PAT.sh']
configTmpl.JobType.maxMemoryMB = 3000
configTmpl.section_('Data')
configTmpl.Data.splitting = 'EventBased'
configTmpl.Data.unitsPerJob = 1000
configTmpl.Data.totalUnits = configTmpl.Data.unitsPerJob*250
configTmpl.Data.publication = True
configTmpl.section_('Site')
configTmpl.Site.storageSite = 'T2_UK_London_IC'

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
        
