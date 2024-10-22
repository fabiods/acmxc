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

Some input files for standard tests are already available here as *.info files:
revised ae6 (atomization energies)    R. Haunschild, W. Klopper, Theor. Chem. Acc. 131, 1112 (2012)
atomic ip   (ionization potentials)   from L. Goerigk and S. Grimme in  J. Chem. Theory Comput. 6, 107 (2010)
hb6         (hydrogen-bond)           Y. Zhao, D. G. Truhlar, JCTC 1, 415 (2005)
di6         (dipole-dipole interact)  Y. Zhao, D. G. Truhlar, JCTC 1, 415 (2005)
ct7         (charge transfer complex) Y. Zhao, D. G. Truhlar, JCTC 1, 415 (2005)
pp5         (pi-pi* complexes)        Y. Zhao, D. G. Truhlar, JCTC 1, 415 (2005)
wi7         (weak interaction)        Y. Zhao, D. G. Truhlar, JCTC 1, 415 (2005)
s22         (non covalent interact)   T. Takatani, E. G. Hohenstein, M. Malagoli, M. S. Marshall, C. D. Sherrill,  J. Chem. Phys. 132, 144104 (2010)
s66         (non covalent interact)   J. Řezáč, K. E. Riley†, P. Hobza, J. Chem. Theory Comput 7, 3466 (2011)
a24         (non covalent interact)   J. Řezáč, P. Hobza, J. Chem. Theory Comput. 9, 2151 (2013)

