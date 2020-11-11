import os
import numpy

basePath = "/vols/cms/mkomm/HNL/gridpacks/HNL_testrun_allv3"

def makeSubmitFile(jobArrayCfg,name):
    if len(jobArrayCfg)==0:
        print "No jobs for '"+name+"' -> skip"
        return
        
    try:
        os.makedirs(os.path.join(basePath,'log'))
    except:
        print "Warning: output log dir already exists: "+os.path.join(basePath,'log')
        
        
    submitFile = open(name,"w")
    submitFile.write('''#!/bin/bash
#$ -cwd
#$ -q hep.q
#$ -l h_rt=12:00:00 
#$ -t 1-'''+str(len(jobArrayCfg))+'''
#$ -e '''+os.path.join(basePath,'log')+'''/log.$TASK_ID.err
#$ -o '''+os.path.join(basePath,'log')+'''/log.$TASK_ID.out
hostname
date
source ~/.bashrc
cd /vols/build/cms/mkomm/HNL/HNL_generation
''')

    submitFile.write("JOBS=(\n")
    submitFile.write(" \"pseudo job\"\n")
    for jobCfg in jobArrayCfg:
        submitFile.write(" \"CMDS=(\\\""+jobCfg["cmds"][0]+"\\\"") 
        for cmd in jobCfg["cmds"][1:]:
            submitFile.write(" \\\""+cmd+"\\\"")
        submitFile.write(")\"\n")
    submitFile.write(")\n")

    submitFile.write('''

eval ${JOBS[$SGE_TASK_ID]}
cd $TMPDIR
echo "Working directory: "$PWD
ls -lh
for cmd in "${CMDS[@]}"
    do
    echo "====================================================="
    echo "command: "$cmd
    echo "-----------------------------------------------------"
    $cmd
    echo "====================================================="
    done
date
    ''')
    submitFile.close()
    
jobCfgs = []



def findGridpacks(path):
    packs = []
    for f in os.listdir(path):
        if f.find("ctau1p0e-03")<0 and f.find("ctau1p0e-04")<0 and f.find("ctau1p0e-05")<0:
            continue
        if not f.endswith("tarball.tar.xz"):
            continue
        packs.append(os.path.join(path,f))
    return packs
    
gridpacks = findGridpacks("/vols/cms/mkomm/HNL/gridpacks/HNL_dirac_allv3")
gridpacks += findGridpacks("/vols/cms/mkomm/HNL/gridpacks/HNL_majorana_allv3")

for gridpack in gridpacks:
    gridpackName = gridpack.rsplit('/',1)[1].replace('_tarball.tar.xz','')
    outputPath = os.path.join(basePath,gridpackName)
    try:
        os.makedirs(outputPath)
    except:
        print "Warning: output dir already exists: "+outputPath
        
    jobCfgs.append({"cmds":[
        'tar xf '+gridpack,
        './runcmsgrid.sh 100000 12345 1',
        'python /vols/build/cms/mkomm/HNL/HNL_generation/extractWeights.py --lhe cmsgrid_final.lhe -o '+outputPath+'/weights.hdf5',
        'cp process/madevent/Cards/reweight_card.dat '+outputPath+'/reweight_card.dat',
        'cp process/madevent/Cards/param_card.dat '+outputPath+'/param_card.dat'
    ]})


makeSubmitFile(jobCfgs,"HNL_testrun.sh")



