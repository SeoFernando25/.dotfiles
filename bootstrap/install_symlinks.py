#!/bin/python

# This script is used to install the symlinks for the ../ folder (dotfiles)
import fnmatch
import os
import re
import sys

# Glob all files on the top directory that are not:
# - the bootstrap folder
# - the .git folder
# - files that match a pattern in .gitignore
# - the README.md

# Change relative path to ../
os.chdir('..')

# Glob
print('Globbing files in folders and subfolders...')
files = []

# Create fileexclude regex from .gitignore
with open('.gitignore', encoding='utf-8') as f:
    ignore = f.read().splitlines()
    # Create a regex pattern from the ignore list into one big regex
    ignore = [re.compile(fnmatch.translate(i)) for i in ignore]

ignore_folders = ['./bootstrap', './.git']
ignore_files = ['README.md', '.gitignore']
for root, dirnames, filenames in os.walk('.'):
    # Ignore folders
    if any([root.startswith(i) for i in ignore_folders]):
        continue
    for filename in filenames:
        if filename in ignore_files:
            continue
        # Check if file matches any of the ignore patterns
        if any(i.match(os.path.join(root, filename)) for i in ignore):
            continue
        files.append(os.path.join(root, filename))

print("Filtering files...")


# Prompt every file to be symlinked
ctx = ""
for f in files:
    print("--------------------")
    print()
    print("####################")
    print(f"File: {f}")
    print("####################")
    # Check if the file exists relative to the home directory
    path = os.path.expanduser('~/' + f)
    # Fix "/./" in path
    path = re.sub(r'/\./', '/', path)

    FILE_EXISTS = os.path.exists(path)
    IS_LINK = os.path.islink(path)
    if FILE_EXISTS and IS_LINK:
        SAME_SYMLINK = FILE_EXISTS and (os.path.islink(
            path) or os.readlink(path) == os.path.abspath(f))
        if SAME_SYMLINK:
            print("File is already symlinked, skipping...")
            continue

    SKIPPED_STEP = ctx not in ('3', '4')

    if FILE_EXISTS and SKIPPED_STEP:

        print("File already exists, would you like to overwrite it?")
        print("1. Yes")
        print("2. No")
        print("3. Skip all existing files")
        print("4. Overwrite all existing files")
        print("5. Exit")
        while True:
            ctx = input("Enter option: ")
            if ctx in ['1', '2', '3', '4', '5']:
                break
            print("Invalid option, try again")

        if ctx == '1':
            print("Overwriting file...")
            os.remove(path)
        elif ctx == '2':
            print("Skipping file...")
            continue
        elif ctx == '3':
            print("Skipping all...")
            break
        elif ctx == '4':
            print("Overwriting all...")
            os.remove(path)
        elif ctx == '5':
            print("Exiting...")
            sys.exit(0)

    if ctx == '4':
        print("Overwriting all...")
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
    elif ctx == '1':
        print("Overwriting file...")
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
    else:
        print("File does not exist, creating symlink...")
        try:
            v = input(
                "Press enter to proceed, or ctrl+c to skip, type anything to exit:")
        except KeyboardInterrupt:
            print("Skipping...")
            continue

        if v != '':
            print("Exiting...")
            sys.exit(0)

    # Create symlink
    print("Creating symlink...")
    print("file: " + f)
    print("path: " + path)
    target = os.path.abspath(f)

    # Create directory if it doesn't exist
    create_dir = os.path.dirname(path)
    if not os.path.exists(create_dir):
        print("Creating directory: " + create_dir)
        os.makedirs(create_dir)

    os.symlink(target, path)
