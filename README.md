*********************** acmxc manual *************************

acmxc is a script to perform calculations using Adiabatic Connection
Models (ACMs) for the correlation energy. It drives electronic
structure calculations from several codes and computes total
energies.
Actually the following codes are supported: TURBOMOLE, Crystal.


== PREREQUISITES ==

To use acmxc the following resources are needed:
 + python interpreter (version 3 or higher)
 + at least one of the following codes:
   - TURBOMOLE (version 7.7 or higher)
   - Crystal (version 3.3 or higher including cryscor)

Note that for calculations with Crystal a development version of the
"properties" executable is required. This can be obtained from the
developers.


== USAGE ==

\* PREPARATION  
To perform calculations with acmxc set up a valid input file for the
program you are going to use. The input file must define a
Hartree-Fock calculation as well a MP2 calculation as usual for the
code of choice. In particular: 

- for TURBOMOLE the RI approximation must be used (the ridft code is
employed) and the control file must contain the data group
$ricc2
 mp2
as well as the proper auxbasis for ricc2 calculations.

- for Crystal <file_name>.d12, <file_name>.d3, and <file_name>.d4
files must be prepared. The <file_name>.d12 must contain the keyword EXCHGENE.


\* RUNNING  
To run the script use:

acmxc -p <program> [ -i <file_name> ] [ other options ]

The -i option is required only if \<progam> == crystal

If you consider systems with vanishing gap (e.g. periodic metals) 
use the --metal option (see below)


\* OPTIONS  
The following options are available:

  -p \<string>, --prog \<string>, --program \<string>
			Program to use. Possible options:
			turbomole
			crystal

  -f \<string>, --formula \<string>
                        ACM formula to be used. 
			Possible options: 
			isi
                        revisi 
			genisi 
			spl
			lb
			dpi
			(default: isi)

  -w \<string>, -wfunc \<string>
                        W_infinity functional to use. 
			Possible options: pc, hpc, mpc
			(default: hpc)

  -n \<int>, -nthreads \<int>
                        Number of threads to use (default: 1)

  -d \<string>, -dir \<string>
                        Base path of \<program> .
			(default=set from environment variable)

  -i \<string>, --input \<string>
                        Specification of \<file_name>
			This is required (and mandatory!) only for
			crystal.
			\<file_name> is not including the .d12 .d3 and
			.d4 extensions

  --metal               Sets E_mp2=-inf. This must be used for
    			calculations of systems with a vanishing gap,
    			e.g. metallic solids
			(default=False)




== EXAMPLES ==

Here are examples of input and output files for simulations using
acmxc together with TURBOMOLE and Crystal

\* TURBOMOLE

This examples runs: acmxc -p turbomole -w pc

- Sample control file -  
```
$title  
$symmetry cs  
$coord  natoms=     6  
   -3.12829134861628     -0.23300394043326      0.00000000000000      o  
    2.35500003894170      0.19405350461602      0.00000000000000      o  
   -1.33053765694300      0.06034211441874      0.00000000000000      h  
   -3.85253284374873      1.42432982102036      0.00000000000000      h  
    2.97818090518316     -0.72286074981094     -1.43347299098969      h  
    2.97818090518316     -0.72286074981094      1.43347299098969      h  
$optimize  
 internal   off  
 redundant  off  
 cartesian  on  
$atoms   
    basis =def-SV(P)  
    cbas  =def-SV(P)  
    jbas  =def-SV(P)  
$basis  
*  
o def-SV(P)  
# o     (7s4p1d) / [3s2p1d]     {511/31/1}  
*  
   5  s  
  2266.1767785     -0.53431809926E-02  
  340.87010191     -0.39890039230E-01  
  77.363135167     -0.17853911985  
  21.479644940     -0.46427684959  
  6.6589433124     -0.44309745172  
   1  s  
 0.80975975668       1.0000000000  
   1  s  
 0.25530772234       1.0000000000  
   3  p  
  17.721504317      0.43394573193E-01  
  3.8635505440      0.23094120765  
  1.0480920883      0.51375311064  
   1  p  
 0.27641544411       1.0000000000  
   1  d  
  1.2000000000       1.0000000000  
*  
h def-SV(P)  
# h     (4s) / [2s]     {31}  
*  
   3  s  
  13.010701000      0.19682158000E-01  
  1.9622572000      0.13796524000  
 0.44453796000      0.47831935000  
   1  s  
 0.12194962000       1.0000000000  
*  
$jbas  
*  
o def-SV(P)  
# o     (8s3p3d1f) / [6s3p3d1f]     {311111/111/111/1}  
*  
   3  s  
  896.10357000      0.59760749700  
  269.72523200       1.5358077900  
  85.615077000       4.0470231300  
   1  s  
  28.445035000       3.4984208300  
   1  s  
  9.8069810000     -0.24387498700E-01  
   1  s  
  3.4747220000      0.32147717800  
   1  s  
  1.2519210000       1.1625987000  
   1  s  
 0.45361300000      0.25268306900  
   1  p  
 0.61470886295     -0.85578439300E-01  
   1  p  
  1.4753012711      0.41799959400E-01  
   1  p  
  3.6956296840     -0.58551078600E-01  
   1  d  
  7.6526720000      0.88298462700E-01  
   1  d  
  2.2178680000      0.11926244900 
   1  d  
 0.68233700000      0.44873891700E-01  
   1  f  
  2.1917808219       1.0000000000  
*  
h def-SV(P)  
# h     (4s2p) / [2s1p]     {31/2}  
*  
   3  s  
  9.3081300000      0.34466183000E-01  
  2.3067180000      0.12253379600  
 0.75201200000      0.18250021100  
   1  s  
 0.27397800000      0.22150547900E-01  
   2  p  
  2.0327040000      0.29513659100E-01  
 0.79025200000      0.32755872800E-01  
*  
$cbas  
*  
o def-SV(P)  
# o     (8s6p5d3f) / [6s5p4d1f]     {311111/21111/2111/3}  
*  
   3  s  
  364.91291000      0.58060367000  
  77.387094000       1.4017984900  
  24.301706000      0.34994578000  
   1  s  
  8.4369545000       1.0000000000  
   1  s  
  3.1527941000       1.0000000000  
   1  s  
  1.5775430000       1.0000000000  
   1  s  
 0.78178244000       1.0000000000  
   1  s  
 0.31652679000       1.0000000000  
   2  p  
  56.735948000       1.0602441000  
  14.997217000       1.2003825800  
   1  p  
  5.6428116000       1.0000000000  
   1  p  
  2.4069219800       1.0000000000  
   1  p  
  1.0264059600       1.0000000000  
   1  p  
 0.43769977000       1.0000000000  
   2  d  
  12.446821000       1.1371699500  
  6.1216917000      0.77017590000  
   1  d  
  2.7102949000       1.0000000000  
   1  d  
  1.1524061000       1.0000000000  
   1  d  
 0.41386174000       1.0000000000  
   3  f  
  4.7793539000      0.25251741000  
  2.3204642000       1.7867127800  
  1.0912804000      0.32923623000  
*  
h def-SV(P)  
# h     (4s3p2d) / [3s2p1d]     {211/21/2}  
*  
   2  s  
  9.3352160900      0.64609379000  
  1.8611070400       1.3700524100  
   1  s  
 0.59512466000       1.0000000000  
   1  s  
 0.26448099000       1.0000000000  
   2  p  
  2.4524982100      0.13284956000  
  1.3540383000       1.4527621500  
   1  p  
 0.59522394000       1.0000000000  
   2  d  
  1.5816376600       1.4936739700  
 0.62743960000     -0.10706900000E-01  
*  
$scfmo   expanded   format(4d20.14)  
     1  a'     eigenvalue=-.20669566707399D+02   nsaos=26  
0.89592777536282D+00-.37746871216853D-010.82359398867189D-02-.18838208095188D-02  
-.32633537534192D-02-.80911858507774D-03-.16638501256839D-020.11520463906557D-04  
-.29431331194870D-06-.11767401985058D-04-.41639988136830D+000.17046761531848D-01  
-.36721906923563D-020.24083191328453D-02-.17089233499919D-020.11956812476660D-02  
-.84698608342965D-03-.33098874774072D-05-.69436992800212D-050.16034218437999D-04  
0.68938599052160D-020.41246634196805D-020.62272784190941D-020.41850760571612D-02  
-.50527649599361D-02-.32682935070380D-02  
     2  a'     eigenvalue=-.20669385356500D+02   nsaos=26  
-.41619460496663D+000.17801765575573D-01-.48843583562648D-020.10769979532047D-02  
0.14232328555636D-02-.57085945076886D-040.69813968866486D-030.50327587462838D-04  
-.16182736325514D-04-.63884931766146D-04-.89591426459364D+000.37758776487991D-01   
-.85394620243728D-020.13120101271289D-02-.28798764523581D-020.11655918020404D-02  
-.14837941101802D-020.19258714233204D-040.11836322380318D-05-.38603072879326D-04  
-.25518166995281D-02-.51844633647526D-03-.27010310605261D-02-.21508875246893D-02  
-.83491092920725D-02-.56960502535459D-02  
     3  a'     eigenvalue=-.12627667073693D+01   nsaos=26  
0.20253470122685D+000.40536978057965D+000.28589629677997D+00-.61821335364015D-02  
-.10256541420150D-010.11360043724909D-02-.32753764711121D-020.21263042673422D-04  
0.11916582976185D-030.10746242220775D-030.20829878007287D+000.41795254437714D+00  
0.29067361641881D+00-.34892207316513D-020.94635144285278D-02-.43590608477584D-02  
0.34322456340511D-02-.17697761210273D-030.33358002850413D-040.17258575015216D-03  
0.45632916110649D-010.20168670131191D-010.38566904517724D-010.25420106031872D-01  
0.55060652052863D-010.35173108804214D-01  
     4  a'     eigenvalue=-.12556205919137D+01   nsaos=26  
0.21148266548186D+000.42661842706784D+000.29045780292400D+00-.62839930656498D-02  
-.11891215059861D-01-.22640579741902D-02-.38324643468915D-020.16516946220181D-03  
0.12000636114082D-05-.84156981620589D-04-.20528349927845D+00-.41288043395960D+00  
-.28373363985113D+000.78445678611539D-02-.11070388358216D-010.42301036815215D-02  
-.32667149424160D-020.16890645609628D-03-.91419346264089D-04-.22091708144688D-03  
0.38408571926868D-010.24368392544130D-010.45579862626715D-010.28172817182510D-01  
-.61922408356044D-01-.39376088617062D-01  
     5  a'     eigenvalue=-.68912974989020D+00   nsaos=26  
0.45133201161795D-020.11161989201620D-010.80317593973680D-02-.45015560923525D+00  
0.21130871934492D+00-.30264166621477D+000.14226400466188D+00-.38135947932689D-05  
-.76049762754573D-05-.11306784710499D-040.30099321294669D-020.24351024982122D-02  
0.18556306994215D-020.20691961306754D+00-.24923724592191D-010.13911688957431D+00  
-.16741046304477D-01-.11072010819357D-05-.35750057397583D-050.44798278006270D-05  
-.16316085116355D+00-.14033823428287D+000.15189081497726D+000.12986260918289D+00  
0.30886598418318D-010.26444221734837D-01  
     6  a'     eigenvalue=-.64500687405146D+00   nsaos=26  
-.30665479670442D-01-.83293556047549D-01-.57262734443865D-010.11130487672951D+00  
0.49990759739691D+000.74372251197687D-010.33573250998136D+00-.29301764237163D-04  
-.12306268264576D-04-.44014606520610D-070.16443488879855D-010.46772529876240D-01  
0.31908680709334D-01-.28061804065854D+000.25614551712710D+00-.18857895773284D+00  
0.17192524483154D+00-.24644736763941D-040.15970056708946D-040.25484703421055D-04  
0.24480270302056D-010.23217672481415D-010.72222433566049D-010.63794831899428D-01  
-.47116370101394D-01-.42035591845854D-01  
     7  a'     eigenvalue=-.63313125059103D+00   nsaos=26  
0.13971123238293D-010.38321752105925D-010.27307918338473D-01-.18525853080654D+00  
-.27562897746970D+00-.12413429153166D+00-.18519962196652D+00-.96282906407013D-07  
0.15054985770758D-040.86747241582136D-050.26718348607073D-010.72077519597776D-01  
0.49913779678554D-01-.42064497315118D-010.56713344768080D+00-.28452395920963D-01  
0.38125218504571D+00-.31602107695737D-040.12055812567863D-040.26455766945557D-04  
-.23421592610155D-01-.22174889628051D-01-.23221759646672D-01-.20463156078256D-01  
-.55396041652226D-01-.49567168352269D-01  
     8  a'     eigenvalue=-.61480547564267D+00   nsaos=26  
-.78174370205223D-03-.51021257371509D-02-.36165837941334D-020.28968361393378D+00  
0.14540162199952D+000.19491546918185D+000.97898334643268D-01-.73137304386611D-05  
0.17391312691203D-050.46066490897950D-05-.10233159879893D-01-.26138867093688D-01  
-.17904281700049D-010.56627693630834D+000.22050457910791D+000.38111478354968D+00  
0.14870318374022D+000.82558586201518D-05-.69774929931325D-050.22105308678486D-05  
0.28933949034801D-010.25058375575581D-01-.10722096644403D-01-.90766215323571D-02  
0.13499103850064D-010.12471234425078D-01  
     1  a"     eigenvalue=-.68435944524169D+00   nsaos=10  
-.18832538375882D-01-.12694106460298D-01-.17887969612720D-05-.42701331021144D-06  
-.53933344881518D+00-.36287112363698D+00-.12519944189883D-040.18578310853218D-04  
0.23096289786306D+000.19768846301673D+00  
     2  a"     eigenvalue=-.62270499585047D+00   nsaos=10  
0.68500222605228D+000.46122550320110D+00-.29231444772550D-06-.27151743878940D-08  
-.18608953452007D-01-.12486453206017D-010.18489817498954D-05-.92396319689806D-05  
0.62464155796151D-020.52414471130059D-02  
$closed shells  
 a'      1-8                                    ( 2 )  
 a"      1-2                                    ( 2 )  
$scfiterlimit       30  
$scfconv        7  
$scfdamp   start=0.300  step=0.050  min=0.100  
$scfdump  
$scfdiis  
$maxcor    500 MiB  per_core  
$scforbitalshift  automatic=.1  
$energy    file=energy  
$grad    file=gradient  
$ricore    1000  
$rij  
$marij  
$denconv     0.10000000E-06  
$cbas    file=auxbasis  
$rundimensions  
   natoms=6  
$last step     define  
$ricc2  
  mp2  
$end  
```

-- Output file --
```

             +-----------------------------+
             |            ACMxc            |
             | Perform HF-ACM calculations |
             |                             |
             +-----------------------------+

04.01.2024 - 11:41:36

Program:  turbomole
Program's path:  /home/turbo/GIT/turbomole
N. cpu:  1
ACM model:  isi
  Ref: Phys. Rev. Lett. 84, 5070 (2000)
W functional:  pc
  Ref: Phys. Rev. A 62, 012502 (2000)

Running SCF calculation...
Running MP2 calculation...

 SCF energy:           -151.8867154974
 HF-exchange energy:    -17.8916221575
 W_inf energy:          -29.2328449451
 W1_inf energy:          28.4040170721
 MP2 corr. energy:       -0.3826886727

RESULTS:
 Correlation energy:             -0.3599516958
 Exchange-correlation energy:   -18.2515738533
 Total energy:                 -152.2466671932
```


\* Crystal

This examples runs: acmxc -p crystal -i h2o -f spl

- Sample input files -

\>> h2o.d12 <<
```
water molecule
MOLECULE
1
3
8 0. 0. 0.137
1 0. 0.770 -0.547
1 0. -0.770 -0.547
BASISSET
cc-pvdz
EXCHGENE
END
```

\>> h2o.d3 <<
```
EDFT
END
NEWK
1 0
LOCALWF
VALENCE
END
END
```

\>> h2o.d4 <<
```
FITBASIS
PG-VTZ
END
```

-- Output file --
```

             +-----------------------------+
             |            ACMxc            |
             | Perform HF-ACM calculations |
             |                             |
             +-----------------------------+

04.01.2024 - 11:49:27

Program:  crystal
Input file:  h2o
Program's path:  /home/atom/ATOMSOFT/CRYSTAL/NEW/utils23
N. cpu:  1
ACM model:  spl
  Ref: Phys. Rev. A 59, 51 (1999)
W functional:  hpc
  Ref: J. Chem. Theory Comput. 18, 5936 (2022)

Running SCF calculation...
Running Properties
Running MP2 calculation...

 SCF energy:            -76.0137252840
 HF-exchange energy:     -8.8999827429
 W_inf energy:          -14.5595607539
 W1_inf energy:          14.0932358327
 MP2 corr. energy:       -0.1320784918

RESULTS:
 Correlation energy:             -0.1262515136
 Exchange-correlation energy:    -9.0262342565
 Total energy:                  -76.1399767976
```
