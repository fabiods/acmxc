import os
import tools
import subprocess
import shutil


class crystal:

    def __init__(self,tdir,ncpu,wfunc,baseinput):
        self.ncpu = ncpu
        self.wfunc = wfunc
        self.crystaldir = self.check_crystal_dir(tdir)
        self.set_crystal(self.crystaldir,self.ncpu)
        self.scf_file_name = "scf.out"
        self.w_file_name = "w.out"
        self.mp2_file_name = "mp2.out"
        self.baseinput = baseinput
#
        if (self.wfunc != "pc" and self.wfunc != "hpc"):
            stri="Strong correlation functional " + self.wfunc + " not supported by Crystal"
            tools.error(stri)
#



# check what is the executable directory for crystal
    def check_crystal_dir(self,tdir):
#   if tdir is not given in command line try to set it from the default value ($CRY23_EXEDIR)
        if (tdir == None):
            envdir = os.getenv('CRY23_UTILS')
            if (envdir == None):
                stri="The $CRY23_EXEDIR variable is not set!"
                tools.error(stri)
        tdir = envdir
#   check if tdir is a proper directory
        if (os.path.isdir(tdir) == False):
            stri= tdir+" is not a valid directory for $CRY23_UTILS"
            tools.error(stri)
        return tdir
        

# set crystal environment variables and executables
    def set_crystal(self,crystaldir,ncpu):
        self.crystal_exec = crystaldir + "/runPcry23"
        self.properties_exec = crystaldir + "/runprop23"
        self.cryscor_exec = crystaldir + "/runcryscor"


    def checkscf(self):
        check_file = os.path.isfile(self.baseinput+".d12")
        if (not check_file):
             print(self.baseinput +".d12  not found")
             quit() 
        check_file = os.path.isfile(self.baseinput+".d3")     
        if (not check_file): 
             print(self.baseinput +".d3  not found")
             quit()


    def checkmp2(self):
        check_file = os.path.isfile(self.baseinput+".d4") 
        if (not check_file): 
            print(self.baseinput +".d4  not found")  
            quit()


    def check_scf_convergence(self):
        f = open(self.scf_file_name,"r")
        scf_content = f.readlines()
        f.close()
        ch = False
        for line in scf_content:
            if ("SCF ENDED" in line):
                ch = True
        for line in scf_content:  
            if ("TOO MANY CYCLES" in line):  
                ch = False
        return ch


    def check_mp2_convergence(self):
        f = open(self.mp2_file_name,"r")
        mp2_content = f.readlines()
        f.close()
        ch = False
        for line in mp2_content:
            if ("MP2 CONVERGENCE REACHED" in line):
                ch = True
        return ch


    def run_scf_and_w(self):
        runscf = True
        check_file = os.path.isfile(self.scf_file_name) 
        if (check_file):
            ch = self.check_scf_convergence()
            if (ch):  
               print("already done")
               runscf = False
        if (runscf == True):
            subprocess.run([self.crystal_exec, str(self.ncpu), self.baseinput], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            shutil.move(self.baseinput + ".out", self.scf_file_name)
            ch = self.check_scf_convergence()
            if (ch == False):
                stri = "The SCF calculation did not converge.\n Check the "+self.scf_file_name+" file"                 
                tools.error(stri) 
        print("Running Properties")
        subprocess.run([self.properties_exec, self.baseinput, self.baseinput], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shutil.move(self.baseinput + ".outp", self.w_file_name)


    def run_mp2(self):
        check_file = os.path.isfile(self.mp2_file_name)
        if (check_file): 
           print("already done")
        else:
           with open(self.baseinput +".d12", 'r') as file:
              content = file.read()
              if "UHF" in content:
                  stri = "UHF not implemented in cryscor"
                  tools.error(stri)
              else:            
                subprocess.run([self.cryscor_exec, self.baseinput], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shutil.move(self.baseinput + ".outc", self.mp2_file_name)


    def extract_results(self):
#       scf energy (= HF energy) and exchange energy
        f = open(self.scf_file_name,"r")
        scffile_content = f.readlines()
        f.close()
        found = 0
        for line in scffile_content:
            if ("::: TOTAL   ENERGY" in line):
                self.scfene = float(line.split()[3])
                found = found + 1
            if ("FOCK EXCHANGE ENERGY" in line):
                self.xene = float(line.split()[3])
                found = found + 1
            if (found == 2):
                break
#       W_inf and W'_inf
        f = open(self.w_file_name,"r")
        wfile_content = f.readlines()
        f.close()
        if (self.wfunc == "pc"):
            stri1 = "AC-Winf "
            stri2 = "AC-W1inf "
        elif (self.wfunc == "hpc"):
            stri1 = "AC-Winf-HPC"
            stri2 = "AC-W1inf-HPC"
        found = 0
        for line in wfile_content:
            if (stri1 in line):
                self.wene = float(line.split()[1])
                found = found + 1
            if (stri2 in line):
                self.w1ene = float(line.split()[1])
                found = found + 1
            if (found == 2):
                break
#       MP2 energy
        f = open(self.mp2_file_name,"r")
        mp2file_content = f.readlines()
        f.close()
        for line in mp2file_content:
            if ("MP2 CORRELATION ENERGY:" in line):
                self.mp2ene = float(line.split()[4])
                break


# for metallic systems print a simple file with E_mp2=-inf
    def print_metallic_mp2_file(self):
        f = open(self.mp2_file_name,"w")
        f.write("MP2 CORRELATION ENERGY: . -inf")
        f.close()
