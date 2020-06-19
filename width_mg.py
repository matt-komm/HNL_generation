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
     
        #note: dirac is 9990012; majorana 9900012 
        mMass = re.match("\\s*99[0-9]+012\\s+([0-9]*\\.[0-9]*[eE][+-][0-9]+)\\s+#\\s+mn1",l)
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
            
        #note: dirac is 9990012; majorana 9900012 
        mWidth = re.match('DECAY\\s+99[0-9]+012\\s+([0-9]*\\.[0-9]*[eE][+-][0-9]+)',l)
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
    
    
def groupWidthByFlavor(partialWidths,verbose=False):
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
            
    return widthPerFlavor
                       
                   
diracCache = {}
def widthTotalDirac(massHNL,couplings,verbose = False):
    if not diracCache.has_key(massHNL):
        partialWidths = getPartialWidthsFromParamCard(
            os.path.join(scriptPath,'templates','HNL_dirac','params0p1','param_card_massHNL%.1f.dat'%(massHNL)),
            massHNL
        )
        

        diracCache[massHNL] = groupWidthByFlavor(partialWidths,verbose)
    widthPerFlavor = diracCache[massHNL]
                       
    widthSum = 0.
    if couplings.has_key('e'):
        widthSum += couplings['e']**2*widthPerFlavor[11]/0.1**2
    if couplings.has_key('mu'):
        widthSum += couplings['mu']**2*widthPerFlavor[13]/0.1**2
    if couplings.has_key('tau'):
        widthSum += couplings['tau']**2*widthPerFlavor[15]/0.1**2
                    
    return widthSum
    
    
    
majoranaCache = {}
def widthTotalMajorana(massHNL,couplings,verbose = False):
    
    if not majoranaCache.has_key(massHNL):
        partialWidths = getPartialWidthsFromParamCard(
            os.path.join(scriptPath,'templates','HNL_majorana','params0p1','param_card_massHNL%.1f.dat'%(massHNL)),
            massHNL
        )
        

        majoranaCache[massHNL] = groupWidthByFlavor(partialWidths,verbose)
    widthPerFlavor = majoranaCache[massHNL]
                    
                       
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
    
def findCouplingsDirac(massHNL,ctau,relCouplings):
    logCouplingScale = scipy.optimize.bisect(
        lambda x: ctau-ctauFromWidth(widthTotalDirac(massHNL,{k: v*10.0**x for (k,v) in relCouplings.items()})),
        -20,
        10
    )
    return {k: v*10.0**logCouplingScale for (k,v) in relCouplings.items()}
    
def findCouplingsMajorana(massHNL,ctau,relCouplings):
    logCouplingScale = scipy.optimize.bisect(
        lambda x: ctau-ctauFromWidth(widthTotalMajorana(massHNL,{k: v*10.0**x for (k,v) in relCouplings.items()})),
        -20,
        10
    )
    return {k: v*10.0**logCouplingScale for (k,v) in relCouplings.items()}
            
#print "-"*60

for mHNL in [1.,1.5, 2.,2.5,3.,3.5,4.,4.5,6.,7.,8.,9.,10.,12.,14.,16.,18.,20.,22.,24.]:
    couplings = {
        'e':0.01,
        'mu':0.02,
        'tau':0.03
    }
    print "%4.1f"%mHNL,"%.5f"%(2*widthTotalDirac(mHNL,couplings)/widthTotalMajorana(mHNL,couplings)-1)
   
for ctau in [1e-2,1,1e2]:
    for mHNL in [1.,1.5, 2.,2.5,3.,3.5,4.,4.5,6.,7.,8.,9.,10.,12.,14.,16.,18.,20.,22.,24.]:
        couplings = {
            'e':0.01,
            #'mu':0.02,
            'tau':0.03,
        }
        couplingsDirac = findCouplingsDirac(mHNL,ctau,couplings)['e']
        couplingsMajorana = findCouplingsMajorana(mHNL,ctau,couplings)['e']
        print "%4.1e"%ctau,"%4.1f"%mHNL,"%.5f"%(couplingsDirac/couplingsMajorana)
    
  
    
'''

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
cv.SetGrid(1)
axis = ROOT.TH2F("axis",";m#lower[0.7]{#scale[0.8]{HNL}} (GeV); |V#lower[0.7]{#scale[0.8]{Nx}}|#lower[-0.7]{#scale[0.8]{2}}",
    50,1,20,50,1e-9,1
)
cv.SetLogy(1)
cv.SetLogx(1)
axis.Draw("AXIS")
rootObj = []

colors = [ROOT.kViolet,ROOT.kBlue,ROOT.kGreen+1,ROOT.kRed+1,ROOT.kOrange,ROOT.kGray,ROOT.kBlack]
f = open('points.txt','w')
for j,ctau in enumerate([1e-2,1e-1,1e0,1e1,1e2,1e3,1e4]):
    masses = []
    values = []
    for mHNL in [1.,1.5, 2.,3.,4.5,6.,8.,10.,12.,16.,20.]:
        #couplingMu = findCouplings(mHNL,ctau,{'mu':1.0})
        couplingAll = findCouplingsMajorana(mHNL,ctau,{'e':1.0,'mu':1.0,'tau':1.0})
        coupling = couplingAll['mu']
        #print "%4.1f, %.3e, %.4e"%(mHNL,coupling,widthTotal(mHNL,{'mu':coupling}))#,ctauFromWidth(widthTotal(mHNL,{'mu':coupling}))
        print "%.3e"%coupling
        
        
        if couplingAll['mu']**2>1 or couplingAll['mu']**2<5e-9:
            continue
        f.write('%.1e %.1f %.3e\n'%(ctau,mHNL,coupling))
        m = ROOT.TMarker(mHNL,coupling**2,20)
        rootObj.append(m)
        m.SetMarkerSize(1.7)
        m.SetMarkerColor(colors[j])
        m.Draw("Same")
        
        masses.append(mHNL)
        values.append(coupling**2)
        
    graph = ROOT.TGraph(len(masses),numpy.array(masses),numpy.array(values))
    graph.SetLineStyle(2)
    graph.SetLineWidth(2)
    graph.SetLineColor(colors[j])
    graph.Draw("L")
    rootObj.append(graph)
        

f.close()
cv.Update()
cv.Print("param3.pdf")
'''



