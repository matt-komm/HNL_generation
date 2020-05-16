import scipy
import scipy.integrate
import scipy.optimize
import math
import numpy
import os
import re
import ROOT

scriptPath = os.path.dirname(__file__)

hbar = 6.58211915e-25 # hbar in GeV s
c = 299792458000.0 # speed of light in mm/s

def getPartialWidthsFromParamCard(card,massHNL):
    f = open(card)
    parseDecay = False    
    parseMass = False
    parseCouplings = False
    partialWidths = []
    hnlMass = -1
    for l in f:
        if l.startswith('#'):
            continue
        if l.startswith('BLOCK'):
            if l.find('MASS')>=0:
                parseMass = True
            else:
                parseMass = False
                
            if l.find('NUMIXING')>=0:
                parseCouplings = True
            else:
                parseCouplings = False
                
        if l.startswith('DECAY'):
            parseMass = False
            parseCouplings = False
            
                
        mMass = re.match("\\s*9990012\\s+([0-9]*\\.[0-9]*[eE][+-][0-9]+)\\s+#\\s+mn1",l)
        if mMass and parseMass:
            hnlMass = float(mMass.groups()[0])
            if math.fabs(hnlMass/massHNL-1)>0.1:
                raise Exception("HNL mass do not match in file "+card)

        
        mVe = re.match("\\s*1\\s+([0-9]*\\.[0-9]*[eE][+-][0-9]+)\\s+#\\s+ven1",l)
        if mVe and parseCouplings:
            if math.fabs(float(mVe.groups()[0])/0.1-1)>0.0001:
                raise Exception("HNL coupling Ve does not match in file "+card)
            
        mVmu = re.match("\\s*4\\s+([0-9]*\\.[0-9]*[eE][+-][0-9]+)\\s+#\\s+vmun1",l)
        if mVmu and parseCouplings:
            if math.fabs(float(mVmu.groups()[0])/0.1-1)>0.0001:
                raise Exception("HNL coupling Vmu does not match in file "+card)
                
        mVtau = re.match("\\s*7\\s+([0-9]*\\.[0-9]*[eE][+-][0-9]+)\\s+#\\s+vtan1",l)
        if mVtau and parseCouplings:
            if math.fabs(float(mVtau.groups()[0])/0.1-1)>0.0001:
                raise Exception("HNL coupling Vtau does not match in file "+card)           
            
        mWidth = re.match('DECAY\\s+9990012\\s+([0-9]*\\.[0-9]*[eE][+-][0-9]+)',l)
        if mWidth:
            totalWidth = float(mWidth.groups()[0])
            parseDecay = True
        elif l.startswith('DECAY') and parseDecay:
            parseDecay = False
        if parseDecay:
            mDecay = re.match(
                "\\s*([0-9]*\\.[0-9]*[eE][+-][0-9]+)\\s+[0-9]+\\s+(-*[0-9]+)\\s+(-*[0-9]+)\\s+(-*[0-9]+)\\s+#\\s+([0-9]*\\.[0-9]*[eE][+-][0-9]+)",
                l
            )
            if mDecay:
                ids = sorted([
                    abs(int(mDecay.groups()[1])),
                    abs(int(mDecay.groups()[2])),
                    abs(int(mDecay.groups()[3])),
                ])
                partialWidth = float(mDecay.groups()[4])
                partialWidths.append({
                    'ids':ids,
                    'width':partialWidth
                })
                
    if hnlMass<0:
        raise Exception("HNL mass not found in file "+card)
                
    return partialWidths
                       
                   

def widthTotal(massHNL,couplings,verbose = False):
    partialWidths = getPartialWidthsFromParamCard(
        os.path.join(scriptPath,'templates','params0p1','param_card_massHNL%.1f.dat'%(massHNL)),
        massHNL
    )
    

    widthPerFlavor = {11: 0.0, 13: 0.0, 15: 0.0}
    
    processed = 0
    
    for i,partialWidth in enumerate(partialWidths):
        if verbose:
            print i,processed,partialWidth,
        for lflavor in [11,13,15]:
            for lflavor2 in [11,13,15]:
                #L LNU (note: if lflavor==lflavor2 then NC possible)
                if lflavor!=lflavor2 and partialWidth['ids'] == sorted([lflavor,lflavor2,lflavor2+1]):
                    widthPerFlavor[lflavor] += partialWidth['width']
                    if verbose:
                        print 'lnu',lflavor,
                    processed+=1
                
                #NU LL
                if partialWidth['ids'] == sorted([lflavor+1,lflavor2,lflavor2]):
                    widthPerFlavor[lflavor] += partialWidth['width']
                    if verbose:
                        print 'null',lflavor,
                    processed+=1
                
                #NU NU NU 
                if partialWidth['ids'] == sorted([lflavor+1,lflavor2+1,lflavor2+1]):
                    widthPerFlavor[lflavor] += partialWidth['width']
                    if verbose:
                        print 'nununu',lflavor,
                    processed+=1
                
                    
            for qflavor in [1,2,3,4,5]:
                for qflavor2 in [1,2,3,4,5]:
                    if qflavor2>qflavor:
                        continue
                    #L QQ (note: qflavor==qflavor2 not possible)
                    if qflavor!=qflavor2 and partialWidth['ids'] == sorted([lflavor,qflavor,qflavor2]):
                        widthPerFlavor[lflavor] += partialWidth['width']
                        if verbose:
                            print 'lqq',lflavor,
                        processed+=1
                        
                    #NU QQ (note: only qflavor==qflavor2 possible) 
                    if qflavor==qflavor2 and partialWidth['ids'] == sorted([lflavor+1,qflavor,qflavor2]):
                        widthPerFlavor[lflavor] += partialWidth['width']
                        if verbose:
                            print 'nuqq',lflavor,
                        processed+=1
        if verbose:
            print
                       
    widthSum = 0.
    if couplings.has_key('e'):
        widthSum += couplings['e']**2*widthPerFlavor[11]/0.1**2
    if couplings.has_key('mu'):
        widthSum += couplings['mu']**2*widthPerFlavor[13]/0.1**2
    if couplings.has_key('tau'):
        widthSum += couplings['tau']**2*widthPerFlavor[15]/0.1**2
                    
    return widthSum
    
def ctauFromWidth(width):
    return hbar*c/width
    
def widthFromCtau(ctau):
    return hbar*c/ctau
    
def findCouplings(massHNL,ctau,relCouplings):
    logCouplingScale = scipy.optimize.bisect(
        lambda x: ctau-ctauFromWidth(widthTotal(massHNL,{k: v*10.0**x for (k,v) in relCouplings.items()})),
        -20,
        10
    )
    return {k: v*10.0**logCouplingScale for (k,v) in relCouplings.items()}
            
#print "-"*60
'''
mHNL = 2.0
couplings = {
    #'e':0.01,
    'mu':0.1,
    #'tau':0.03
}
'''
'''
#print widthTotal(3.0,{'e':0.0007,'mu':0.0011,'tau':0.0017},False)
#couplings = findCouplings(10.0,1.0,{'e':1.0,'mu':0.5}) 
#print couplings,ctauFromWidth(widthTotal(10.0,couplings))
ROOT.gROOT.SetBatch(True)
cv = ROOT.TCanvas("cv","",800,700)
axis = ROOT.TH2F("axis","",50,1,20,50,1e-10,4)
cv.SetLogy(1)
cv.SetLogx(1)
axis.Draw("AXIS")
rootObj = []

for ctau in [1e-2,1e-1,1e0,1e1,1e2,1e3,1e4]:
    
    for mHNL in [1.,1.5, 2.,3.,4.5,6.,8.,10.,12.,16.,20.]:
        targetCtau = ctau
        coupling = findCouplings(mHNL,ctau,{'e':1,'mu':1,'tau':1})['mu']
        #print "%4.1f, %.3e, %.4e"%(mHNL,coupling,widthTotal(mHNL,{'mu':coupling}))#,ctauFromWidth(widthTotal(mHNL,{'mu':coupling}))
        print "%.3e"%coupling
        
        if coupling**2>1 or coupling**2<5e-9:
            continue
        m = ROOT.TMarker(mHNL,coupling**2,20)
        rootObj.append(m)
        m.SetMarkerSize(1.0)
        m.SetMarkerColor(ROOT.kBlack)
        m.Draw("Same")
        
    print "Total width: ",widthTotal(mHNL,{'mu':0.1})#,ctauFromWidth(totalWidth),"mm"
cv.Update()
cv.Print("param.pdf")
'''


