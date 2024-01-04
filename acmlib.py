from numpy import sqrt
from numpy import log
import numpy as np
import tools

def compute_acm(formula,xene,wene,w1ene,mp2ene):
    if (formula == "isi"):
        correne = compute_isi(xene,wene,w1ene,mp2ene)
    elif (formula == "revisi"):
        correne = compute_revisi(xene,wene,w1ene,mp2ene)
    elif (formula == "spl"):
        correne = compute_spl(xene,wene,mp2ene)
    elif (formula == "lb"):
        correne = compute_lb(xene,wene,mp2ene)
    elif (formula == "genisi"): 
        correne = compute_genisi(xene,wene,w1ene,mp2ene)  
    elif (formula == "dpi"): 
        correne = compute_dpi(xene,wene,w1ene,mp2ene) 
    else:
        stri = "Formula "+formula+ " not implemented!"
        tools.error(stri)
    return correne


def print_refs(formula):
    if (formula == "isi"):
        refstri="Phys. Rev. Lett. 84, 5070 (2000)"
    elif (formula == "revisi"):
        refstri=" J. Chem. Theory Comput. 5, 743 (2009)"
    elif (formula == "spl"):
        refstri="Phys. Rev. A 59, 51 (1999)"
    elif (formula == "lb"):
        refstri="Phys. Rev. A 79, 064503 (2009)"
    elif (formula == "genisi"): 
        refstri="J. Chem. Phys. 159, 244111 (2023)"
    elif (formula == "dpi"):  
        refstri="Phys. Rev. B 81, 085123 (2010)"
    stri = "  Ref: " + refstri
    print(stri)
         

def compute_isi(xene,wene,w1ene,mp2ene):
    if (mp2ene == 0):
        return 0.0
    elif (mp2ene == -np.inf ):
        cene=compute_isi_lim(xene,wene,w1ene)   
        return cene
    else:
        x = -4*mp2ene
        y = w1ene
        z = xene - wene
        xx = x*(y**2)/(z**2)
        yy = (x**2)*(y**2)/(z**4)
        zz = x*(y**2)/(z**3) - 1.
        tmp1 = sqrt(1.+yy)
        tmp2 = tmp1 - 1 - zz*log((tmp1+zz)/(1.+zz))
        cene = (wene - xene) + 2.*xx*tmp2/yy
        return cene

def compute_revisi(xene,wene,w1ene,mp2ene):
    if (mp2ene == 0):
        return 0.0
    elif (mp2ene == -np.inf):
        cene=compute_revisi_lim(xene,wene,w1ene)     
        return cene
    else:
        tmp1 = 2.*mp2ene*(w1ene**2)
        tmp2 = (xene - wene)**2
        bb = -4.*tmp1/tmp2
        cc = 2.*4.*mp2ene*tmp1/(tmp2**2)
        dd = -1. - 4.*tmp1/(tmp2*(xene-wene))
        cene = (wene - xene) + bb/(sqrt(1.+cc)+dd)
        return cene

def compute_genisi(xene,wene,w1ene,mp2ene):
    if (mp2ene == 0):
        return 0.0
    elif (mp2ene == -np.inf):
        cene=compute_uegisi_lim(xene,wene,w1ene)-xene     
        return cene
    else:
        dd=3.5
        tmpueg=compute_uegisi_lim(xene,wene,w1ene)            
        tmpaa=xene*(1.+(xene-(wene))**3/(4.*2.*mp2ene*w1ene**2)*(1.+dd))
        tmppp=2.*mp2ene/xene
        tmpqq=18.*(xene/wene)**3
        tmpadd=tmpaa*tmppp/(2.*(tmpqq*tmppp+1)**2)
        cene=tmpadd + tmpueg-xene
        return cene

def  compute_dpi(xene,wene,w1ene,mp2ene):            
     if (mp2ene == 0):    
         return 0.0
     elif (mp2ene == -np.inf): 
         q =  (xene-wene)/w1ene     
         t1 = q ** 2
         t2 = t1 ** 2
         t4 = 0.8292998565e1 * t2 + 0.1e1
         t5 = t4 ** (0.1e1 / 0.4e1)
         t6 = t5 ** 2
         t7 = t6 * t5
         t10 = sqrt(0.1e1 + 0.2879756685e1 * t1)
         t11 = t10 * t7
         t12 = t2 * t1
         t15 = log(q)
         t21 = log(0.575951337e9 * t1 + 0.200000000e9)
         t42 = t1 * t7
         t44 = 0.1119834367e4 * t12 * t11 + 0.1110311573e3 * t15 * t12 * t11 - 0.5551557864e2 * t21 * t12 * t11 + 0.1709829722e4 * t2 * t11 + 0.1684395906e3 * t15 * t2 * t11 - 0.842197953e2 * t21 * t2 * t11 + 0.657067862e3 * t1 * t11 + 0.4510236884e2 * t15 * t1 * t11 - 0.2255118442e2 * t21 * t1 * t11 + 0.6636220998e2 * t11 - 0.4510236884e2 * t42
         t47 = t5 * t10
         t55 = sqrt(t4)
         t56 = t55 * t10
         t67 = -0.1298838482e3 * t2 * t7 + 0.2388181806e2 * t12 * t47 + 0.8292998564e1 * t2 * t47 - 0.5489204206e2 * t1 * t47 - 0.1906134721e2 * t47 + 0.1294717915e3 * t1 * t56 + 0.4495928153e2 * t56 + 0.455219626e3 * t12 * t10 + 0.5489204205e2 * t1 * t10 + 0.1580757251e3 * t2 * t10 + 0.1906134721e2 * t10
         t85 = 0.4291781739e12 * t42 + 0.1490327902e12 * t7 + 0.5363254149e11 * t12 * t5 + 0.1862398367e11 * t2 * t5 - 0.1232736853e12 * t1 * t5 - 0.4280697947e11 * t5 + 0.2907609974e12 * t1 * t55 + 0.1009672098e12 * t55 + 0.1022308496e13 * t12 + 0.1232736853e12 * t1 + 0.3549982194e12 * t2 + 0.4280697948e11
         Fq = 0.2245747845e10 / t10 / t85 * (t67 + t44) * q
         cene = wene + w1ene*Fq - xene   
         return cene
     else:
         return 0.0

def compute_uegisi_lim(xene,wene,w1ene):
    dd = 3.5
    tmpbb = (xene - wene)*(1. + dd)
    tmpcc = (tmpbb**2)/(4.*w1ene**2)
    tmpueg = wene + tmpbb / ( dd + sqrt(1.+tmpcc))
    return tmpueg
 
def compute_isi_lim(xene,wene,w1ene):
     q = (xene-wene)/w1ene
     Fq = 2.-2.*(log(1.+q))/q
     cene = wene + w1ene*Fq - xene
     return cene

def compute_revisi_lim(xene,wene,w1ene):  
     q = (xene-wene)/w1ene    
     Fq = 2.*q/(2.+q)     
     cene = wene + w1ene*Fq - xene              
     return cene

def compute_spl(xene,wene,mp2ene):
    if (mp2ene == 0):
        return 0.0
    elif (mp2ene == -np.inf):
        cene=compute_spl_lim(xene,wene)
        return cene            
    else:
        cc = 2.*mp2ene/(wene-xene)
        cene = (xene-wene)*((sqrt(1.+2.*cc)-1.-cc)/cc)
        return cene


def compute_lb(xene,wene,mp2ene):
    if (mp2ene == 0):
        return 0.0
    elif (mp2ene == -np.inf):
        cene=compute_lb_lim(xene,wene)       
        return cene
    else:
        bb = (xene - wene)/2.
        cc = 1.6*mp2ene/(wene-xene)
        cene = 2.*bb*( (sqrt(1.+cc) - (1.+cc/2.)/(1.+cc))/cc - 1.)
        return cene
        
def compute_spl_lim(xene,wene): 
     cene=wene-xene
     return cene

def compute_lb_lim(xene,wene):
     cene=wene-xene
     return cene
