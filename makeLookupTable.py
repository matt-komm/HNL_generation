import os
import h5py
import json
import re
import numpy
import barycentricCoordinates

basepath = "/vols/cms/mkomm/HNL/gridpacks/HNL_testrun_allv3"

hbar = 6.58211915e-25 # hbar in GeV s
c = 299792458000.0 # speed of light in mm/s


def readParamCard(paramCard):
    mass = None
    width = None
    with open(paramCard) as f:
        readMass = False
        for l in f:
            matchBlock = re.match("^BLOCK\\s+(\\S+)",l)
            if matchBlock:
                readMass = matchBlock.group(1)=="MASS"
            if readMass:
                matchMass = re.match("^\\s*(99[0-9]+012)\\s+([0-9]*\\.[0-9]*[eE][+-][0-9]+)",l)
                if matchMass:
                    pdgid = int(matchMass.group(1))
                    if pdgid==9990012 or pdgid==9900012:
                        mass = float(matchMass.group(2))
            matchWidth = re.match("^DECAY\\s*(99[0-9]+012)\\s+([0-9]*\\.[0-9]*[eE][+-][0-9]+)",l)
            if matchWidth:
                pdgid = int(matchWidth.group(1))
                if pdgid==9990012 or pdgid==9900012:
                    width = float(matchWidth.group(2))
                    
    return mass,width
                
    
def readReweightCard(reweightCard):
    couplings = []
    with open(reweightCard) as f:
        Ve = -1
        Vmu = -1
        Vtau = -1
        for l in f:
            if l.startswith("launch"):
                if Ve>=0 and Vmu>=0 and Vtau>=0:
                    couplings.append({
                        "Ve":Ve,
                        "Vmu":Vmu,
                        "Vtau":Vtau
                    })
                Ve = -1
                Vmu = -1
                Vtau = -1
            else:
                matchMod = re.match("set\\s+numixing\\s+([0-9]+)\\s+([0-9]*\\.[0-9]*[eE][+-][0-9]+)",l)
                if matchMod:
                    couplingId = int(matchMod.group(1))
                    couplingValue = float(matchMod.group(2))
                    if couplingId==1:
                        Ve = couplingValue
                    elif couplingId==4:
                        Vmu = couplingValue
                    elif couplingId==7:
                        Vtau = couplingValue
    return couplings
    
def readWeights(weights):
    xsecs = []
    with h5py.File(weights,'r') as f:
        weightNames = sorted(filter(lambda x: x.startswith("rwgt"),f.keys()), key=lambda x: int(x.rsplit('_',1)[1]))
        scaleUp = f['1021'][()]/f['1001'][()] #<weight id="1021" MUR="2.0" MUF="2.0" PDF="325300" > MUR=2.0 MUF=2.0  </weight>
        scaleDown = f['1041'][()]/f['1001'][()] # <weight id="1041" MUR="0.5" MUF="0.5" PDF="325300" > MUR=0.5 MUF=0.5  </weight>
        for weightName in weightNames:
            weights = f[weightName][()]
            weightsUp = weights*scaleUp
            weightsDown = weights*scaleDown
            
            xsec = sum(weights)
            xsecUp = sum(weightsUp)
            xsecDown = sum(weightsDown)
            
            xsecs.append({
                "nominal":xsec,
                "up":xsecUp,
                "down":xsecDown
            })
    return xsecs
                    
outputDict = {}
                
for f in os.listdir(basepath):
    outputDict[f] = {}
    
    paramCard = os.path.join(basepath,f,"param_card.dat")
    reweightCard = os.path.join(basepath,f,"reweight_card.dat")
    weights = os.path.join(basepath,f,"weights.hdf5")
    if not os.path.exists(paramCard):
        print "param_card file not found in ",f," -> skip"
        continue
    if not os.path.exists(reweightCard):
        print "reweight_card file not found in ",f," -> skip"
        continue
    if not os.path.exists(weights):
        print "Weight file not found in ",f," -> skip"
        continue
    
    print "processing ... ",f
    
    mass,width = readParamCard(paramCard)
    outputDict[f]['mass'] = mass
    outputDict[f]['width'] = width
    outputDict[f]['ctau'] = hbar*c/width
    
    
    couplings = readReweightCard(reweightCard)
    xsecs = readWeights(weights)
    
    outputDict[f]['weights'] = {}
    outputDict[f]['weights'][1] = {
        "barycentric": {
            "Ve":1./3,
            "Vmu":1./3,
            "Vtau":1./3
        },
        "couplings":couplings[0],
        "xsec": xsecs[0]
    }
    
    for i,l1,l2,l3 in barycentricCoordinates.generate(11):
        outputDict[f]['weights'][i+2] = {
            "barycentric": {
                "Ve":l1,
                "Vmu":l2,
                "Vtau":l3
            },
            "couplings":couplings[i+1],
            "xsec": xsecs[i+1]
        }


with open("lookupTable.json","w") as f:
    json.dump(
        outputDict,
        f,
        ensure_ascii=True, 
        check_circular=True, 
        allow_nan=True, 
        cls=None, 
        indent=4, 
        sort_keys=True, 
    )
    
    
