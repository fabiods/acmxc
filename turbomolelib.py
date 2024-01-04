import os
import tools
import subprocess
import shutil


class turbomole:

    def __init__(self,tdir,ncpu,wfunc):
        self.ncpu = ncpu
        self.wfunc = wfunc
        self.turbodir = self.check_turbodir(tdir)
        self.set_turbomole(self.turbodir,self.ncpu)
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
            stri= tdir+" is not a valid directory for $TURBODIR"
            tools.error(stri)
        return tdir


# set turbomole environment variables and executables paths
    def set_turbomole(self,tdir,ncpu):
        if (ncpu > 1):
            para_arch = "SMP"
            os.putenv("PARA_ARCH",para_arch)
            os.putenv("SMPCPUS",str(ncpu))
            sname = subprocess.check_output("sysname", shell=True).decode('utf-8').strip()
            ssname = subprocess.check_output("sysname -s", shell=True).decode().strip()
            path = tdir+"/scripts:"+tdir+"/bin/"+sname+":"+tdir+"/bin/"+ssname+":/bin:/usr/bin"
            os.putenv("PATH",path)
            self.ridft_exec = tdir+"/bin/"+sname+"/ridft_smp -nthreads "+str(ncpu)
            self.ricc2_exec = tdir+"/bin/"+sname+"/ricc2_smp -nthreads "+str(ncpu)
        else:
            para_arch = ""
            os.putenv("PARA_ARCH",para_arch)
            os.putenv("SMPCPUS","1")
            sname = subprocess.check_output("sysname", shell=True).decode('utf-8').strip()
            path = tdir+"/scripts:"+tdir+"/bin/"+sname+":/bin:/usr/bin"
            os.putenv("PATH",path)
            self.ridft_exec = tdir+"/bin/"+sname+"/ridft"
            self.ricc2_exec = tdir+"/bin/"+sname+"/ricc2"


    def check_scf_convergence(self):
        f = open(self.scf_file_name,"r")
        scf_content = f.readlines()
        f.close()
        ch = False
        for line in scf_content:
            if ("convergence criteria satisfied" in line):
                ch = True
        return ch

    def check_mp2_convergence(self):
        f = open(self.mp2_file_name,"r")
        mp2_content = f.readlines()
        f.close()
        ch = False
        for line in mp2_content:
            if ("ricc2 ended normally" in line):
                ch = True
        return ch
 

    def checkscf(self):
        check_file = os.path.isfile("control")
        if (not check_file):
             print("control find not found")
             quit()            
        sline = subprocess.check_output("sdg rij 2> /dev/null | wc -l", shell=True).decode('utf-8').strip()         
        if (sline == "0"):
             print("RI not set")
             quit()


    def checkmp2(self):
        sline = subprocess.check_output("sdg ricc2 2> /dev/null | grep mp2 | wc -l", shell=True).decode('utf-8').strip()  
        if (sline == "0"):   
             print("ricc2 mp2 not set")  
             quit()


    def run_scf_and_w(self):
#       SCF part 
        runscf = True
        check_file = os.path.isfile(self.scf_file_name) 
        if (check_file):
            ch = self.check_scf_convergence()
            if (ch):  
               print("already done")
               runscf = False
        if (runscf == True):
            os.system(self.ridft_exec+" &> "+self.scf_file_name)
            ch = self.check_scf_convergence()
            if (ch == False):
                stri = "The SCF calculation did not converge.\n Check the "+self.scf_file_name+" file"                 
                tools.error(stri)   
#       W calculation
#        this is performed in the temporary direcotry TMP
        if (os.path.isdir("TMP")): tools.remove_dir("TMP")
        os.mkdir("TMP")
        tools.cp_all_files(".","TMP")
        os.chdir("TMP")
        tools.kdg("scfiterlimit")
        tools.adg("$scfiterlimit 1")
        tools.adg("$dft\n   functional "+self.wfunc+"\n   gridsize 3")
        os.system(self.ridft_exec+" &> "+self.w_file_name)
        os.chdir("..")
        shutil.copy("TMP/"+self.w_file_name,".")
        tools.remove_dir("TMP")


    def run_mp2(self):
        torun = True
        check_file=os.path.isfile(self.mp2_file_name)
        if (check_file):
           ch = self.check_mp2_convergence()   
           if (ch == True):          
               print("already done")
               torun = False
        if (torun == True): 
           os.system(self.ricc2_exec+" &> "+self.mp2_file_name)
           ch = self.check_mp2_convergence()
           if (ch == False):
              stri = "The MP2 calculation did not converge.\n Check the "+self.mp2_file_name+" file"   
              tools.error(stri)  


    def extract_results(self):
#       scf energy ( = HF energy)
        f = open("energy","r")
        raw = f.readlines()
        f.close()
        self.scfene = float(raw[len(raw)-2].split()[1])
#       exchange energy, W_inf and W'_inf        
        f = open(self.w_file_name,"r")
        wfile_content = f.readlines()
        f.close()
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
        f = open(self.mp2_file_name,"r")
        mp2file_content = f.readlines()
        f.close()
        for line in mp2file_content:
            if ("MP2 correlation energy (doubles)" in line):
                self.mp2ene = float(line.split()[6])
                break


# for metallic systems print a simple file with E_mp2=-inf
    def print_metallic_mp2_file(self):
        f = open(self.mp2_file_name,"w")
        f.write("MP2 correlation energy (doubles) . . -inf")
        f.close()
