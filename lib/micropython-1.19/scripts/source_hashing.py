import hashlib
import json
import os


def filehash(filepath):
    sha = hashlib.sha1()
    with open(filepath, 'rb') as fp:
        while 1:
            data = fp.read(4096)
            if data:
                sha.update(data)
            else:
                break
    return sha.hexdigest()


def get_folder_files(folder):
    extensions = (".c", ".h")
    scanned_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            # print("file", file)
            if file.endswith(extensions):
                scanned_files.append(os.path.join(root, file))
    return scanned_files


def hash_files(files):
    hashes = {}
    for file in files:
        hashes[file] = filehash(file)
    return hashes

def hash_sources(root_folder):
    hashed_files = hash_files(get_folder_files(root_folder))
    return hashed_files


def load_hashed_files(filename):
    existing_hashed_files = {}
    if os.path.isfile(filename):
        with open(filename, 'r') as read_hashed_files:
            existing_hashed_files = json.load(read_hashed_files)
    return existing_hashed_files


def save_hashed_files(filename, hashed_files):
    with open(filename, 'w') as write_hashed_files:
        write_hashed_files.write(json.dumps(hashed_files))


def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj


def compare_hashed_files(hashed_files1, hashed_files2):
    return ordered(hashed_files1) == ordered(hashed_files2)
