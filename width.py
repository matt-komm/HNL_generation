import scipy
import scipy.integrate
import scipy.optimize
import math
import numpy
import ROOT

#calculations are taken from https://arxiv.org/abs/1805.08567
#following constants are MG defaults

GF = 1.174560e-05
mW = 7.995123e+01
mZ = 9.118760e+01
sinW2 = 1-(mW/mZ)**2
hbar = 6.58211915e-25 # hbar in GeV s
c = 299792458000.0 # speed of light in mm/s

mL = {
    'e':5.110000e-04, # Me 
    'mu':1.056600e-01, # MMU 
    'tau':1.777000e+00, # MTA 
}
    
mQ = {
    'd':5.040000e-03, # MD 
    'u':2.550000e-03, # MU 
    's':1.010000e-01, # MS 
    'c':1.270000e+00, # MC 
    'b':4.700000e+00, # MB 
    't':1.733000e+02, # MT
}

Vckm = {
    'ud':0.97427,
    'us':0.22534,
    'ub':0.00351,
    'cd':0.22520,
    'cs':0.97344,
    'cb':0.04120,
    'tu':0.00867,
    'ts':0.04040,
    'tb':0.99915
}

def lambdaFct(a,b,c):
    return a**2+b**2+c**2-2*(a*b+a*c+b*c)

def Iudl(xu,xd,xl):
    a = (xd+xl)**2
    b = (1-xu)**2

    fct = lambda x: 12./x*(x-xl**2-xd**2)*(1+xu**2-x)*numpy.sqrt(lambdaFct(x,xl**2,xd**2)*lambdaFct(1,x,xu**2))
    return scipy.integrate.quad(fct,a,b)[0]
    

def widthNUNU_NC_sameFlavor(massHNL,couplingHNL):
    #NOTE: the paper suggests 2x cross section while MG agrees with 0.5x
    #TODO: this could be different for majorana vs dirac (i.e. paper assumes majorana)
    return 0.5*widthNUNU_NC_oppositeFlavor(massHNL,couplingHNL) 

def widthNUNU_NC_oppositeFlavor(massHNL,couplingHNL):
    return (1+0)*GF**2*massHNL**5/(768*math.pi**3)*couplingHNL**2

def widthQQ_CC(massHNL,couplingHNL,Vud,massL,massU,massD):
    Nc = 3.0
    Nw = Nc*Vud**2
    xl = massL/massHNL
    xu = massU/massHNL
    xd = massD/massHNL
    
    if xl>0.49:
        return 0
    if xu>0.49:
        return 0
    if xd>0.49:
        return 0
    
    return Nw*GF**2*massHNL**5/(192.0*math.pi**3)*couplingHNL**2*Iudl(xu,xd,xl)
    
def widthUU_NC(massHNL,couplingHNL,massU):
    NZ = 3

    C1 = 1/4.*(1-8/3.*sinW2+32/9.*sinW2**2)
    C2 = 1/3.*sinW2*(4/3.*sinW2-1)
    
    x = massU/massHNL
    if x>0.49:
        return 0 #kinematically forbidden
        
    #Lx = math.log((1-3*x**2-(1-x**2)*math.sqrt(1-4*x**2))/(x**2*(1+math.sqrt(1-4*x**2))))
    Lx = 0 #NOTE: there seems to be a mistake in the Lx equation; 
    #anyway this seems to be a small correction
    result = C1*((1-14*x**2-2*x**4-12*x**6)*math.sqrt(1-4*x**2)+12*x**4*(x**4-1)*Lx)
    result += 4*C2*(x**2*(2+10*x**2-12*x**4)*math.sqrt(1-4*x**2)+6*x**4*(1-2*x**2+2*x**4)*Lx)
    result *= NZ*GF**2*massHNL**5/(192*math.pi**3)*couplingHNL**2

    return result
    
def widthDD_NC(massHNL,couplingHNL,massD):
    NZ = 3

    C1 = 1/4.*(1-4/3.*sinW2+8/9.*sinW2**2)
    C2 = 1/6.*sinW2*(2/3.*sinW2-1)
    
    x = massD/massHNL
    if x>0.49:
        return 0 #kinematically forbidden
        
    #Lx = math.log((1-3*x**2-(1-x**2)*math.sqrt(1-4*x**2))/(x**2*(1+math.sqrt(1-4*x**2))))
    Lx = 0 #NOTE: there seems to be a mistake in the Lx equation; 
    #anyway this seems to be a small correction
    result = C1*((1-14*x**2-2*x**4-12*x**6)*math.sqrt(1-4*x**2)+12*x**4*(x**4-1)*Lx)
    result += 4*C2*(x**2*(2+10*x**2-12*x**4)*math.sqrt(1-4*x**2)+6*x**4*(1-2*x**2+2*x**4)*Lx)
    result *= NZ*GF**2*massHNL**5/(192*math.pi**3)*couplingHNL**2

    return result
    
    
    
#charged current; i.e. leptons need to be different
def widthLNU_CC_oppositeFlavor(massHNL,couplingHNL,massL1,massL2):
    Nw = 1.0
    if (abs(massL1-massL2)/massL1<1e-3):
        print "WARNING - leptons need to be opposite flavor for CC decay"
    xl = massL1/massHNL
    xu = massL2/massHNL
    
    if xl>0.49:
        return 0
    if xu>0.49:
        return 0
    
    xd = 0.0
    return Nw*GF**2*massHNL**5/(192.0*math.pi**3)*couplingHNL**2*Iudl(xu,xd,xl)
    
#neutral+charged current for same flavour leptons; 
#e.g. HNL->nu,e+,e- = HNL->e-,W+ with W->nu,e+ AND HNL->nu,Z with Z->e+,e-
def widthLNU_sameFlavor(massHNL,couplingHNL,massL):
    NZ = 1

    C1 = 0.25*(1+4*sinW2+8*sinW2**2)
    C2 = 0.5*sinW2*(2*sinW2+1)
    
    x = massL/massHNL
    if x>0.49:
        return 0 #kinematically forbidden
    
    #Lx = math.log((1-3*x**2-(1-x**2)*math.sqrt(1-4*x**2))/(x**2*(1+math.sqrt(1-4*x**2))))
    Lx = 0 #NOTE: there seems to be a mistake in the Lx equation; 
    #anyway this seems to be a small correction
    result = C1*((1-14*x**2-2*x**4-12*x**6)*math.sqrt(1-4*x**2)+12*x**4*(x**4-1)*Lx)
    result += 4*C2*(x**2*(2+10*x**2-12*x**4)*math.sqrt(1-4*x**2)+6*x**4*(1-2*x**2+2*x**4)*Lx)
    result *= NZ*GF**2*massHNL**5/(192*math.pi**3)*couplingHNL**2

    return result

#neutral current where leptons have different flavor than neutrino
def widthLNU_NC_oppositeFlavor(massHNL,couplingHNL,massL):
    NZ = 1

    C1 = 0.25*(1-4*sinW2+8*sinW2**2)
    C2 = 0.5*sinW2*(2*sinW2-1)
    
    x = massL/massHNL
    if x>0.49:
        return 0 #kinematically forbidden
        
    #Lx = math.log((1-3*x**2-(1-x**2)*math.sqrt(1-4*x**2))/(x**2*(1+math.sqrt(1-4*x**2))))
    Lx = 0 #NOTE: there seems to be a mistake in the Lx equation; 
    #anyway this seems to be a small correction
    result = C1*((1-14*x**2-2*x**4-12*x**6)*math.sqrt(1-4*x**2)+12*x**4*(x**4-1)*Lx)
    result += 4*C2*(x**2*(2+10*x**2-12*x**4)*math.sqrt(1-4*x**2)+6*x**4*(1-2*x**2+2*x**4)*Lx)
    result *= NZ*GF**2*massHNL**5/(192*math.pi**3)*couplingHNL**2

    #TODO: this can be negative near thresholds?
    if result<0:
        return 0

    return result

def ctauFromWidth(width):
    return hbar*c/width
    
def widthFromCtau(ctau):
    return hbar*c/ctau
    
    
totalWidth = 0.



def widthTotal(massHNL,couplings,verbose = False):
    widthSum = 0.0
    for leptonFlavor,coupling in couplings.iteritems():
        if verbose:
            print "Lepton flavor: ",leptonFlavor 
        
        if verbose:
            print "\tL QQ (CC)"
        for uq in ['u','c']: 
            for dq in ['d','s']:
                w = widthQQ_CC(massHNL,coupling,Vckm[uq+dq],mL[leptonFlavor],mQ[uq],mQ[dq])
                if verbose:
                    print '\t\t%-5s %-5s %-5s %.4e'%(leptonFlavor,uq,dq,w)
                widthSum += w
                
        if verbose:
            print "\tNU UU (NC)"
        for uq in ['u','c']: 
            w = widthUU_NC(massHNL,coupling,mQ[uq])
            if verbose:
                print '\t\t%-5s %-5s %-5s %.4e'%('nu'+leptonFlavor,uq,uq,w)
            widthSum += w
            
        if verbose:        
            print "\tNU DD (NC)"
        for dq in ['d','s']: 
            w = widthDD_NC(massHNL,coupling,mQ[dq])
            if verbose:
                print '\t\t%-5s %-5s %-5s %.4e'%('nu'+leptonFlavor,dq,dq,w)
            widthSum += w
            
        if verbose:
            print "\tL LNU (CC)"
        for leptonFlavor2 in ['e','mu','tau']:
            if leptonFlavor!=leptonFlavor2:
                w = widthLNU_CC_oppositeFlavor(massHNL,coupling,mL[leptonFlavor],mL[leptonFlavor2])
                if verbose:
                    print '\t\t%-5s %-5s %-5s %.4e'%(leptonFlavor,leptonFlavor2,'nu'+leptonFlavor2,w)
                widthSum += w
            
        if verbose:    
            print "\tL LNU (CC+NC)"
        for leptonFlavor2 in ['e','mu','tau']:
            if leptonFlavor==leptonFlavor2:
                w = widthLNU_sameFlavor(massHNL,coupling,mL[leptonFlavor])
                if verbose:
                    print '\t\t%-5s %-5s %-5s %.4e'%(leptonFlavor,leptonFlavor2,'nu'+leptonFlavor2,w)
                widthSum += w
        
        if verbose:
            print '\tNU LL (NC)'
        for leptonFlavor2 in ['e','mu','tau']:
            #same falvor can be CC and NC and is handled in LNU
            if leptonFlavor!=leptonFlavor2:
                w = widthLNU_NC_oppositeFlavor(massHNL,coupling,mL[leptonFlavor2])
                if verbose:
                    print '\t\t%-5s %-5s %-5s %.4e'%('nu'+leptonFlavor,leptonFlavor2,leptonFlavor2,w)
                widthSum += w
                
        if verbose:
            print "\tNU NUNU (NC)"
        for leptonFlavor2 in ['e','mu','tau']:
            if leptonFlavor==leptonFlavor2:
                w = widthNUNU_NC_sameFlavor(massHNL,coupling)
                if verbose:
                    print '\t\t%-5s %-5s %-5s %.4e'%('nu'+leptonFlavor,'nu'+leptonFlavor2,'nu'+leptonFlavor2,w)
                widthSum += w
            else:
                w = widthNUNU_NC_oppositeFlavor(massHNL,coupling)
                if verbose:
                    print '\t\t%-5s %-5s %-5s %.4e'%('nu'+leptonFlavor,'nu'+leptonFlavor2,'nu'+leptonFlavor2,w)
                widthSum += w
                
    return widthSum
    
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

#print widthTotal(20.0,{'e':0.1,'mu':0.2,'tau':0.3},True))
#couplings = findCouplings(10.0,1.0,{'e':1.0,'mu':0.5}) 
#print couplings,ctauFromWidth(widthTotal(10.0,couplings))
'''
cv = ROOT.TCanvas("cv","",800,700)
axis = ROOT.TH2F("axis","",50,1,20,50,1e-10,1)
cv.SetLogy(1)
cv.SetLogx(1)
axis.Draw("AXIS")
rootObj = []

for ctau in [1e-1,1e0,1e1,1e2,1e3,1e4]:
    
    for mHNL in [1.,1.5, 2.,3.,4.,6.,8.,10.,14.,20.]:
        targetCtau = ctau
        logCoupling = scipy.optimize.bisect(
            lambda x: targetCtau-ctauFromWidth(widthTotal(mHNL,{'e':0.0*10.0**x,'mu':1.0*10.0**x,'tau':0.0*10.0**x})),
            -10,
            1
        )
        coupling = 10.0**logCoupling
        #print "%4.1f, %.3e, %.4e"%(mHNL,coupling,widthTotal(mHNL,{'mu':coupling}))#,ctauFromWidth(widthTotal(mHNL,{'mu':coupling}))
        print "%.3e"%coupling
        
        if coupling**2>1 or coupling**2<1e-10:
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
