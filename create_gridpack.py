from string import Template
import os
import subprocess
import shutil
import numpy
#from width_mg import *
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-o','--output', dest='output', type=str, required=True, help='output')
parser.add_argument('--name', dest = 'name', type=str, required=True, help='name')
parser.add_argument('--massHNL', dest='massHNL', type=float, required=True, help='HNL mass')
parser.add_argument('--Ve', dest='Ve', type=float, default = 0.0, help='Ve coupling')
parser.add_argument('--Vmu', dest='Vmu', type=float, default = 0.0, help='Vmu coupling')
parser.add_argument('--Vtau', dest='Vtau', type=float, default = 0.0, help='Vtau coupling')
parser.add_argument('--alt', dest='alt', default=[], action='append',help="Alternative coupling in format: Ve,Vmu,Vtau")
parser.add_argument('--dirac', dest='dirac', default=False, action='store_true', help="")
parser.add_argument('--majorana', dest='majorana', default=False, action='store_true', help="")
parser.add_argument('--branch', dest='branch', default='localx', help="genproduction branch to checkout")
args = parser.parse_args()


print "nominal coupling: Ve=%.6e, Vmu=%.6e, Vtau=%.6e"%(args.Ve,args.Vmu,args.Vtau)
altCouplings = []
for altCoupling in map(lambda x: map(float,x.split(',')),args.alt):
    print "adding alternative coupling: Ve=%.6e, Vmu=%.6e, Vtau=%.6e"%(
        altCoupling[0],
        altCoupling[1],
        altCoupling[2]
    ) 
    if altCoupling[0]>0. and args.Ve<1e-12:
        raise Exception("Nominal Ve coupling ("+str(args.Ve)+") too small to perform reweighting reliably")
    if altCoupling[1]>0. and args.Vmu<1e-12:
        raise Exception("Nominal Vmu coupling ("+str(args.Vmu)+") too small to perform reweighting reliably")
    if altCoupling[2]>0. and args.Vtau<1e-12:
        raise Exception("Nominal Vtau coupling ("+str(args.Vtau)+") too small to perform reweighting reliably")

    altCouplings.append({
        'e':altCoupling[0],
        'mu':altCoupling[1],
        'tau':altCoupling[2]
    })
    

#sys.exit(1)

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
    gridpackOutput, 
    massHNL,
    couplings, 
    altCouplings = [],
    templateDir = os.path.join(os.path.dirname(__file__),"templates","HNL_dirac"),
    cwdDir = os.getcwd(),
    hnlParticles = "n1 n1~",
    branch = 'localx'
):
    if os.path.exists(os.path.join(gridpackOutput,cardName+"_tarball.tar.xz")):
        print "Tarball already exists: "+os.path.join(gridpackOutput,cardName+"_tarball.tar.xz")
        print " -->>> skip"
        return
        
    try:
        os.makedirs(gridpackOutput)
    except Exception, e:
        pass
        
    
    proc = subprocess.Popen([
        'git',
        'clone',
        '-b',
        branch,
        '--depth',
        '1',
        '-n',
        'https://github.com/matt-komm/genproductions.git',
    ],
        shell = False,
        cwd = cwdDir
    )
    proc.wait()
    if proc.returncode!=0:
        raise Exception("Cloning genproductions failed")
        
    proc = subprocess.Popen(
        ['git','config','core.sparsecheckout','true'],
        cwd = os.path.join(cwdDir,'genproductions'),
        shell = False,
    )
    proc.wait()
    if proc.returncode!=0:
        raise Exception("Configure git for sparse checkout failed")
        
    fsparseCfg = open(os.path.join(cwdDir,'genproductions','.git','info','sparse-checkout'),'w')
    fsparseCfg.write('bin/MadGraph5_aMCatNLO\n')
    fsparseCfg.write('MetaData\n')
    fsparseCfg.write('Utilities\n')
    fsparseCfg.close()
        
    proc = subprocess.Popen(
        ['git','read-tree','-vmu','HEAD'],
        cwd = os.path.join(cwdDir,'genproductions'),
        shell = False,
    )
    proc.wait()
    if proc.returncode!=0:
        raise Exception("Running sparse checkout failed")
        
    cardDir = cardName+'_cards'
    cardOutput = os.path.join(cwdDir,'genproductions','bin','MadGraph5_aMCatNLO',cardDir)

    try:
        os.makedirs(cardOutput)
    except Exception, e:
        print e
        
    
    leptons = ""
    neutrinos = ""
    Ve = 0.0
    Vmu = 0.0
    Vtau = 0.0
    if couplings.has_key('e') and couplings['e']>1e-12:
        Ve = couplings['e']
        leptons += "e+ e- "
        neutrinos += "ve ve~ "
    if couplings.has_key('mu') and couplings['mu']>1e-12:
        Vmu = couplings['mu']
        leptons += "mu+ mu- "
        neutrinos += "vm vm~ "
    if couplings.has_key('tau') and couplings['tau']>1e-12:
        Vtau = couplings['tau']
        leptons += "ta+ ta- "
        neutrinos += "vt vt~ "
        

    write_template(
        outputPath = os.path.join(cardOutput,cardName+"_proc_card.dat"),
        templatePath = os.path.join(templateDir,"proc_card.dat"),
        parameters = {
            "LEPTONS": leptons,
            "NEUTRINOS": neutrinos,
            "HNL": hnlParticles,
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
    
    write_template(
        outputPath = os.path.join(cardOutput,cardName+"_extramodels.dat"),
        templatePath = os.path.join(templateDir,"extramodels.dat"),
    )
    
    #reweight to alternative couplings
    if len(altCouplings)>0:
        reweightCard = open(os.path.join(cardOutput,cardName+"_reweight_card.dat"),'w')
        reweightCard.write('# default coupling: Ve=%.6e, Vmu=%.6e, Vtau=%.6e\n'%(
            Ve,Vmu,Vtau
        ))
        reweightCard.write('change rwgt_dir ./rwgt\n')
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
    ''' 
    #remove potential exiting working folder from previous failed run
    if os.path.exists(os.path.join(scriptPath,"genproductions","bin","MadGraph5_aMCatNLO",cardName)):
        shutil.rmtree(os.path.join(scriptPath,"genproductions","bin","MadGraph5_aMCatNLO",cardName))
    if os.path.exists(os.path.join(scriptPath,"genproductions","bin","MadGraph5_aMCatNLO",cardName+".log")):
        shutil.rmtree(os.path.join(scriptPath,"genproductions","bin","MadGraph5_aMCatNLO",cardName+".log"))
    '''
    
    proc = subprocess.Popen(
        [
            "./gridpack_generation.sh",
            cardName,
            cardDir,
            "local",
            "ALL",
            "slc7_amd64_gcc630",
            "CMSSW_9_3_16"
        ],
        #stdout = subprocess.STDOUT,
        #stderr = subprocess.STDOUT,
        shell = False,
        cwd = os.path.join(cwdDir,"genproductions","bin","MadGraph5_aMCatNLO"),
        #env = os.environ
    )
    proc.wait()
    
    if proc.returncode!=0:
        raise Exception("Gridpack script failed")
        
    shutil.move(
        os.path.join(cwdDir,"genproductions","bin","MadGraph5_aMCatNLO",cardName+"_slc7_amd64_gcc630_CMSSW_9_3_16_tarball.tar.xz"),
        os.path.join(gridpackOutput,cardName+"_tarball.tar.xz")
    )
    shutil.move(
        os.path.join(cwdDir,"genproductions","bin","MadGraph5_aMCatNLO",cardName+".log"),
        os.path.join(gridpackOutput,cardName+".log")
    )
    #shutil.rmtree(os.path.join(cwdDir,"genproductions","bin","MadGraph5_aMCatNLO",cardName))

   
   
if args.dirac:
    create_gridpack(
        cardName = args.name,
        gridpackOutput = args.output,
        massHNL = args.massHNL,
        couplings = {
            'e': args.Ve,
            'mu': args.Vmu,
            'tau': args.Vtau
        },
        altCouplings = altCouplings,
        templateDir = os.path.join(os.path.dirname(__file__),"templates","HNL_dirac"),
        hnlParticles = 'n1 n1~',
        branch = args.branch
    )
    
elif args.majorana:
    create_gridpack(
        cardName = args.name,
        gridpackOutput = args.output,
        massHNL = args.massHNL,
        couplings = {
            'e': args.Ve,
            'mu': args.Vmu,
            'tau': args.Vtau
        },
        altCouplings = altCouplings,
        templateDir = os.path.join(os.path.dirname(__file__),"templates","HNL_majorana"),
        hnlParticles = 'n1',
        branch = args.branch
    )


