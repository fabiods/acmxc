import argparse
#import turbomolelib
import sys
import shutil
import os
from datetime import datetime
import acmlib


# manage the command line options
def manage_options():
    parser = argparse.ArgumentParser(description='PREREQUISITE: Set up a valid input file to run an ACM calculation with TURBOMOLE or CRYSTAL, then run the script.')
#
    parser.add_argument("-p","--prog","--program",
                        required=True,
                        choices=["turbomole","crystal"],
                        metavar="<string>")
#
    parser.add_argument("-f","--formula",
                        default="isi",
                        choices=["isi","revisi","spl","lb","genisi","dpi"],
                        help="Formula to be used. Options: isi, revisi, genisi, spl, lb ,dpi",
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
    parser.add_argument("-d","-dir",
                        default=None,
                        help="Base path of <program> (default=set from environment variable)",
                        metavar="<string>")
#
    parser.add_argument("-i","--input",
                        default="input",
                        help="root of the crystal file name (not including the .d12 .d3 and .d4 extensions)",
                        metavar="<string>")

#
    parser.add_argument("--metal",
                        action='store_true',
                        default=False,
                        help="Sets E_mp2=-inf. Use for calculations of systems with vanishing gap (default=False)")
#
    options = vars(parser.parse_args())
#
#
    return options
    

# print an error message and exit
def error(stri):
    print()
    print("ERROR!!")
    print(stri)
    print()
    sys.exit(1)


# delete a data group from turbomole control file
def kdg(datagroup):
    stri = "$"+datagroup
    f = open("control","r")
    control_content = f.readlines()
    f.close()
    f = open("control.tmp","w")
    i = 0
    while (i < len(control_content)):
        line = control_content[i]
        if (stri not in line):
            f.write(line)
#            print(line)
            i = i + 1
        else:
            j = 1
            while (i+j < len(control_content)):
                bline = control_content[i+j]
                if ("$" in bline):
                    break
                j = j + 1
            i = i + j
    f.close()
    shutil.move("control.tmp","control")
                

# add a data group to turbomole control file
def adg(datagroup):
    stri = datagroup + "\n"
    kdg("end")
    f = open("control","a")
    f.write(stri)
    f.write("$end\n")
    f.close()


# copy all file (and only files) from one directory to another
def cp_all_files(from_dir,to_dir):
    for ff in os.listdir(from_dir):
        file_full_name = os.path.join(from_dir, ff)
        if os.path.isfile(file_full_name):
            shutil.copy(file_full_name, to_dir)

# remove a non empty directory
def remove_dir(dire):
    for ff in os.listdir(dire):
        file_full_name = os.path.join(dire, ff)
        if os.path.isfile(file_full_name):
            os.remove(file_full_name)
    os.rmdir(dire)


# print header
def print_header():
    data = datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
    print ("")
    print("             +-----------------------------+")
    print("             |            ACMxc            |")
    print("             | Perform HF-ACM calculations |")
    print("             |                             |")
    print("             +-----------------------------+")
    print("")
    print(data)


# print a summary of the options
def print_options(options,tdir):
    print("")
    print("Program: ",options["prog"])
    if (options["prog"] == "crystal"):
        print ("Input file: ",options["input"])
    print("Program's path: ",tdir)
    print("N. cpu: ",options["n"])
    print("ACM model: ",options["formula"])
    acmlib.print_refs(options["formula"])
    print("W functional: ",options["w"])
    print_w_refs(options["w"])
    print("")


def print_w_refs(wfunc):
    if (wfunc == "pc"):
        refstri = "Phys. Rev. A 62, 012502 (2000)"
    elif (wfunc == "hpc"):
        refstri = "J. Chem. Theory Comput. 18, 5936 (2022)"
    elif (wfunc == "mpc"):
        refstri = "Phys. Rev. B 99, 085117 (2019)"
    stri = "  Ref: " + refstri
    print(stri)
