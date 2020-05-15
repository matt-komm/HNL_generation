import os
import numpy
from width import *

basePath = "/vols/cms/mkomm/HNL/gridpacks/HNL_dirac_muonly"

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
#$ -l h_rt=03:00:00 
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

for ctau in [1e-1,1e0,1e1,1e2,1e3,1e4]:
    for mHNL in [1.,1.5, 2.,3.,4.5,6.,8.,10.,14.,20.]:
        couplings = findCouplings(mHNL,ctau,{'mu':1.0})
        if (couplings['mu']**2)<1e-9:
            continue
        name = ('HNL_dirac_muonly_ctau%.1e_massHNL%.1f_Vmu%.3e'%(ctau,mHNL,couplings['mu'])).replace('.','p')
        print name
        
        cmd = "python create_gridpack.py"
        cmd += " -o "+basePath
        cmd += " --name "+name
        cmd += " --massHNL %.1f"%(mHNL)
        cmd += " --Vmu %.6e"%(couplings['mu'])
        jobCfgs.append({"cmds":[cmd]})

makeSubmitFile(jobCfgs,"HNL_dirac_muonly.sh")



