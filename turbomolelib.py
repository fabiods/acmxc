import os
import tools
import subprocess
import shutil


class turbomole:

    def __init__(self,tdir,ncpu,wfunc):
        self.ncpu = ncpu
        self.wfunc = wfunc
        self.turbodir = self.check_turbodir(tdir)
        self.set_turbomole()
        self.scf_file_name = "scf.out"
        self.w_file_name = "w.out"
        self.mp2_file_name = "mp2.out"


# check the value of TURBODIR and set it if not defined
    def check_turbodir(self,tdir):
#   if tdir was not given in command line set it to the default value ($TURBODIR)
        if (tdir == None):
            envtdir=os.getenv('TURBODIR')
            if (envtdir == None):
                stri="The $TURBODIR variable is not set!"
                tools.error(stri)
            else:
                tdir = envtdir
#   check if tdir is a proper directory
        if (os.path.isdir(tdir) == False):
            stri= f"{tdir} is not a valid directory for $TURBODIR"
            tools.error(stri)
        return tdir


# set turbomole environment variables and executables paths
    def set_turbomole(self):
        para_arch = "SMP" if (self.ncpu > 1) else ""
        os.putenv("PARA_ARCH",para_arch)
        os.putenv("SMPCPUS",str(self.ncpu))
        sname = subprocess.check_output("sysname", shell=True).decode('utf-8').strip()
        ssname = subprocess.check_output("sysname -s", shell=True).decode().strip()
        if (self.ncpu > 1):
            path = f"{self.turbodir}/scripts:{self.turbodir}/bin/{sname}:{self.turbodir}/bin/{ssname}:/bin:/usr/bin"
        else:
            path = f"{self.turbodir}/scripts:{self.turbodir}/bin/{sname}:/bin:/usr/bin"
        os.putenv("PATH",path)
        if (self.ncpu > 1):
            self.ridft_exec = f"{self.turbodir}/bin/{sname}/ridft_smp"
            self.ricc2_exec = f"{self.turbodir}/bin/{sname}/ricc2_smp"
        else:
            self.ridft_exec = f"{self.turbodir}/bin/{sname}/ridft"
            self.ricc2_exec = f"{self.turbodir}/bin/{sname}/ricc2"


    def check_scf_convergence(self):
        with open(self.scf_file_name,"r") as f:
            scf_content = f.readlines()
        return any("convergence criteria satisfied" in line for line in scf_content)


    def check_mp2_convergence(self):
        with open(self.mp2_file_name,"r") as f:
            mp2_content = f.readlines()
        return any("ricc2 : all done" in line for line in mp2_content)
 

    def checkscf(self):
        check_file = os.path.isfile("control")
        if (not check_file):
            stri="control file not found!"
            tools.error(stri)   
        sline = subprocess.check_output("sdg rij 2> /dev/null | wc -l", shell=True).decode('utf-8').strip()         
        if (sline == "0"):
            stri="RI not set!"
            tools.error(stri)


    def checkmp2(self):
        sline = subprocess.check_output("sdg ricc2 2> /dev/null | grep mp2 | wc -l", shell=True).decode('utf-8').strip()  
        if (sline == "0"):
            stri="$ricc2 mp2 not set!" 
            tools.error(stri)


    def run_scf_and_w(self):
#       SCF part 
        runscf = True 
        if (os.path.isfile(self.scf_file_name)):
            if (self.check_scf_convergence()):  
               print("Already done")
               runscf = False
        if (runscf == True):
            with open(self.scf_file_name,"w") as f:
                if (self.ncpu > 1):
                    subprocess.run([self.ridft_exec,"-nthreads",f"{self.ncpu}"], stdout=f, stderr=subprocess.DEVNULL)
                else:
                    subprocess.run([self.ridft_exec], stdout=f, stderr=subprocess.DEVNULL)
            if (not self.check_scf_convergence()):
                stri = f"The SCF calculation did not converge.\n Check the {self.scf_file_name} file"
                tools.error(stri)   
#       W calculation
#        this is performed in the temporary directory TMP
        if (os.path.isdir("TMP")): tools.remove_dir("TMP")
        os.mkdir("TMP")
        tools.cp_all_files(".","TMP")
        os.chdir("TMP")
        tools.kdg("scfiterlimit")
        tools.adg("$scfiterlimit 1")
        tools.adg(f"$dft\n   functional {self.wfunc}\n   gridsize 3")
        with open(self.w_file_name,"w") as f:
                if (self.ncpu > 1):
                    subprocess.run([self.ridft_exec,"-nthreads",f"{self.ncpu}"], stdout=f, stderr=subprocess.DEVNULL)
                else:
                    subprocess.run([self.ridft_exec], stdout=f, stderr=subprocess.DEVNULL)
        os.chdir("..")
        shutil.copy(f"TMP/{self.w_file_name}",".")
        tools.remove_dir("TMP")


    def run_mp2(self):
        torun = True
        if (os.path.isfile(self.mp2_file_name)):
           if (self.check_mp2_convergence()):          
               print("Already done")
               torun = False
        if (torun == True): 
           with open(self.mp2_file_name,"w") as f:
                if (self.ncpu > 1):
                    subprocess.run([self.ricc2_exec,"-nthreads",f"{self.ncpu}"], stdout=f, stderr=subprocess.DEVNULL)
                else:
                    subprocess.run([self.ricc2_exec], stdout=f, stderr=subprocess.DEVNULL)
           ch = self.check_mp2_convergence()
           if (not self.check_mp2_convergence()):
              stri = f"The MP2 calculation did not converge.\n Check the {self.mp2_file_name} file"   
              tools.error(stri)  


    def extract_results(self):
#       scf energy ( = HF energy)
        with open("energy","r") as f:
            raw = f.readlines()
        self.scfene = float(raw[len(raw)-2].split()[1])
#       exchange energy, W_inf and W'_inf        
        with open(self.w_file_name,"r") as f:
            wfile_content = f.readlines()
        found = 0
        for i in range(len(wfile_content)):
            line = wfile_content[i]
            if ("exK =" in line):
                self.xene = float(line.split("=",1)[1])
                found = found + 1
            if ("Strong correlation functionals" in line):
                self.wene = float(wfile_content[i+1].split()[2])
                self.w1ene = float(wfile_content[i+2].split()[2])
                found = found + 1
            if (found == 2):
                break                
#       MP2 energy
        with open(self.mp2_file_name,"r") as f:
            mp2file_content = f.readlines()
        for line in mp2file_content:
            if ("MP2 correlation energy (doubles)" in line):
                self.mp2ene = float(line.split()[6])
                break


# for metallic systems print a simple file with E_mp2=-inf
    def print_metallic_mp2_file(self):
        f = open(self.mp2_file_name,"w")
        f.write("MP2 correlation energy (doubles) . . -inf")
        f.close()
