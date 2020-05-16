import os
import numpy
from width_mg import *

basePath = "/vols/cms/mkomm/HNL/gridpacks/HNL_dirac_allv2"

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
#$ -q hep.q
#$ -l h_rt=12:00:00 
#$ -t 1-'''+str(len(jobArrayCfg))+'''
#$ -e '''+os.path.join(basePath,'log')+'''/log.$TASK_ID.err
#$ -o '''+os.path.join(basePath,'log')+'''/log.$TASK_ID.out
hostname
date
source ~/.bashrc
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

for ctau in [1e-2,1e-1,1e0,1e1,1e2,1e3,1e4]:
    for mHNL in [1.,1.5, 2.,3.,4.5,6.,8.,10.,12.,16.,20.]:
        couplings = findCouplings(mHNL,ctau,{'e':0.5,'mu':0.5,'tau':0.5})
        if couplings['mu']**2>1 or couplings['mu']**2<5e-9:
            continue
        #print couplings
        name = ('HNL_dirac_all_ctau%.1e_massHNL%.1f_Vall%.3e'%(ctau,mHNL,couplings['mu'])).replace('.','p').replace('+','')
        print name
        
        cmd = "python /vols/build/cms/mkomm/HNL/HNL_generation/create_gridpack.py"
        cmd += " -o "+basePath
        cmd += " --name "+name
        cmd += " --massHNL %.1f"%(mHNL)
        cmd += " --Ve %.6e"%(couplings['e'])
        cmd += " --Vmu %.6e"%(couplings['mu'])
        cmd += " --Vtau %.6e"%(couplings['tau'])
        
        n = 11
        cmd += " --alt %.6e,%.6e,%.6e"%(couplings['e'],couplings['mu'],couplings['tau'])
        for i,l3 in enumerate(numpy.linspace(0,1,n)):
            for l2 in numpy.linspace(0,1-l3,n-i):
                l1 = max(0,1 - l2 - l3)
                altCoupling = findCouplings(mHNL,ctau,{'e':l1,'mu':l2,'tau':l3})
                print '\t fractions=%.3f,%.3f,%.3f => couplings=%.4e,%.4e,%.4e'%(
                    l1,l2,l3,altCoupling['e'],altCoupling['mu'],altCoupling['tau']
                )
                cmd += " --alt %.6e,%.6e,%.6e"%(altCoupling['e'],altCoupling['mu'],altCoupling['tau'])
        jobCfgs.append({"cmds":[cmd]})

makeSubmitFile(jobCfgs,"HNL_dirac_allv2.sh")



