acmxcturbotest.py is an utility script to run test calculations with acmxc and TURBOMOLE.

USAGE:
acmxc_test.py [-h] -i <string> [-a <string>] [-b <string>] [--no-bsse]
                     [-f <string>] [-w <string>] [-n <int>]

PREREQUISITE: Input file with all informations about the test to be run and a running acmxc script.

optional arguments:
  -h, --help            show this help message and exit
  -i <string>, --input <string>
                        Input file name (full path)
  -a <string>, --acmxc-exe <string>
                        Full path of the acmxc script
  -b <string>, --basis <string>
                        Basis set to employ
  --no-bsse             Do not perform counterpois correction for BSSE
                        (default: perform)
  -f <string>, --formula <string>
                        Formula to be used. Options: isi, revisi, genisi, spl,
                        lb, spl2, mpacf1, dpi, mp2
  -w <string>, -wfunc <string>
                        W_inf functional. Options: pc, hpc, mpc
  -n <int>, -nthreads <int>
                        Number of threads to use (default: 1)

INPUT FILE
The input file is a csv file containing all the information about the systems to be tested.
It has this general structure:
system name ; reference energy (kcal/mol) ; number of fragments ; stoichiometric coefficients ; charges ; fragments atoms ; coordinates

Some input files for standard tests are already available here
