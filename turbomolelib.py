import os
import tools
import subprocess
import shutil


class turbomole:

    def __init__(self,tdir,ncpu,wfunc,metal_mode,path):
        self.ncpu = ncpu
        self.wfunc = wfunc
        self.tdir = self.check_turbodir(tdir)
        self.set_turbomole()
        self.check_input(metal_mode,path)
        self.scf_file_name = "scf.out"
        self.w_file_name = "w.out"
        self.mp2_file_name = "mp2.out"


# check the value of TURBODIR and set it if not defined
#   if tdir was not given in command line set it to the default value ($TURBODIR)
    def check_turbodir(self,tdir):
        if (tdir == None):
            envtdir=os.getenv('TURBODIR')
            if (envtdir == None):
                tools.error("The $TURBODIR variable is not set!")
            tdir = envtdir
        return tdir


# set turbomole environment variables and executables paths
    def set_turbomole(self):
        para_arch = "SMP" if (self.ncpu > 1) else ""
        os.putenv("PARA_ARCH",para_arch)
        os.putenv("SMPCPUS",str(self.ncpu))
        sname = subprocess.check_output("sysname", shell=True).decode('utf-8').strip()
        ssname = subprocess.check_output("sysname -s", shell=True).decode().strip()
        if (self.ncpu > 1):
            path = f"{self.tdir}/scripts:{self.tdir}/bin/{sname}:{self.tdir}/bin/{ssname}:/bin:/usr/bin"
        else:
            path = f"{self.tdir}/scripts:{self.tdir}/bin/{sname}:/bin:/usr/bin"
        os.putenv("PATH",path)
        if (self.ncpu > 1):
            self.ridft_exec = f"{self.tdir}/bin/{sname}/ridft_smp"
            self.ricc2_exec = f"{self.tdir}/bin/{sname}/ricc2_smp"
        else:
            self.ridft_exec = f"{self.tdir}/bin/{sname}/ridft"
            self.ricc2_exec = f"{self.tdir}/bin/{sname}/ricc2"


    def check_input(self,metal_mode,path):
        control_file_path = f"{path}/control"        
        if (not os.path.isfile(control_file_path)):
            tools.error("control file not found!")
        with open(control_file_path,"r") as f:
            control_content = f.read()
            if "$rij" not in control_content:
                tools.error("RI option not set in control file")
            if (not metal_mode):
                if "$ricc2" not in control_content:
                    tools.error("$ricc2 datagroup not set in control file")
                if "mp2" not in control_content:
                    tools.error("MP2 option not set in control file")
                

    def check_scf_convergence(self):
        with open(self.scf_file_name,"r") as f:
            scf_content = f.readlines()
        return any("convergence criteria satisfied" in line for line in scf_content)


    def check_mp2_convergence(self):
        with open(self.mp2_file_name,"r") as f:
            mp2_content = f.readlines()
        return any("ricc2 : all done" in line for line in mp2_content)


    def run_ridft(self,f,rerun=False,damp=0.0):
        if (rerun):
            tools.kdg("restart")
            tools.kdg("scfdamp")
            tools.adg(f"$scfdamp   start={damp:.3f}  step=0.050  min=0.100")
            tools.kdg("scfiterlimit")
            tools.adg("$scfiterlimit 200")
        if (self.ncpu > 1):
            subprocess.run([self.ridft_exec,"-nthreads",f"{self.ncpu}"], stdout=f, stderr=subprocess.DEVNULL)
        else:
            subprocess.run([self.ridft_exec], stdout=f, stderr=subprocess.DEVNULL)

            
    def run_scf_and_w(self):
#       do nothing if the SCF calculation is already there
        if (os.path.isfile(self.scf_file_name) and self.check_scf_convergence()):  
            print("Already done")
        else:
#       SCF part
            with open(self.scf_file_name,"w") as f:
                self.run_ridft(f,False)
                if (not self.check_scf_convergence()):
                    self.run_ridft(f,True,damp=3)
                    if (not self.check_scf_convergence()):
                        self.run_ridft(f,True,damp=16)
                        if (not self.check_scf_convergence()):
                            self.run_ridft(f,True,damp=12)
                            if (not self.check_scf_convergence()):
                                tools.error(f"The SCF calculation did not converge.\n Check the {self.scf_file_name} file") 
#       W calculation
#        this is performed in the temporary directory TMP
        if (os.path.isdir("TMP")): shutil.rmtree("TMP") #tools.remove_dir("TMP")
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
        shutil.rmtree("TMP")# tools.remove_dir("TMP")


    def run_mp2(self):
#       do nothing if the MP2 calculation is already there
        if (os.path.isfile(self.mp2_file_name)):
           if (self.check_mp2_convergence()):          
               print("Already done")
               return
#       MP2 calculation
        with open(self.mp2_file_name,"w") as f:
            if (self.ncpu > 1):
                subprocess.run([self.ricc2_exec,"-nthreads",f"{self.ncpu}"], stdout=f, stderr=subprocess.DEVNULL)
            else:
                subprocess.run([self.ricc2_exec], stdout=f, stderr=subprocess.DEVNULL)
        if (not self.check_mp2_convergence()):
            tools.error(f"The MP2 calculation did not converge.\n Check the {self.mp2_file_name} file")


# for metallic systems print a simple file with E_mp2=-inf
    def print_metallic_mp2_file(self):
        with open(self.mp2_file_name,"w") as f:
            f.write("MP2 correlation energy (doubles) . . -inf")


    def extract_results(self):
#       scf energy ( = HF energy)
        with open("energy","r") as f:
            raw = f.readlines()
        self.scfene = float(raw[len(raw)-2].split()[1])
#       exchange energy, W_inf and W'_inf        
        with open(self.w_file_name,"r") as f:
            wfile_content = f.readlines()
            found = 0
            for i, line in enumerate(wfile_content):
                if ("exK =" in line):
                    self.xene = float(line.split("=", 1)[1])
                    found += 1
                elif ("Strong correlation functionals" in line):
                    self.wene = float(wfile_content[i + 1].split()[2])
                    self.w1ene = float(wfile_content[i + 2].split()[2])
                    found += 1
                if (found == 2):
                    break                
#       MP2 energy
        with open(self.mp2_file_name,"r") as f:
            mp2file_content = f.readlines()
            for line in mp2file_content:
                if ("MP2 correlation energy (doubles)" in line):
                    self.mp2ene = float(line.split()[6])
                    break
