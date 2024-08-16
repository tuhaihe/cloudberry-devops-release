#!/usr/bin/env python3

import os
import subprocess
import re
from collections import defaultdict
from prettytable import PrettyTable
import argparse

def run_command(command):
    """
    Executes a command using subprocess and returns the decoded output.

    Args:
        command (list): A list of command arguments to be executed.

    Returns:
        str: The decoded output of the command.
        None: If the command fails to execute.
    """
    try:
        return subprocess.check_output(command, stderr=subprocess.STDOUT).decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(command)}: {e.output.decode('utf-8').strip()}")
        return None

def parse_ldd_line(line):
    """
    Parses a single line of `ldd` output to extract the library path.

    Args:
        line (str): A single line of `ldd` output.

    Returns:
        str: The path to the shared library, if found.
        None: If no valid library path is found in the line.
    """
    match = re.search(r'\s*(\S+) => (\S+) \((0x[0-9a-f]+)\)', line)
    return match.group(2) if match else None

def find_library_in_ld_library_path(lib_name):
    """
    Searches for a shared library in the directories specified by LD_LIBRARY_PATH.

    Args:
        lib_name (str): The name of the library to find.

    Returns:
        str: The full path to the library if found, or None if not found.
    """
    ld_library_path = os.environ.get('LD_LIBRARY_PATH', '')
    for directory in ld_library_path.split(':'):
        potential_path = os.path.join(directory, lib_name)
        if os.path.isfile(potential_path):
            return potential_path
    return None

def get_package_info(lib_path):
    """
    Retrieves package information for a given library file.

    Args:
        lib_path (str): The path to the shared library file.

    Returns:
        tuple: A tuple containing the package name and the full package name.
        None: If the package information could not be retrieved.
    """
    # If the library is not found, check in LD_LIBRARY_PATH
    if not os.path.isfile(lib_path):
        lib_name = os.path.basename(lib_path)
        lib_path = find_library_in_ld_library_path(lib_name)
        if not lib_path:
            return None

    try:
        full_package_name = run_command(['rpm', '-qf', lib_path])
        if full_package_name:
            package_name = full_package_name.split('-')[0]
            return package_name, full_package_name.strip()
    except subprocess.CalledProcessError:
        pass
    return None

def print_summary(packages, special_cases):
    """
    Prints a summary of the unique runtime packages required and any special cases.

    Args:
        packages (list): A list of tuples containing package names and full package names.
        special_cases (list): A list of special cases where the package could not be identified.
    """
    print("\nSummary of unique runtime packages required:")
    table = PrettyTable(['Package Name', 'Full Package Name'])
    table.align['Package Name'] = 'l'
    table.align['Full Package Name'] = 'l'

    unique_packages = sorted(set(packages))
    for package_name, full_package_name in unique_packages:
        table.add_row([package_name, full_package_name])
    print(table)

    if special_cases:
        print("\nSpecial Cases:")
        for case in sorted(set(special_cases)):
            print(case)

def process_binary(binary_path):
    """
    Processes a single binary file to determine its runtime package dependencies.

    Args:
        binary_path (str): The path to the binary file to be processed.

    Returns:
        list: A list of tuples containing package names and full package names.
        list: A list of special cases where the package could not be identified.
    """
    print(f"Binary: {binary_path}\n")
    print("Libraries and their corresponding packages:")

    packages = []
    special_cases = []
    known_special_cases = ['linux-vdso.so.1', 'ld-linux-x86-64.so.2']

    ldd_output = run_command(['ldd', binary_path])
    if ldd_output is None:
        return packages, special_cases

    for line in ldd_output.splitlines():
        if any(special in line for special in known_special_cases):
            continue  # Skip known special cases

        lib_path = parse_ldd_line(line)
        if lib_path:
            package_info = get_package_info(lib_path)
            if package_info:
                print(f"{lib_path} => {package_info[1]}")
                packages.append(package_info)
            else:
                # Custom or non-RPM library handling
                if os.path.exists(lib_path):
                    special_case = f"{lib_path} is a custom or non-RPM library"
                else:
                    special_case = f"{lib_path} is not found and might be a special case"
                special_cases.append(special_case)
                print(f"{lib_path} => {special_case}")
        else:
            special_case = f"{lib_path} is a special case or built-in library"
            special_cases.append(special_case)
            print(f"{lib_path} => {special_case}")

    print_summary(packages, special_cases)
    print("-------------------------------------------")
    return packages, special_cases

def process_directory(directory):
    """
    Recursively processes all ELF binaries within a directory to determine their runtime package dependencies.

    Args:
        directory (str): The path to the directory to be processed.
    """
    grand_summary = defaultdict(set)
    grand_special_cases = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if is_elf_binary(file_path):
                packages, special_cases = process_binary(file_path)
                for package_name, full_package_name in packages:
                    grand_summary[package_name].add(full_package_name)
                grand_special_cases.extend(special_cases)

    print_grand_summary(grand_summary, grand_special_cases)

def is_elf_binary(file_path):
    """
    Checks whether a given file is an ELF binary (executable or shared object).

    Args:
        file_path (str): The path to the file to be checked.

    Returns:
        bool: True if the file is an ELF binary, False otherwise.
    """
    file_output = run_command(['file', file_path])
    return 'ELF' in file_output and ('executable' in file_output or 'shared object' in file_output)

def print_grand_summary(grand_summary, grand_special_cases):
    """
    Prints a grand summary of unique runtime packages required and special cases across all processed binaries.

    Args:
        grand_summary (defaultdict): A dictionary mapping package names to sets of full package names.
        grand_special_cases (list): A list of special cases encountered during processing.
    """
    if grand_summary or grand_special_cases:
        print("\nGrand Summary of unique runtime packages required across all binaries:")
        table = PrettyTable(['Package Name', 'Full Package Name'])
        table.align['Package Name'] = 'l'
        table.align['Full Package Name'] = 'l'

        for package_name, full_package_names in sorted(grand_summary.items()):
            for full_package_name in sorted(full_package_names):
                table.add_row([package_name, full_package_name])
        print(table)

        if grand_special_cases:
            print("\nGrand Summary of special cases across all binaries:")
            for case in sorted(set(grand_special_cases)):
                print(case)

# Main entry point
if __name__ == '__main__':
    """
    Main function that parses command-line arguments and processes the specified binary file or directory.

    Usage:
        python elf_dependency_analyzer.py -f <binary_file1> <binary_file2> ...
        python elf_dependency_analyzer.py -d <directory_path>

    Options:
        -f, --file : Specify one or more individual binary files to review.
        -d, --dir  : Specify a directory to recursively review all ELF binary files.

    Description:
        This script processes ELF binary files to determine their runtime package dependencies.
        It uses the `ldd` command to list shared libraries required by the binaries and then
        identifies the packages owning those libraries using `rpm`. The results are displayed
        in a structured table format, and any special cases (e.g., libraries not owned by any package)
        are highlighted separately.

        The script can be run in two modes:
        1. File Mode: Specify one or more individual binary files to analyze.
        2. Directory Mode: Specify a directory to recursively find and analyze all ELF binaries.

        The final output includes a summary of unique runtime packages required across all processed binaries.
    """
    parser = argparse.ArgumentParser(description="Process ELF binaries to determine runtime package dependencies.")

    # Short and long options for --file, using nargs='+' to handle multiple files with a single -f
    parser.add_argument('-f', '--file', type=str, nargs='+', help="Specify one or more individual files to review.")

    # Short and long options for --dir
    parser.add_argument('-d', '--dir', type=str, help="Specify a directory to recursively review all binary files.")

    args = parser.parse_args()

    grand_summary = defaultdict(set)
    grand_special_cases = []

    if args.file:
        for file in args.file:
            if os.path.isfile(file):
                packages, special_cases = process_binary(file)
                # Accumulate results for the grand summary
                for package_name, full_package_name in packages:
                    grand_summary[package_name].add(full_package_name)
                grand_special_cases.extend(special_cases)
            else:
                print(f"Error: {file} is not a valid file.")

        # Only print the grand summary if more than one file was processed
        if len(args.file) > 1:
            print_grand_summary(grand_summary, grand_special_cases)

    elif args.dir:
        if os.path.isdir(args.dir):
            process_directory(args.dir)
        else:
            print(f"Error: {args.dir} is not a valid directory.")
