Import('env')
import os,sys
import json
from os.path import join, realpath
import subprocess

from source_hashing import load_hashed_files,hash_sources,compare_hashed_files,save_hashed_files
from source_file_extractor import get_search_files
from SCons import Util
import hashlib
from generate_strings import generate_strings

if env is None:
    env = {}

def get_library_json():
    f = open(os.getcwd() + "/../library.json")
    jsonconfig = json.load(f)
    return jsonconfig

def get_current_platform():
    current_platform = env.get("PIOPLATFORM", "")
    if current_platform == "native":
        current_platform+= "-" + env.get("PLATFORM","")
    return current_platform


def get_library_common_configuration(jsonconfig):
    library_common_configuration = {}
    if ("build" in jsonconfig):
        if ("environments" in jsonconfig["build"]):
            if ("common" in jsonconfig["build"]["environments"]):
                library_common_configuration = jsonconfig["build"]["environments"]["common"]
    return library_common_configuration

def get_library_platform_configuration(jsonconfig, current_platform):
    library_platform_configuration = {}
    if ("build" in jsonconfig):
        if ("environments" in jsonconfig["build"]):
            if (current_platform in jsonconfig["build"]["environments"]):
                library_platform_configuration = jsonconfig["build"]["environments"][current_platform]
    return library_platform_configuration

# print("library config", library_common_configuration, library_platform_configuration)


def fix_includes(flags):
    for i, f in enumerate(flags):
        # print("i", i, "f", f)
        flag_parts = f.split(" ")
        if (flag_parts[0] == "-I"):
            flags[i] = flag_parts[0] + " " + os.path.abspath("../" + flag_parts[1]).replace(os.sep, "/")
    return flags


def append_library_common_configuration(library_common_configuration):
    if library_common_configuration:
        if ("flags" in library_common_configuration):
            # print("Adding flags",library_common_configuration["flags"])
            fixed_flags = fix_includes(library_common_configuration["flags"])
            # print("fixed", fixed_flags)
            flags = env.ParseFlags(fixed_flags)
            # print("flags", flags)
            env.MergeFlags(flags)
            # env.Append(FLAGS=library_common_configuration["flags"])
        if ("srcFilter" in library_common_configuration):
            # print("Adding source filters", library_common_configuration["srcFilter"])
            env.Append(SRC_FILTER=library_common_configuration["srcFilter"])

def append_library_platform_configuration(library_platform_configuration):
    if library_platform_configuration:
        if ("flags" in library_platform_configuration):
            # print("Adding flags",library_platform_configuration["flags"])
            fixed_flags = fix_includes(library_platform_configuration["flags"])
            # print("fixed", fixed_flags)
            flags = env.ParseFlags(fixed_flags)
            # print("flags", flags)
            env.MergeFlags(flags)
            # env.Append(FLAGS=library_platform_configuration["flags"])
        if ("srcFilter" in library_platform_configuration):
            # print("Adding source filters", library_platform_configuration["srcFilter"])
            env.Append(SRC_FILTER=library_platform_configuration["srcFilter"])


jsonconfig = get_library_json();
append_library_common_configuration(get_library_common_configuration(jsonconfig))
append_library_platform_configuration(get_library_platform_configuration(jsonconfig, get_current_platform()))

# print(env.Dump());
# exit(10)

def normalize_defines(defines):
    cppdefines = []
    for item in defines:
        # print("define", item)
        if type(item) is tuple:
            cppdefines.append(item[0] + "=" + str(item[1]))
        else:
            cppdefines.append(item)
    return cppdefines


def get_generated_folder(current_platform):
    generated_folder =  "../generated/" + current_platform + "/genhdr"

    if not os.path.exists(generated_folder):
        os.makedirs(generated_folder)
    return generated_folder


def get_library_root():
    library_root = os.path.abspath(os.getcwd() + "/../")
    return library_root


def get_compiler_flags(library_root):
    cc_cmd = env.get("CC","")
    cpp_defines_list = normalize_defines(env.get("CPPDEFINES"));
    cpp_defines_list.append("NO_QSTR")
    cpp_defines = ["-D" + sub for sub in cpp_defines_list]
    defines = " ".join(cpp_defines)

    c_flags = " ".join(env.get("CFLAGS",[]))
    c_flags += " " + " ".join(env.get("CCFLAGS", []))

    

    cpp_path = env.get("CPPPATH",[])
    cpp_path.append(library_root)
    cpp_path_includes = ["-I " + sub for sub in cpp_path]
    includes = " ".join(cpp_path_includes)

    return {
        "cc_cmd": cc_cmd,
        "defines" : defines,
        "c_flags": c_flags,
        "includes": includes
    }

library_root = get_library_root()
generated_folder = get_generated_folder(get_current_platform())

hashes_filename = generated_folder + "/source_hashes.json"

fresh_hashes = hash_sources(library_root)
existing_hashes = load_hashed_files(hashes_filename)
if not compare_hashed_files(fresh_hashes, existing_hashes):
    print("detected changes in source files, regenerating strings...")

    compiler_flags = get_compiler_flags(library_root)
    src_filter = env.get("SRC_FILTER")
    generate_strings(library_root, compiler_flags, generated_folder, src_filter)
    save_hashed_files(hashes_filename, fresh_hashes)

