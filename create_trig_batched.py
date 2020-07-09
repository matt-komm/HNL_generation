import os
import numpy
from width_mg import *

basePath = "/vols/cms/mkomm/HNL/gridpacks/HNL_majorana_allv3"

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

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptFit(0)
ROOT.gStyle.SetOptDate(0)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFile(0)
ROOT.gStyle.SetOptTitle(0)

ROOT.gStyle.SetLabelFont(43,"XYZ")
ROOT.gStyle.SetLabelSize(28,"XYZ")
ROOT.gStyle.SetTitleFont(43,"XYZ")
ROOT.gStyle.SetTitleSize(31,"XYZ")

cv = ROOT.TCanvas("cv","",800,750)
cv.SetLeftMargin(0.14)
cv.SetRightMargin(0.04)
cv.SetBottomMargin(0.12)
cv.SetTopMargin(0.08)
cv.Range(0,0,1,1)
cv.RangeAxis(0,0,1,1)

def applyAxisStyle(axis):
    axis.SetLabelFont(43)
    axis.SetLabelSize(29)
    axis.SetTitleFont(43)
    axis.SetTitleSize(33)
    axis.CenterTitle(True)
    
def getX(ve,vmu,vtau):
    x = 0*ve+1*vmu+0.5*vtau
    x*=0.8
    x+=0.1
    return x
    
def getY(ve,vmu,vtau):
    y = 0*ve+0*vmu+1*vtau
    y*=0.75
    y+=0.15
    return y

axis1 = ROOT.TGaxis(
    getX(0,1,0),getY(0,1,0),
    getX(1,0,0),getY(1,0,0),
    0.0,1,
    512,"+U"
)
applyAxisStyle(axis1)
axis1.SetTickSize(0.025)
axis1.Draw()

axis1L = ROOT.TGaxis(
    
    getX(0,1,0),getY(0,1,0),
    getX(1,0,0),getY(1,0,0),
    0.0,1,
    512,"-S"
)
applyAxisStyle(axis1L)
axis1L.SetTickSize(0.0)
axis1L.SetLabelOffset(0.0)
axis1L.SetTitleOffset(1.7)
axis1L.SetTitle("f#lower[0.3]{#scale[0.8]{e#mu}}")##times|V#lower[0.3]{#scale[0.8]{e}}|#lower[-0.7]{#scale[0.8]{2}}+(1-f#lower[0.3]{#scale[0.8]{e#mu}})#times|V#lower[0.3]{#scale[0.8]{#mu}}|#lower[-0.7]{#scale[0.8]{2}}")
axis1L.SetLabelOffset(0.04)
axis1L.Draw()


axis2 = ROOT.TGaxis(
    
    getX(0,0,1),getY(0,0,1),
    getX(0,1,0),getY(0,1,0),
    0.0,1,
    512,"+U"
)
applyAxisStyle(axis2)
axis2.SetTickSize(0.025)
axis2.Draw()

axis2L = ROOT.TGaxis(
    
    getX(0,0,1),getY(0,0,1),
    getX(0,1,0),getY(0,1,0),
    0.0,1,
    512,"+S="
)
applyAxisStyle(axis2L)
axis2L.SetTickSize(0.0)
axis2L.SetTitleOffset(1.75)
axis2L.SetLabelOffset(0.07)
axis2L.SetTitle("f#lower[0.3]{#scale[0.8]{#mu#tau}}")##times|V#lower[0.3]{#scale[0.8]{#mu}}|#lower[-0.7]{#scale[0.8]{2}}+(1-f#lower[0.3]{#scale[0.8]{#mu#tau}})#times|V#lower[0.3]{#scale[0.8]{#tau}}|#lower[-0.7]{#scale[0.8]{2}}")
axis2L.Draw()



axis3 = ROOT.TGaxis(
    getX(1,0,0),getY(1,0,0),
    getX(0,0,1),getY(0,0,1),
    0.0,1,
    512,"+U"
)
applyAxisStyle(axis3)
axis3.SetTickSize(0.025)
axis3.Draw()

axis3L = ROOT.TGaxis(
    getX(1,0,0),getY(1,0,0),
    getX(0,0,1),getY(0,0,1),
    0.0,1,
    512,"+S="
)
applyAxisStyle(axis3L)
axis3L.SetTickSize(0.0)
axis3L.SetTitleOffset(1.75)
axis3L.SetLabelOffset(0.07)
axis3L.SetTitle("f#lower[0.3]{#scale[0.8]{e#tau}}")##times|V#lower[0.3]{#scale[0.8]{e}}|#lower[-0.7]{#scale[0.8]{2}}+(1-f#lower[0.3]{#scale[0.8]{e#tau}})#times|V#lower[0.3]{#scale[0.8]{#tau}}|#lower[-0.7]{#scale[0.8]{2}}")
axis3L.Draw()

rootObj = []

for v in numpy.linspace(0,1,11):
    
    l1 = ROOT.TLine(
        getX(1,0,v),getY(1,0,v),
        getX(0,1-v,v),getY(0,1-v,v)
    )
    rootObj.append(l1)
    l1.SetLineColor(ROOT.kGray+1)
    l1.SetLineStyle(2)
    l1.Draw("Same")
    
    l2 = ROOT.TLine(
        getX(v,1-v,0),getY(v,1-v,0),
        getX(v,1-v,v),getY(v,1-v,v)
    )
    rootObj.append(l2)
    l2.SetLineColor(ROOT.kGray+1)
    l2.SetLineStyle(2)
    l2.Draw("Same")
    
    l3 = ROOT.TLine(
        getX(v,1-v,0),getY(v,1-v,0),
        getX(v,0,1-v),getY(v,0,1-v)
    )
    rootObj.append(l3)
    l3.SetLineColor(ROOT.kGray+1)
    l3.SetLineStyle(2)
    l3.Draw("Same")
    
    

for ctau in [1e-0]:#,1e-1,1e0,1e1,1e2,1e3,1e4]:
    for mHNL in [1.]:#,1.5, 2.,3.,4.5,6.,8.,10.,12.,16.,20.]:
        couplings = findCouplingsMajorana(mHNL,ctau,{'e':0.5,'mu':0.5,'tau':0.5})
        
        #use this to generate same ctau/mass points for dirac and majorana
        couplingsCheck = findCouplingsDirac(mHNL,ctau,{'e':0.5,'mu':0.5,'tau':0.5})
        if couplingsCheck['mu']**2>1 or couplingsCheck['mu']**2<5e-9:
            continue
        #print couplings
        name = ('HNL_majorana_all_ctau%.1e_massHNL%.1f_Vall%.3e'%(ctau,mHNL,couplings['mu'])).replace('.','p').replace('+','')
        print name
        
        cmd = "python /vols/build/cms/mkomm/HNL/HNL_generation/create_gridpack.py"
        cmd += " -o "+basePath
        cmd += " --name "+name
        cmd += " --majorana "
        cmd += " --massHNL %.1f"%(mHNL)
        cmd += " --Ve %.6e"%(couplings['e'])
        cmd += " --Vmu %.6e"%(couplings['mu'])
        cmd += " --Vtau %.6e"%(couplings['tau'])
        
        n = 11
        cmd += " --alt %.6e,%.6e,%.6e"%(couplings['e'],couplings['mu'],couplings['tau'])
        index=2
        for i,l3 in enumerate(numpy.linspace(0,1,n)):
            for l2 in numpy.linspace(0,1-l3,n-i):
                l1 = max(0,1 - l2 - l3)
                altCoupling = findCouplingsMajorana(mHNL,ctau,{'e':l1,'mu':l2,'tau':l3})
                print '\t %02i fractions=%.3f,%.3f,%.3f => couplings=%.4e,%.4e,%.4e'%(
                    index,l1,l2,l3,altCoupling['e'],altCoupling['mu'],altCoupling['tau']
                )
                index+=1
                cmd += " --alt %.6e,%.6e,%.6e"%(altCoupling['e'],altCoupling['mu'],altCoupling['tau'])
                
                m = ROOT.TMarker(getX(l1,l2,l3),getY(l1,l2,l3),20)
                rootObj.append(m)
                m.SetMarkerSize(1.6)
                m.Draw("Same")
        jobCfgs.append({"cmds":[cmd]})

#cv.Print('trig.pdf')
#makeSubmitFile(jobCfgs,"HNL_majorana_allv3.sh")



