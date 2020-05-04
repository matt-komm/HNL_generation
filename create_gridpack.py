from string import Template
import os
import subprocess
import shutil
import numpy
from width import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-o','--output', dest='output', type=str, required=True, help='output')
parser.add_argument('--name', dest = 'name', type=str, required=True, help='name')
parser.add_argument('--massHNL', dest='massHNL', type=float, required=True, help='HNL mass')
parser.add_argument('--Ve', dest='Ve', type=float, default = 0.0, help='Ve coupling')
parser.add_argument('--Vmu', dest='Vmu', type=float, default = 0.0, help='Vmu coupling')
parser.add_argument('--Vtau', dest='Vtau', type=float, default = 0.0, help='Vtau coupling')
args = parser.parse_args()


scriptPath = os.path.dirname(__file__)

def check_ascii(text):
    try:
        text.decode('ascii')
    except UnicodeDecodeError:
        return False
    return True

def write_template(outputPath,templatePath,parameters={}):
    f = open(templatePath)
    template = Template(f.read())
    result = template.substitute(parameters)
    if (not check_ascii(result)):
        raise Exception("Template "+templatePath+" resulted in non ascii text")
    o = open(outputPath,"w")
    o.write(result)
    o.close()
    f.close()

def create_gridpack(
    cardName,
    cardOutput,
    gridpackOutput, 
    massHNL,
    couplings, 
    altCouplings = [],
    templateDir = os.path.join(os.path.dirname(__file__),"templates","HNL_dirac"),
):
    if os.path.exists(os.path.join(gridpackOutput,cardName+"_tarball.tar.xz")):
        print "Tarball already exists: "+os.path.join(gridpackOutput,cardName+"_tarball.tar.xz")
        print " -->>> skip"
        return

    try:
        os.makedirs(cardOutput)
    except Exception, e:
        print e
        
    try:
        os.makedirs(gridpackOutput)
    except Exception, e:
        print e
    
    leptons = ""
    Ve = 0.0
    Vmu = 0.0
    Vtau = 0.0
    if couplings.has_key('e') and couplings['e']>1e-12:
        Ve = couplings['e']
        leptons += "e+ e- "
    if couplings.has_key('mu') and couplings['mu']>1e-12:
        Vmu = couplings['mu']
        leptons += "mu+ mu- "
    if couplings.has_key('tau') and couplings['tau']>1e-12:
        Vtau = couplings['tau']
        leptons += "ta+ ta- "
        
    write_template(
        outputPath = os.path.join(cardOutput,cardName+"_proc_card.dat"),
        templatePath = os.path.join(templateDir,"proc_card.dat"),
        parameters = {
            "LEPTONS": leptons,
            "OUTPUT_NAME": cardName  
        }
    )
    write_template(
        outputPath = os.path.join(cardOutput,cardName+"_param_card.dat"),
        templatePath = os.path.join(templateDir,"param_card.dat"),
        parameters = {
            "HNL_MASS": "%.6e"%(massHNL),
            "HNL_VE": "%.6e"%(Ve),
            "HNL_VMU": "%.6e"%(Vmu),
            "HNL_VTAU": "%.6e"%(Vtau),
        }
    )
    
    write_template(
        outputPath = os.path.join(cardOutput,cardName+"_run_card.dat"),
        templatePath = os.path.join(templateDir,"run_card.dat"),
    )
    
    #reweight to alternative couplings
    if len(altCouplings)>0:
        reweightCard = open(os.path.join(cardOutput,cardName+"_reweight_card.dat"),'w')
        reweightCard.write('# default coupling: Ve=%.6e, Vmu=%.6e, Vtau=%.6e\n'%(
            Ve,Vmu,Vtau
        ))
        reweightCard.write('launch\n')
        for i,altCoupling in enumerate(altCouplings):
            altVe = altCoupling['e'] if altCoupling.has_key('e') else 0.0
            altVmu = altCoupling['mu'] if altCoupling.has_key('mu') else 0.0
            altVtau = altCoupling['tau'] if altCoupling.has_key('tau') else 0.0
            
            reweightCard.write('# alt coupling %i: Ve=%.6e, Vmu=%.6e, Vtau=%.6e\n'%(
                i,altVe,altVmu,altVtau
            ))
            reweightCard.write('set numixing 1 %.6e\n'%(altVe))
            reweightCard.write('set numixing 4 %.6e\n'%(altVmu))
            reweightCard.write('set numixing 7 %.6e\n'%(altVtau))
            reweightCard.write('launch\n')
        reweightCard.close()
            
    proc = subprocess.Popen(
        [
            "./gridpack_generation.sh",
            cardName,
            os.path.join('..','..','..',cardOutput),
            "local",
            "ALL",
            "slc7_amd64_gcc630",
            "CMSSW_9_3_16"
        ],
        #stdout = subprocess.STDOUT,
        #stderr = subprocess.STDOUT,
        shell = False,
        cwd = os.path.join(scriptPath,"genproductions","bin","MadGraph5_aMCatNLO"),
        #env = os.environ
    )
    proc.wait()
    
    if proc.returncode!=0:
        raise Exception("Gridpack script failed")
        
    shutil.rmtree(os.path.join(scriptPath,"genproductions","bin","MadGraph5_aMCatNLO",cardName))
    shutil.move(
        os.path.join(scriptPath,"genproductions","bin","MadGraph5_aMCatNLO",cardName+"_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz"),
        os.path.join(gridpackOutput,cardName+"_tarball.tar.xz")
    )
    shutil.move(
        os.path.join(scriptPath,"genproductions","bin","MadGraph5_aMCatNLO",cardName+".log"),
        os.path.join(gridpackOutput,cardName+".log")
    )
    
    
   
create_gridpack(
    cardName = args.name,
    cardOutput = os.path.join(scriptPath,'cards'),
    gridpackOutput = args.output,#"/vols/cms/mkomm/HNL/gridpacks"
    massHNL = args.massHNL,
    couplings = {
        'e': args.Ve,
        'mu': args.Vmu,
        'tau': args.Vtau
    }
)

'''
for ctau in [1e0]:#[1e-1,1e0,1e1,1e2,1e3,1e4]:
    for mHNL in [5.]:#[1.,1.5, 2.,3.,4.5,6.,8.,10.,14.,20.]:
        couplings = findCouplings(mHNL,ctau,{'mu':1.0})
        if (couplings['mu']**2)<1e-10:
            continue
        name = ('HNL_dirac_muonly_ctau%.1e_massHNL%.1f_Vmu%.3e'%(ctau,mHNL,couplings['mu'])).replace('.','p')
        print name
        
        create_gridpack(
            name,
            name,
            massHNL = mHNL,
            couplings = couplings
        )
'''
'''
for ctau in [1e0]:#1e-1,1e0,1e1,1e2,1e3,1e4]:
    for mHNL in [5.]:#1.,1.5, 2.,3.,4.5,6.,8.,10.,14.,20.]:
        couplings = findCouplings(mHNL,ctau,{'e':0.5,'mu':0.5,'tau':0.5})
        altCouplings = []
        #use barycentric coordinates
        for x in numpy.linspace(0,1,10):
            for y in numpy.linspace(0,1,10):
                l3 = 1.-l1-l2
                altVe = l1*1.0+
                altVmu = 
        
        name = ('HNL_dirac_muonly_ctau%.1e_massHNL%.1f_Vmu%.3e'%(ctau,mHNL,couplings['mu'])).replace('.','p')
        print name
        
        create_gridpack(
            name,
            name,
            massHNL = mHNL,
            couplings = couplings
        )
'''

