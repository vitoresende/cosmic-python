import hashlib
import os
import shutil
from pathlib import Path
"""
Imagine we want to write code for synchronizing two file directories, 
which we'll call the source and the destination:
- If a file exists in the source but not in the destination, copy the file over.
- If a file exists in the source, but it has a different name than in the 
destination, rename the destination file to match.
- If a file exists in the destination but not in the source, remove it.
"""

def sync(source, dest):
    # imperative shell step 1, gather inputs
    source_hashes = read_paths_and_hashes(source)
    dest_hashes = read_paths_and_hashes(dest)

    # step 2: call functional core
    actions = determine_actions(source_hashes, dest_hashes, source, dest)

    # imperative shell step 3, apply outputs
    for action, *paths in actions:
        if action == "COPY":
            shutil.copyfile(*paths)
        if action == "MOVE":
            shutil.move(*paths)
        if action == "DELETE":
            os.remove(paths[0])

"""
To detect renames, we'll have to inspect the content of files. 
For this, we can use a hashing function like MD5 or SHA-1. 
The code to generate a SHA-1 hash from a file is simple enough:
"""
BLOCKSIZE = 65536

def hash_file(path):
    hasher = hashlib.sha1()
    with path.open("rb") as file:
        buf = file.read(BLOCKSIZE)
        while buf:
            hasher.update(buf)
            buf = file.read(BLOCKSIZE)
    return hasher.hexdigest()

"""
Isolates the I/O part of our application.
"""
def read_paths_and_hashes(root):
    hashes = {}
    for folder, _, files in os.walk(root):
        for fn in files:
            hashes[hash_file(Path(folder) / fn)] = fn
    return hashes

"""
The determine_actions() function will be the core of our business logic, 
which says, "Given these two sets of hashes and filenames, what should 
we copy/move/delete?". 
It takes simple data structures and returns simple data structures:
"""
def determine_actions(source_hashes, dest_hashes, source_folder, dest_folder):
    source_folder = Path(source_folder)
    dest_folder = Path(dest_folder)
    
    for sha, filename in source_hashes.items():
        if sha not in dest_hashes:
            sourcepath = source_folder / filename
            destpath = dest_folder / filename
            yield "COPY", sourcepath, destpath

        elif dest_hashes[sha] != filename:
            olddestpath = dest_folder / dest_hashes[sha]
            newdestpath = dest_folder / filename
            yield "MOVE", olddestpath, newdestpath

    for sha, filename in dest_hashes.items():
        if sha not in source_hashes:
            yield "DELETE", dest_folder / filename