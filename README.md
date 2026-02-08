# OPATCH_DIFF – Comparing Oracle OPatch Output

Version: 1.1

This repository contains a Python script *opatch_diff.py* for comparing two Oracle 
Database OPatch outputs.

Both `opatch lspatch` and `opatch lsinventory` outputs are supported. The supported OPatch output sources are:
- A file name for already saved OPatch output.
- ORACLE_HOME path, so that the *opatch_diff.py* can run
`$ORACLE_HOME/OPatch/opatch` command directly   .

## Usage

```
./opatch_diff.py -h
usage: opatch_diff.py [-h] [-s] [-v] [--lspatches] [--lsinventory]
                      [-oh ORACLE_HOME] [-oh1 ORACLE_HOME1]
                      [-oh2 ORACLE_HOME2] [-f1 FILE1] [-f2 FILE2]
                      [-out PATCH_OUTPUT] [-out1 PATCH_OUTPUT1]
                      [-out2 PATCH_OUTPUT2]
                      [first_file] [second_file]

Compare two Oracle OPatch inventories.

positional arguments:
  first_file            first OPatch output file
  second_file           second OPatch output file

options:
  -h, --help            show this help message and exit
  -s, --short           print less details (hide extra lines)
  -v, --version         show program's version number and exit
  --lspatches           run 'opatch lspatches'
  --lsinventory         run 'opatch lsinventory'
  -oh ORACLE_HOME, --oracle_home ORACLE_HOME
                        ORACLE_HOME directory
  -oh1 ORACLE_HOME1, --oracle_home1 ORACLE_HOME1
                        first ORACLE_HOME directory
  -oh2 ORACLE_HOME2, --oracle_home2 ORACLE_HOME2
                        second ORACLE_HOME directory
  -f1 FILE1, --file1 FILE1
                        first OPatch output file
  -f2 FILE2, --file2 FILE2
                        second OPatch output file
  -out PATCH_OUTPUT, --patch_output PATCH_OUTPUT
                        save OPatch output to file
  -out1 PATCH_OUTPUT1, --patch_output1 PATCH_OUTPUT1
                        save first OPatch output to file
  -out2 PATCH_OUTPUT2, --patch_output2 PATCH_OUTPUT2
                        save second OPatch output to file
  -ru, --release_update
                        only print Release Update version
  --oratab              use /etc/oratab file to find ORACLE_HOME directories
  
=> Created by Andrej Simon, Oracle CSS Germany (https://github.com/asimondev)
```

## Examples

### Comparing Two OPatch Output Files

The `opatch lspatches` output was saved to files. You want to compare these 
files to find the differences in the installed patches.

```
./opatch_diff.py opatch_lspatches_12.out opatch_lspatches_13.out
Reading patches from 'opatch lspatches' opatch_lspatches_12.out...
Reading patches from 'opatch lspatches' opatch_lspatches_13.out...

Summary:
  - First source  => file: opatch_lspatches_12.out contains 7 patches
  - Second source => file: opatch_lspatches_13.out contains 9 patches

Database Release Update : 19.28.0.0.250715 (37960098)

Patches only in the first source:
  No patches only in file: opatch_lspatches_12.out

Patches only in the second source:
 ==> 37690446; ORA-600 [KTATMKREF-RS] ERRORS IN THE ALERT LOG POST-PATCH 37260974 (19.26.0.0.250121 DBRU)
 ==> 38764114; DIAGNOSTIC PATCH FOR BUG 38427593
```

If you only want to check for differences, use the *-s/--short* option:

```
./opatch_diff.py --short opatch_lspatches_12.out opatch_lspatches_13.out 
Reading patches from 'opatch lspatches' opatch_lspatches_12.out...
Reading patches from 'opatch lspatches' opatch_lspatches_13.out...

Summary:
  - First source  => file: opatch_lspatches_12.out contains 7 patches
  - Second source => file: opatch_lspatches_13.out contains 9 patches

Database Release Update : 19.28.0.0.250715 (37960098)

Patches only in the first source:
  No patches only in file: opatch_lspatches_12.out

Patches only in the second source:
 ==> 37690446; ORA-600 [KTATMKREF-RS] ERRORS IN THE ALERT LOG POST-PATCH 37260974 (19.26.0.0.250121 DBRU)
 ==> 38764114; DIAGNOSTIC PATCH FOR BUG 38427593
```

`opatch lsinventory` provides more detailed information about patch differences. 
```
./opatch_diff.py opatch_lsinventory_12.out opatch_lsinventory_13.out
Reading patches from 'opatch lsinventory' opatch_lsinventory_12.out...
Reading patches from 'opatch lsinventory' opatch_lsinventory_13.out...

Summary:
  - First source  => file: opatch_lsinventory_12.out contains 7 patches
  - Second source => file: opatch_lsinventory_13.out contains 9 patches

Database Release Update : 19.28.0.0.250715 (37960098)

Patches only in the first source:
  No patches only in file: opatch_lsinventory_12.out

Patches only in the second source:
 ==> 37690446; ORA-600 [KTATMKREF-RS] ERRORS IN THE ALERT LOG POST-PATCH 37260974 (19.26.0.0.250121 DBRU)
   Created on 17 Jul 2025, 04:45:30 hrs PST8PDT
   Bugs fixed:
     37690446
   This patch overlays patches:
     37960098
   This patch needs patches:
     37960098
   as prerequisites

 ==> 38764114; DIAGNOSTIC PATCH FOR BUG 38427593
   Created on 13 Jan 2026, 22:27:00 hrs PST8PDT
   Bugs fixed:
     38764114
   This patch overlays patches:
     37960098
   This patch needs patches:
     37960098
   as prerequisites
```

The *-s/--short* option reduces the output.
```
./opatch_diff.py opatch_lsinventory_12.out opatch_lsinventory_13.out -s
Reading patches from 'opatch lsinventory' opatch_lsinventory_12.out...
Reading patches from 'opatch lsinventory' opatch_lsinventory_13.out...

Summary:
  - First source  => file: opatch_lsinventory_12.out contains 7 patches
  - Second source => file: opatch_lsinventory_13.out contains 9 patches

Database Release Update : 19.28.0.0.250715 (37960098)

Patches only in the first source:
  No patches only in file: opatch_lsinventory_12.out

Patches only in the second source:
 ==> 37690446; ORA-600 [KTATMKREF-RS] ERRORS IN THE ALERT LOG POST-PATCH 37260974 (19.26.0.0.250121 DBRU)
 ==> 38764114; DIAGNOSTIC PATCH FOR BUG 38427593
```
### Comparing Saved Output With Generated Output

Sometimes you already have a saved OPatch output, which you want to compare with the 
installed patches on the local ORACLE_HOME. You can generate the OPatch output on your 
own or you can provide the ORACLE_HOME path to the tool. The tool would set the 
environment variable ORACLE_HOME, generate the OPatch output and compare them.

```
./opatch_diff.py -oh /u01/oracle/db19a ./opatch_lspatches_01.out  --lspatches 
Running command: /u01/oracle/db19a/OPatch/opatch lspatches
Reading patches from 'opatch lspatches' for ORACLE_HOME: /u01/oracle/db19a...
Reading patches from 'opatch lspatches' ./opatch_lspatches_01.out...

Summary:
  - First source  => ORACLE_HOME: /u01/oracle/db19a contains 3 patches
  - Second source => file: ./opatch_lspatches_01.out contains 3 patches

Database Release Update : 19.24.0.0.240716 (36582781)

Patches only in the first source:
  No patches only in ORACLE_HOME: /u01/oracle/db19a

Patches only in the second source:
  No patches only in the file: ./opatch_lspatches_01.out

```

You can use the options *--lspatches* or *--lsinventory* for generating 
the OPatch output. The default option is *--lsinventory*.

### Comparing Generated Output

Sometimes you have multiple ORACLE_HOMEs and want to compare them. In 
this case you can run the tool and provide the path to both ORACLE_HOMEs. 

```
./opatch_diff.py -oh1 /u01/oracle/db19a -oh2 /u01/oracle/db19b --lspatches  
Running command: /u01/oracle/db19a/OPatch/opatch lspatches
Reading patches from 'opatch lspatches' for ORACLE_HOME: /u01/oracle/db19a...
Running command: /u01/oracle/db19b/OPatch/opatch lspatches
Reading patches from 'opatch lspatches' for ORACLE_HOME: /u01/oracle/db19b...

Summary:
  - First source  => ORACLE_HOME: /u01/oracle/db19a contains 3 patches
  - Second source => ORACLE_HOME: /u01/oracle/db19b contains 3 patches

 ===> WARNING: Database Release Updates differ:
  - First source  => Database Release Update : 19.24.0.0.240716 (36582781)
  - Second source => Database Release Update : 19.26.0.0.250121 (37260974)

Patches only in the first source:
 ==> 36414915; OJVM RELEASE UPDATE: 19.24.0.0.240716 (36414915)
 ==> 36582781; Database Release Update : 19.24.0.0.240716 (36582781)

Patches only in the second source:
 ==> 37102264; OJVM RELEASE UPDATE: 19.26.0.0.250121 (37102264)
 ==> 37260974; Database Release Update : 19.26.0.0.250121 (37260974)

```

### Saving OPatch Output

If you already use this tool, you could also generate and save OPatch output for 
any local ORACLE_HOME.

```
./opatch_diff.py -oh /u01/oracle/db19a -out my_patches.out --lspatches 
Running command: /u01/oracle/db19a/OPatch/opatch lspatches
OPatch output saved to file: my_patches.out
Reading patches from 'opatch lspatches' for ORACLE_HOME: /u01/oracle/db19a...

Database Release Update:
  - Database Release Update : 19.24.0.0.240716 (36582781)

```

### Get Release Update Version

Sometimes you want to know the Release Update version of the local ORACLE_HOME or
the saved OPatch output. You can use the *-ru* or *--release_update* option.

```
./opatch_diff.py -ru local/opatch_lsinventory_12.out 
Reading patches from 'opatch lsinventory' local/opatch_lsinventory_12.out...
Database Release Update:
  - Database Release Update : 19.28.0.0.250715 (37960098)
```

This option together with the *--oratab* option can be used to find the Release Update 
versions of all local ORACLE_HOMEs from the `/etc/oratab` file.

```
./opatch_diff.py -ru --oratab
Checking Release Update for ORACLE_HOME: /u01/oracle/db19a
Running command: /u01/oracle/db19a/OPatch/opatch lspatches
Reading patches from 'opatch lspatches' for ORACLE_HOME: /u01/oracle/db19a...
Database Release Update:
  - Database Release Update : 19.24.0.0.240716 (36582781)

Checking Release Update for ORACLE_HOME: /u01/oracle/db12
error: the directory /u01/oracle/db12 does not exist

Checking Release Update for ORACLE_HOME: /u01/oracle/db19b
Running command: /u01/oracle/db19b/OPatch/opatch lspatches
Reading patches from 'opatch lspatches' for ORACLE_HOME: /u01/oracle/db19b...
Database Release Update:
  - Database Release Update : 19.26.0.0.250121 (37260974)
```