#!/usr/bin/env python3

# Created by Andrej Simon, Oracle CSS Germany

import argparse
import os
import re
import subprocess
import sys

from typing import NamedTuple

class OPatchArg(NamedTuple):
    source: str
    path: str
    lspatches: bool
    lsinventory: bool
    output: str

def read_lspatches(lines, filename):
    patches = {}

    for line in lines:
        line = line.strip()
        if not line or line.find(';') == -1:
            continue
        num, desc = line.split(';', 1)
        try:
            patch_id = int(num)
            patches[patch_id] = {"description": desc,
                                 "extra_lines": ""}
        except ValueError:
            print(f"error: invalid patch ID: '{num}' in {filename}")
            sys.exit(1)

    return patches

def read_lsinventory(lines):
    patches = {}
    current_id = None
    current_desc = None
    extra_lines = []
    is_capturing_extra = False

    for line in lines:
        patch_match = re.search(r"^Patch\s+(\d+)\s+:", line)
        if patch_match:
            if current_id:
                patches[current_id] = {
                    "description": current_desc,
                    "extra_lines": "\n".join(extra_lines)
                }

            current_id = int(patch_match.group(1))
            current_desc = None
            extra_lines = []
            is_capturing_extra = False
            continue

        desc_match = re.search(r'Patch\s+description\s*:\s*"(.*)"', line)
        if desc_match and current_id:
            current_desc = desc_match.group(1)
            is_capturing_extra = True
            continue

        if is_capturing_extra and current_id:
            clean_line = line.strip()
            if clean_line:
                extra_lines.append(line)
            else:
                is_capturing_extra = False
                # continue
        #
        # if is_capturing_extra:
        #     extra_lines.append(line)

    if current_id:
        patches[current_id] = {
            "description": current_desc,
            "extra_lines": "".join(extra_lines)
        }

    return patches

def check_args(args):
    if len(args) != 2:
        print("Usage: opatch_diff.py OPatch_lspatches_output OPatch_lspatches_output")
        sys.exit(1)

    return args[0], args[1]

def is_lsinventory(lines):
    for line in lines:
        if (line.startswith('Oracle Interim Patch Installer') or
                line.startswith('Interim patches')):
            return True

    return False

def read_patches(filename):
    with open(filename) as f:
        lines = f.read().splitlines()

    if not lines:
        print(f"error: no lines found in {filename}")
        sys.exit(1)

    if is_lsinventory(lines):
        print(f"Reading patches from 'opatch lsinventory' {filename}...")
        return read_lsinventory(lines)

    print(f"Reading patches from 'opatch lspatches' {filename}...")
    return read_lspatches(lines, filename)

def read_opatch_source(src):
    patches = {}

    if src.source == 'file':
        patches = read_patches(src.path)
        if not patches:
            print(f"No patches found in the file {src.path}")

    elif src.source == 'oracle_home':
        patches = run_opatch(src)
        if not patches:
            print(f"No patches found in the Oracle Home {src.path}")

    return patches

def check_opatch_path(oracle_home):
    if not os.path.isdir(oracle_home):
        print(f"error: the directory {oracle_home} does not exist")
        return None

    opatch_path = os.path.join(oracle_home, "OPatch", "opatch")

    # 1. Check if the path exists
    if not os.path.exists(opatch_path):
        print(f"error: the directory or file {opatch_path} does not exist")
        return None

    # 2. Check if it is actually a file (not a directory) and is executable
    if not os.path.isfile(opatch_path) or not os.access(opatch_path, os.X_OK):
        print(f"error: {opatch_path} is not an executable file")
        return None

    return opatch_path

def read_opatch_output(oracle_home, lines, is_lspatches =False):
    if is_lspatches:
        print(f"Reading patches from 'opatch lspatches' for ORACLE_HOME: {oracle_home}...")
        return read_lspatches(lines, oracle_home)

    print(f"Reading patches from 'opatch lsinventory' for ORACLE_HOME: {oracle_home}...")
    return read_lsinventory(lines)

# def run_opatch(oracle_home, is_lspatches=False, is_lsinventory=False):
def run_opatch(source):
    my_env = os.environ.copy()
    my_env["ORACLE_HOME"] = source.path
    opatch = check_opatch_path(source.path)
    if not opatch:
        return {}

    opatch_arg = "lspatches" if source.lspatches else "lsinventory"
    cmd = [opatch, opatch_arg]

    print(f"Running command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                universal_newlines=True,
                                check=True, env=my_env)
        if result.returncode == 0 and result.stdout:
            if source.output:
                with open(source.output, "w") as f:
                    f.write(result.stdout)
                print(f"OPatch output saved to file: {source.output}")
            return read_opatch_output(source.path, result.stdout.splitlines(),
                                      source.lspatches)
        else:
            return {}

    except subprocess.CalledProcessError as e:
        print(f"error: command {cmd} failed with error: {e.stderr}")
        sys.exit(1)

def check_release_update(first, second):
    ru1 = ru2 = None

    for num in first:
        if first[num]['description'].startswith('Database Release Update'):
            ru1 = first[num]['description']
            break

    for num in second:
        if second[num]['description'].startswith('Database Release Update'):
            ru2 = second[num]['description']
            break

    if ru1 and ru2 and ru1 != ru2:
        print(f"\n ===> WARNING: Database Release Updates differ:")
        print(f"  - First source  => {ru1}")
        print(f"  - Second source => {ru2}")
    elif ru1:
        print(f"\n{ru1}")

def print_release_update(patches):
    if not patches:
        return

    print("Database Release Update:")

    for num in patches:
        if patches[num]['description'].startswith('Database Release Update'):
            print(f"  - {patches[num]['description']}")
            break
    else:
        print("  - No Database Release Update found")

def compare_patches(first, second, patches1, patches2):
    print(f"\nSummary:")
    if first.source == 'oracle_home':
        sources1 = f"ORACLE_HOME: {first.path}"
    else:
        sources1 = f"file: {first.path}"

    if second.source == 'oracle_home':
        sources2 = f"ORACLE_HOME: {second.path}"
    else:
        sources2 = f"file: {second.path}"

    print(f"  - First source  => {sources1} contains {len(patches1)} patches")
    print(f"  - Second source => {sources2} contains {len(patches2)} patches")

    check_release_update(patches1, patches2)

    print("\nPatches only in the first source:")
    patches_dif = sorted(set(patches1) - set(patches2))
    if not patches_dif:
        print(f"  No patches only in {sources1}")
    else:
        for num in patches_dif:
            patch_data = patches1[num]
            print(f" ==> {num}; {patch_data['description']}")
            if not args.short and patch_data['extra_lines']:
                print(f"{patch_data['extra_lines']}")

    print("\nPatches only in the second source:")
    patches_dif = sorted(set(patches2) - set(patches1))
    if not patches_dif:
        print(f"  No patches only in the {sources2}")
    else:
        for num in patches_dif:
            patch_data = patches2[num]
            print(f" ==> {num}; {patch_data['description']}")
            if not args.short and patch_data['extra_lines']:
                print(f"{patch_data['extra_lines']}\n")

    sys.exit(0)
def prepare_patches(first, second, ru):
    patches1 = read_opatch_source(first)

    if ru or not second:      # Only run opatch to get opatch output
        print_release_update(patches1)

    if not patches1:
        sys.exit(1)

    if not second:      # Only run opatch to get opatch output
        sys.exit(0)

    print()
    patches2 = read_opatch_source(second)
    if ru:
        print_release_update(patches2)

    if not patches2:
        sys.exit(1)

    if ru:
        sys.exit(0)

    compare_patches(first, second, patches1, patches2)

def check_oratab_release_update():
    found = set()
    with open('/etc/oratab') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            oracle_home = line.split(':')[1]
            if oracle_home in found:
                continue

            found.add(oracle_home)
            print(f"Checking Release Update for ORACLE_HOME: {oracle_home}")
            patches = run_opatch(OPatchArg(source='oracle_home', path=oracle_home,
                                          lspatches=True, lsinventory=False, output=""))
            print_release_update(patches)
            print()

# Main function
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare two Oracle OPatch inventories.",
                                     epilog=" => Created by Andrej Simon, Oracle CSS Germany (https://github.com/asimondev/opatch_diff)")
    parser.add_argument("-s", "--short", action="store_true", help="print less details (hide extra lines)")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.2")
    parser.add_argument("--lspatches", action="store_true", help="run 'opatch lspatches'")
    parser.add_argument("--lsinventory", action="store_true", help="run 'opatch lsinventory'")
    parser.add_argument("-oh", "--oracle_home", help="ORACLE_HOME directory")
    parser.add_argument("-oh1", "--oracle_home1", help="first ORACLE_HOME directory")
    parser.add_argument("-oh2", "--oracle_home2", help="second ORACLE_HOME directory")
    parser.add_argument("-f1", "--file1", help="first OPatch output file")
    parser.add_argument("-f2", "--file2", help="second OPatch output file")
    parser.add_argument("first_file", nargs='?', default=None,
                        help="first OPatch output file")
    parser.add_argument("second_file", nargs='?', default=None,
                        help="second OPatch output file")
    parser.add_argument("-out", "--patch_output", help="save OPatch output to file")
    parser.add_argument("-out1", "--patch_output1",
                        help="save first OPatch output to file")
    parser.add_argument("-out2", "--patch_output2",
                        help="save second OPatch output to file")
    parser.add_argument("-ru", "--release_update", action="store_true",
                        help="only print Release Update version")
    parser.add_argument("--oratab", action="store_true",
                        help="use /etc/oratab file to find ORACLE_HOME directories")

    args = parser.parse_args()

    if args.first_file and args.second_file and args.oracle_home:
        parser.error("--oracle_home can not be specified with two OPatch output files")

    if args.file1 and args.file2 and (args.first_file or args.second_file):
        parser.error("only two OPatch output files can be specified")

    if args.file1 and args.oracle_home1:
        parser.error("--oracle_home1 or --file1 can be specified but not both")

    if args.file2 and args.oracle_home2:
        parser.error("--oracle_home2 or --file2 can be specified but not both")

    if args.lspatches and (not args.oracle_home and not
            args.oracle_home1 and not args.oracle_home2):
        parser.error("--lspatches can only be specified with --oracle_homeX")

    if args.lsinventory and (not args.oracle_home and not
            args.oracle_home1 and not args.oracle_home2):
        parser.error("--lsinventory can only be specified with --oracle_homeX")

    if args.oratab:
        if args.release_update:
            check_oratab_release_update()
            sys.exit(0)
        else:
            parser.error("--oratab can only be specified with --release_update")

    if args.first_file and args.second_file:
        prepare_patches(OPatchArg(source='file', path=args.first_file,
                                  lspatches=False, lsinventory=False, output=""),
                        OPatchArg(source='file', path=args.second_file,
                                  lspatches=False, lsinventory=False, output=""),
                        args.release_update)

    if args.oracle_home and args.first_file:
        prepare_patches(OPatchArg(source='oracle_home', path=args.oracle_home,
                                  lspatches=args.lspatches, lsinventory=args.lsinventory,
                                  output=args.patch_output if args.patch_output else None),
                        OPatchArg(source='file', path=args.first_file,
                                  lspatches=False, lsinventory=False, output= ""),
                        args.release_update)

    if (args.oracle_home and not args.file1 and not args.file2 and
            not args.first_file and not args.second_file and
            not args.oracle_home1 and not args.oracle_home2):
        prepare_patches(OPatchArg(source='oracle_home', path=args.oracle_home,
                                  lspatches=args.lspatches, lsinventory=args.lsinventory,
                                  output=args.patch_output if args.patch_output else None),
                        None, args.release_update)

    if args.file1 or args.first_file:
        file1 = OPatchArg(source='file', path=args.file1 if args.file1 else args.first_file,
                          lspatches=False, lsinventory=False, output="")
    elif args.oracle_home1:
        file1 = OPatchArg(source='oracle_home', path=args.oracle_home1,
                          lspatches=args.lspatches, lsinventory=args.lsinventory,
                          output=args.patch_output1 if args.patch_output1 else None)
    else:
        file1 = None

    if args.file2 or args.second_file:
        file2 = OPatchArg(source='file', path=args.file2 if args.file2 else args.second_file,
                          lspatches=False, lsinventory=False, output="")
    elif args.oracle_home2:
        file2 = OPatchArg(source='oracle_home', path=args.oracle_home2,
                          lspatches=args.lspatches, lsinventory=args.lsinventory,
                          output=args.patch_output2 if args.patch_output2 else None)
    else:
        file2 = None

    if file1 is None and file2 is None:
        parser.error("either --fileX or --oracle_homeX must be specified")

    if file1 is None or file2 is None:
        if args.release_update:
            prepare_patches(file1 if file1 else file2, None, args.release_update)
        else:
            parser.error("either --fileX or --oracle_homeX must be specified")

    prepare_patches(file1, file2, args.release_update)
