#!/usr/bin/env python3

import os
from numpy import array as nparray
from numpy import sum as npsum
from numpy import sqrt
from numpy import exp
import shutil
import subprocess
import tools
import argparse
from datetime import datetime
import acmlib


############################################################
#   FUNCTIONS
############################################################

# manage the command line options
def manage_options():
    parser = argparse.ArgumentParser(description='PREREQUISITE: Input file with all informations about the test to be run.')
#
    parser.add_argument("-i","--input",
                        required=True,
                        metavar="<string>",
                        help="Input file name (full path)")
#
    parser.add_argument("-a","--acmxc-exe",
                        default="/home/users/fabiano/fhgfs/HFAMC/NEW_PYTHON/SVN/LIB_VERSION/acmxc.py",
                        metavar="<string>",
                        help="Full path of the acmxc script")
#
    parser.add_argument("-b","--basis",
                        default="cc-pVTZ",
                        metavar="<string>",
                        help="Basis set to employ")
#
    parser.add_argument("--no-bsse",
                        action='store_false',
                        default=True,
                        help="Do not perform counterpois correction for BSSE (default: perform)")
#
    parser.add_argument("-f","--formula",
                        default="isi",
                        choices=["isi","revisi","spl","lb","spl2","mpacf1","genisi","dpi","mp2"],
                        help="Formula to be used. Options: isi, revisi, genisi, spl, lb, spl2, mpacf1, dpi, mp2",
                        metavar="<string>")
#
    parser.add_argument("-w","-wfunc",
                        default="hpc",
                        choices=["pc","hpc","mpc"],
                        help="W_inf functional. Options: pc, hpc, mpc",
                        metavar="<string>")
#
    parser.add_argument("-n","-nthreads",
                        default=1,
                        type=int,
                        help="Number of threads to use (default: 1)",
                        metavar="<int>")
#
    options = vars(parser.parse_args())
#
#
    return options



def read_input(filename):
    with open(filename,"r") as f:
        content = f.readlines()
        names = [line.split(";")[0] for line in content]
        ref_enes = [float(line.split(";")[1]) for line in content]
        nfrags = [int(line.split(";")[2]) for line in content]
        coeffs = [line.split(";")[3] for line in content]
        charges = [line.split(";")[4] for line in content] #es 0, 1, -1
        frag_atoms = [line.split(";")[5] for line in content] #es 1 2 , 3 4 5 , 6
        coords = [line.split(";")[6] for line in content] #es o 0.0 0.0 0.0 , h 1.0 0.0 0.0 , h 0.0 1.0 0.0
    return names, ref_enes, nfrags, coeffs, charges, frag_atoms, coords


def write_coord_file(coords):
    conv = 1.88972612462577
    with open("coord","w") as f:
        f.write("$coord\n")
        for line in coords:
            x = float(line.split()[1])*conv
            y = float(line.split()[2])*conv
            z = float(line.split()[3])*conv
            f.write(f"{x:.7f}  {y:.7f}  {z:.7f}  {line.split()[0]}\n")
        f.write("$end")
    
## run define
def run_define(basis,charge,freeze):
    with open("def.in","w") as f:
        f.write("\n\n")
        f.write("a coord\n")
        f.write("*\n")
        f.write("no\n")
        f.write(f"b all {basis}\n")
        if (freeze != None):
            ff = "".join(f"{str(i)}," for i in freeze)
            fff = ff[:ff.rfind(",")] + ff[ff.rfind(",")+1:]
            f.write(f"c {fff} 0\n\n")
        f.write("*\n")
        f.write("eht\n")
        f.write("\n")
        f.write(f"{charge}\n")
        f.write("\n\n\n\n\n\n\n")
        f.write("ri\n")
        f.write("on\n")
        f.write("m 50000\n")
        f.write("\n")
        f.write("marij\n")
        f.write("\n")
        f.write("scf\n")
        f.write("iter\n")
        f.write("100\n")
        f.write("\n")
        f.write("cc\n")
        f.write("cbas\n")
        f.write("*\n")
        f.write("*\n")
        f.write("*\n")
        f.close()
    with open("def.out","w") as f:
        with open("def.in") as inp:
            subprocess.run(["define"], stdin=inp, stdout=f, stderr=subprocess.DEVNULL)
    tools.adg("$ricc2\n  mp2")


def extract_energy(path):
    with open(f"{path}/acmxc.out","r") as f:
        content = f.readlines()
        for line in content:
            if ("SCC interaction energy:" in line):
                eint = float(line.split()[3])
    return eint


def extract_energy_components(path):
    with open(f"{path}/acmxc.out","r") as f:
        content = f.readlines()
        scfene = nparray([float(line.split()[len(line.split())-1]) for line in content if "SCF energy:" in line and "Int." not in line])
        xene = nparray([float(line.split()[len(line.split())-1]) for line in content if "HF-exchange energy:" in line])
        wene = nparray([float(line.split()[len(line.split())-1]) for line in content if "W_inf energy:" in line and "Int." not in line])
        w1ene = nparray([float(line.split()[len(line.split())-1]) for line in content if "W1_inf energy:" in line and "Int." not in line])
        mp2ene = nparray([float(line.split()[len(line.split())-1]) for line in content if "MP2 corr. energy:" in line])
        return scfene, xene, wene, w1ene, mp2ene
    

def print_header(logfile):
    data = datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
    print("")
    print("             +-----------------------------------+")
    print("             |             ACMxc TEST            |")
    print("             | Run tests for HF-ACM calculations |")
    print("             |                                   |")
    print("             +-----------------------------------+")
    print("")
    print(data)
    logfile.write("\n")
    logfile.write("             +-----------------------------------+\n")
    logfile.write("             |             ACMxc TEST            |\n")
    logfile.write("             | Run tests for HF-ACM calculations |\n")
    logfile.write("             |                                   |\n")
    logfile.write("             +-----------------------------------+\n") 
    logfile.write("\n")        
                  

def print_options(logfile,options):
    input_filename = options["input"]
    acmxc_exe = options["acmxc_exe"]
    formula = options["formula"]
    wfunc = options["w"]
    ncpu = str(options["n"])
    basis = options["basis"]
    bsse = options["no_bsse"]
    print("")
    print(f"Input data file: {input_filename}")
    print(f"ACM model: {formula}")
    print(f"W functional: {wfunc}")
    print(f"Basis set: {basis}")
    print(f"BSSE: {bsse}")
    print(f"ACMxc path: {acmxc_exe}")
    print(f"N. cpu: {ncpu}")
    print("")
    logfile.write("\n")
    logfile.write(f"Input data file: {input_filename}\n")
    logfile.write(f"ACM model: {formula}\n")
    logfile.write(f"W functional: {wfunc}\n")
    logfile.write(f"Basis set: {basis}\n")
    logfile.write(f"BSSE: {bsse}\n")
    logfile.write(f"ACMxc path: {acmxc_exe}\n")
    logfile.write(f"N. cpu: {ncpu}\n")
    logfile.write("\n")

    
def extrapolate_23(dz_scfene,dz_xene,dz_wene,dz_w1ene,dz_mp2ene,tz_scfene,tz_xene,tz_wene,tz_w1ene,tz_mp2ene):
    aa = 2.085
    cbs_scfene = (tz_scfene*exp(-2.*aa) - dz_scfene*exp(-3.*aa))/(exp(-2.*aa) -exp(-3.*aa))
    cbs_xene = (tz_xene*exp(-2.*aa) - dz_xene*exp(-3.*aa))/(exp(-2.*aa) -exp(-3.*aa))
    cbs_wene = (tz_wene*exp(-2.*aa) - dz_wene*exp(-3.*aa))/(exp(-2.*aa) -exp(-3.*aa))
    cbs_w1ene = (tz_w1ene*exp(-2.*aa) - dz_w1ene*exp(-3.*aa))/(exp(-2.*aa) -exp(-3.*aa))
    aa = 0.3939 # 1.
    tmp1 = (3.+aa)**3
    tmp2 = (2.+aa)**3
    cbs_mp2ene = (tz_mp2ene*tmp1 - dz_mp2ene*tmp2)/(tmp1-tmp2)
    return cbs_scfene,cbs_xene,cbs_wene,cbs_w1ene,cbs_mp2ene


def acm_calc(formula,coeff,cbs_scfene,cbs_xene,cbs_wene,cbs_w1ene,cbs_mp2ene):
    cbs_correne = []
    for i in range(len(cbs_xene)):
        cbs_correne.append(acmlib.compute_acm(formula,cbs_xene[i],cbs_wene[i],cbs_w1ene[i],cbs_mp2ene[i]))
    int_scfene = npsum(coeff*cbs_scfene)
    int_xene = npsum(coeff*cbs_xene)
    int_wene = npsum(coeff*cbs_wene)
    int_w1ene = npsum(coeff*cbs_w1ene)
    int_mp2ene = npsum(coeff*cbs_mp2ene)
    int_correne = npsum(coeff*cbs_correne)
    int_xcene = int_xene + int_correne
##    print(int_scfene,int_xene,int_wene,int_w1ene,int_mp2ene,int_correne)
    inf_scfene = -(int_scfene - coeff[0]*cbs_scfene[0])
    inf_xene = -(int_xene - coeff[0]*cbs_xene[0])
    inf_wene = -(int_wene - coeff[0]*cbs_wene[0])
    inf_w1ene = -(int_w1ene - coeff[0]*cbs_w1ene[0])
    inf_mp2ene = -(int_mp2ene - coeff[0]*cbs_mp2ene[0])
    inf_correne = acmlib.compute_acm(formula,inf_xene,inf_wene,inf_w1ene,inf_mp2ene)
    scc_correne = cbs_correne[0]*coeff[0] - inf_correne
    scc_xcene = int_xene + scc_correne
    scc = scc_correne - int_correne
    int_totene = int_scfene + int_correne
    scc_totene = int_scfene + scc_correne
    return int_totene, scc_totene


############################################################
#   CLASSES
############################################################

class system:

    def __init__(self,name,ref_ene,nfrags,coeffs,charges,frag_atoms,coords,basis,bsse):
        self.name = name.strip()
        self.path = f"{os.getcwd()}/{self.name}"
        self.refene = float(ref_ene)
        self.nfrags = int(nfrags)
        self.set_coeffs(coeffs)
        self.set_charges(charges)
        self.set_coords(coords)
        self.basis = basis
        self.bsse = bsse
        self.tot = molecule("TOTAL",self.path,self.coords,None,self.charges[0],self.basis)
        self.set_fragments(self.path,self.coords,self.nfrags,frag_atoms,self.charges[1:],self.basis,self.bsse)
        if (os.path.isdir(self.path)): shutil.rmtree(self.path) #tools.remove_dir(self.path)
        os.mkdir(self.path)

        
    def set_coeffs(self,coeffs):
        self.coeffs = nparray([float(c) for c in coeffs.split(",")])

        
    def set_charges(self,charges):
        self.charges = nparray([int(c) for c in charges.split(",")])


    def set_coords(self,coords):
        self.coords = [coord for coord in coords.split(",")]


    def set_fragments(self,path,coords,nfrags,frag_atoms,charges,basis,bsse):
        self.fragments = []
        for i in range(nfrags):
            name = f"FRAG{i+1}"
            atoms = [int(j) for j in frag_atoms.split(",")[i].split()]
            if (bsse):
                frag_coords = coords
                freeze = [j+1 for j in range(len(coords)) if j+1 not in atoms]
            else:
                frag_coords = [coords[j-1] for j in atoms]
                freeze = None
            charge = charges[i]
            self.fragments.append(molecule(name,path,frag_coords,freeze,charge,basis)) 


    def prepare_input(self):
        self.tot.prepare_input()
        for frag in self.fragments:
            frag.prepare_input()
        here = os.getcwd()
        os.chdir(self.path)
        with open("acmxc_int.info","w") as f:
            f.write(f"{self.coeffs[0]}  {self.tot.name}\n")
            for i in range(self.nfrags):
                f.write(f"{self.coeffs[i+1]}  {self.fragments[i].name}\n")
        os.chdir(here)


    def run_calc(self,acmxc_command):
        here = os.getcwd()
        os.chdir(self.path)
        with open("acmxc.out","w") as f:
            subprocess.run(acmxc_command, stdout=f, stderr=subprocess.DEVNULL)
        os.chdir(here)
        

#-------------------------#

class molecule:

    def __init__(self,name,path,coords,freeze,charge,basis):
        self.name = name.strip()
        self.path = f"{path}"
        self.coords = coords
        self.freeze = freeze
        self.charge = charge
        self.basis = basis


    def prepare_input(self):
        here = os.getcwd()
        os.chdir(self.path)
        if (os.path.isdir(self.name)): shutil.rmtree(self.name)
        os.mkdir(self.name)
        os.chdir(self.name)
        write_coord_file(self.coords)
        run_define(self.basis,self.charge,self.freeze)
        os.chdir(here)

        
############################################################
#   MAIN CODE
############################################################

options = manage_options()
input_filename = options["input"]
acmxc_exe = options["acmxc_exe"]
formula = options["formula"]
wfunc = options["w"]
ncpu = str(options["n"])
basis = options["basis"]
bsse = options["no_bsse"]
acmxc_command = [acmxc_exe,"-p","turbomole","-f",formula,"-w",wfunc,"-n",ncpu,"--int","acmxc_int.info"]


if (os.path.isdir("acmxc_test.log")): shutil.rmtree("acmxc_test.log")
logfile = open("acmxc_test.log","w")

print_header(logfile)
print_options(logfile,options)


names, ref_enes, nfrags, coeffs, charges, frag_atoms, coords = read_input(input_filename)


ref = []
diff = []
for j in range(len(names)):
    if (basis == "ext-23"):
#       DZ
        sys = system(names[j],ref_enes[j], nfrags[j], coeffs[j], charges[j], frag_atoms[j], coords[j],"aug-cc-pVDZ",bsse)
        sys.prepare_input() ; sys.run_calc(acmxc_command)
        dz_scfene, dz_xene, dz_wene, dz_w1ene, dz_mp2ene = extract_energy_components(sys.path)
#       TZ
        sys = system(names[j],ref_enes[j], nfrags[j], coeffs[j], charges[j], frag_atoms[j], coords[j],"aug-cc-pVTZ",bsse)
        sys.prepare_input() ; sys.run_calc(acmxc_command)
        tz_scfene, tz_xene, tz_wene, tz_w1ene, tz_mp2ene = extract_energy_components(sys.path)
#       EXTRAPOLATION AND SCC INTERACTION ENERGY
        cbs_scfene,cbs_xene,cbs_wene,cbs_w1ene,cbs_mp2ene = extrapolate_23(dz_scfene,dz_xene,dz_wene,dz_w1ene,dz_mp2ene,tz_scfene,tz_xene,tz_wene,tz_w1ene,tz_mp2ene)
        int_totene, scc_totene = acm_calc(formula,sys.coeffs,cbs_scfene,cbs_xene,cbs_wene,cbs_w1ene,cbs_mp2ene)
        eint = scc_totene * -627.50960803
    else:
#       ANY BASIS SET
        sys = system(names[j],ref_enes[j], nfrags[j], coeffs[j], charges[j], frag_atoms[j], coords[j],basis,bsse)
        sys.prepare_input()
        sys.run_calc(acmxc_command)
        eint = extract_energy(sys.path) * -627.50960803
#   PRINT RESULTS
    dd = eint - sys.refene
    print(f"{sys.name:18s}  Energy: {eint:.5f}  Ref: {sys.refene:.5f}  Diff: {dd:.5f}")
    logfile.write(f"{sys.name:18s}  Energy: {eint:.5f}  Ref: {sys.refene:.5f}  Diff: {dd:.5f}\n")
    ref.append(sys.refene)
    diff.append(dd)
diff = nparray(diff)
ref = nparray(ref)

    
# FINAL STATISTICS
som = npsum(diff)
ssom = npsum(diff*diff)
asom = npsum(abs(diff))
rsom = npsum(abs(diff)/abs(ref))
nn = len(diff)
stdev = sqrt(ssom/nn - (som/nn)**2)

print("--------------")
print(f"ME: {som/nn:.5f}")
print(f"MAE: {asom/nn:.5f}")
print(f"MARE: {rsom/nn:.5f}")
print(f"Std.Dev.: {stdev:.5f}")
print("")
logfile.write("--------------\n")
logfile.write(f"ME: {som/nn:.5f}\n")
logfile.write(f"MAE: {asom/nn:.5f}\n")
logfile.write(f"MARE: {rsom/nn:.5f}\n")
logfile.write(f"Std.Dev.: {stdev:.5f}\n")
logfile.write("\n")


logfile.close()

