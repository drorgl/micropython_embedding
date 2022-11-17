# qstrdefs.generated.h

import os, glob, re
import io
import sys
import platform

# Steps:
# 1. list files based on src_filter
SRC_HEADER_EXT = ["h", "hpp"]
SRC_ASM_EXT = ["S", "spp", "SPP", "sx", "s", "asm", "ASM"]
SRC_C_EXT = ["c"]
SRC_CXX_EXT = ["cc", "cpp", "cxx", "c++"]
SRC_BUILD_EXT = SRC_C_EXT + SRC_CXX_EXT + SRC_ASM_EXT
SRC_FILTER_DEFAULT = ["+<*>", "-<.git%s>" % os.sep, "-<.svn%s>" % os.sep]

def path_endswith_ext(path, extensions):
    if not isinstance(extensions, (list, tuple)):
        extensions = [extensions]
    for ext in extensions:
        if path.endswith("." + ext):
            return True
    return False

def match_src_files(src_dir, src_filter=None, src_exts=None, followlinks=True):
    # print("src", src_dir,"filter", src_filter, "ext",src_exts)
    def _add_candidate(items, item, src_dir):
        if not src_exts or path_endswith_ext(item, src_exts):
            items.add(os.path.relpath(item, src_dir))

    def _find_candidates(pattern):
        candidates = set()
        for item in glob.glob(
            os.path.join(glob.escape(src_dir), pattern), recursive=True
        ):
            if not os.path.isdir(item):
                _add_candidate(candidates, item, src_dir)
                continue
            for root, dirs, files in os.walk(item, followlinks=followlinks):
                for d in dirs if not followlinks else []:
                    if os.path.islink(os.path.join(root, d)):
                        _add_candidate(candidates, os.path.join(root, d), src_dir)
                for f in files:
                    _add_candidate(candidates, os.path.join(root, f), src_dir)
        return candidates

    src_filter = src_filter or ""
    if isinstance(src_filter, (list, tuple)):
        src_filter = " ".join(src_filter)

    result = set()
    # correct fs directory separator
    src_filter = src_filter.replace("/", os.sep).replace("\\", os.sep)
    for (action, pattern) in re.findall(r"(\+|\-)<([^>]+)>", src_filter):
        candidates = _find_candidates(pattern)
        if action == "+":
            result |= candidates
        else:
            result -= candidates
    return sorted(list(result))

def MatchSourceFiles(src_dir, src_filter=None, src_exts=None):
    # src_filter = subst(src_filter) if src_filter else None
    src_filter = src_filter or SRC_FILTER_DEFAULT
    src_exts = src_exts or (SRC_BUILD_EXT + SRC_HEADER_EXT)
    return match_src_files(src_dir, src_filter, src_exts)

def get_search_files(src_dir, src_filter):
    # print("src dir", src_dir)
    return [
        os.path.join(src_dir, item)
        for item in MatchSourceFiles(
            src_dir, src_filter, SRC_BUILD_EXT
        )
    ]


# 2. pass through regex
# 3. build QDEF(MP_QSTR_exc_info, 28762, 8, "exc_info")

def process_file(filename):
    with io.open(filename, encoding="utf-8") as c_file_obj:
        re_line = re.compile(r"#[line]*\s\d+\s\"([^\"]+)\"")
        # if args.mode == _MODE_QSTR:
        re_match = re.compile(r"MP_QSTR_[_a-zA-Z0-9]+")
        output = set();
        
        # elif args.mode == _MODE_COMPRESS:
        #     re_match = re.compile(r'MP_COMPRESSED_ROM_TEXT\("([^"]*)"\)')
        # elif args.mode == _MODE_MODULE:
        #     re_match = re.compile(r"MP_REGISTER_MODULE\(.*?,\s*.*?\);")
        # output = []
        last_fname = None
        for line in c_file_obj:
            if line.isspace():
                continue
            # match gcc-like output (# n "file") and msvc-like output (#line n "file")
            if line.startswith(("# ", "#line")):
                m = re_line.match(line)
                assert m is not None
                fname = m.group(1)
                # if not is_c_source(fname) and not is_cxx_source(fname):
                #     continue
                # if fname != last_fname:
                #     write_out(last_fname, output)
                #     output = []
                #     last_fname = fname
                continue
            for match in re_match.findall(line):
                # if args.mode == _MODE_QSTR:
                    name = match.replace("MP_QSTR_", "")
                    # output.append("Q(" + name + ")")
                    output.add(name)
                # elif args.mode in (_MODE_COMPRESS, _MODE_MODULE):
                #     output.append(match)

        # if last_fname:
        #     write_out(last_fname, output)
    return output



if platform.python_version_tuple()[0] == "2":
    bytes_cons = lambda val, enc=None: bytearray(val)
    from htmlentitydefs import codepoint2name
elif platform.python_version_tuple()[0] == "3":
    bytes_cons = bytes
    from html.entities import codepoint2name

# this must match the equivalent function in qstr.c
def compute_hash(qstr, bytes_hash):
    hash = 5381
    for b in qstr:
        hash = (hash * 33) ^ b
    # Make sure that valid hash is never zero, zero means "hash not computed"
    return (hash & ((1 << (8 * bytes_hash)) - 1)) or 1

def escape_bytes(qstr, qbytes):
    if all(32 <= ord(c) <= 126 and c != "\\" and c != '"' for c in qstr):
        # qstr is all printable ASCII so render it as-is (for easier debugging)
        return qstr
    else:
        # qstr contains non-printable codes so render entire thing as hex pairs
        return "".join(("\\x%02x" % b) for b in qbytes)


def make_bytes(cfg_bytes_len, cfg_bytes_hash, qstr):
    qbytes = bytes_cons(qstr, "utf8")
    qlen = len(qbytes)
    qhash = compute_hash(qbytes, cfg_bytes_hash)
    if qlen >= (1 << (8 * cfg_bytes_len)):
        print("qstr is too long:", qstr)
        assert False
    qdata = escape_bytes(qstr, qbytes)
    return '%d, %d, "%s"' % (qhash, qlen, qdata)

def print_qstr_data(qcfgs, qstrs):
    # get config variables
    cfg_bytes_len = int(qcfgs["BYTES_IN_LEN"])
    cfg_bytes_hash = int(qcfgs["BYTES_IN_HASH"])

    # print out the starter of the generated C header file
    print("// This file was automatically generated by makeqstrdata.py")
    print("")

    # add NULL qstr with no hash or data
    print('QDEF(MP_QSTRnull, 0, 0, "")')

    # go through each qstr and print it out
    for order, ident, qstr in sorted(qstrs.values(), key=lambda x: x[0]):
        qbytes = make_bytes(cfg_bytes_len, cfg_bytes_hash, qstr)
        print("QDEF(MP_QSTR_%s, %s)" % (ident, qbytes))


# 4. build MP_REGISTER_MODULE() 


pattern = re.compile(r"\s*MP_REGISTER_MODULE\((.*?),\s*(.*?)\);", flags=re.DOTALL)


def find_module_registrations(filename):
    """Find any MP_REGISTER_MODULE definitions in the provided file.

    :param str filename: path to file to check
    :return: List[(module_name, obj_module)]
    """
    global pattern

    with io.open(filename, encoding="utf-8") as c_file_obj:
        return set(re.findall(pattern, c_file_obj.read()))

def generate_module_table_header(modules):
    """Generate header with module table entries for builtin modules.

    :param List[(module_name, obj_module)] modules: module defs
    :return: None
    """
    output = ""

    # Print header file for all external modules.
    mod_defs = set()
    output += ("// Automatically generated by makemoduledefs.py.\n")
    for module_name, obj_module in modules:
        mod_def = "MODULE_DEF_{}".format(module_name.upper())
        mod_defs.add(mod_def)
        if "," in obj_module:
            print(
                "ERROR: Call to MP_REGISTER_MODULE({}, {}) should be MP_REGISTER_MODULE({}, {})\n".format(
                    module_name, obj_module, module_name, obj_module.split(",")[0]
                )
                # ,
                # file=sys.stderr,
            )
            sys.exit(1)
        output += (
            (
                "extern const struct _mp_obj_module_t {obj_module};\n"
                "#undef {mod_def}\n"
                "#define {mod_def} {{ MP_ROM_QSTR({module_name}), MP_ROM_PTR(&{obj_module}) }},\n"
            ).format(
                module_name=module_name,
                obj_module=obj_module,
                mod_def=mod_def,
            )
        )

    output += ("\n#define MICROPY_REGISTERED_MODULES \\")

    for mod_def in sorted(mod_defs):
        output += ("    {mod_def} \\".format(mod_def=mod_def))

    output += ("// MICROPY_REGISTERED_MODULES")
    return output


files = get_search_files(os.getcwd(), None)

print(files)

modules = set()
qstrs = set()
for file in files:
    modules = modules.union(find_module_registrations(file))
    qstrs = qstrs.union(process_file(file))

# print(modules)
# print(qstrs)

# print("header: " + generate_module_table_header(modules))
qcfgs = {}
qcfgs["BYTES_IN_LEN"] = 10
qcfgs["BYTES_IN_HASH"] = 3

def qstr_escape(qst):
    def esc_char(m):
        c = ord(m.group(0))
        try:
            name = codepoint2name[c]
        except KeyError:
            name = "0x%02x" % c
        return "_" + name + "_"

    return re.sub(r"[^A-Za-z0-9_]", esc_char, qst)


def prepare_qstrs(qstrs):
    for qstr in qstrs:
        ident = qstr_escape(qstr)

        # don't add duplicates
        if ident in qstrs:
            continue

        # add the qstr to the list, with order number to retain original order in file
        order = len(qstrs)
        # but put special method names like __add__ at the top of list, so
        # that their id's fit into a byte
        if ident == "":
            # Sort empty qstr above all still
            order = -200000
        elif ident == "__dir__":
            # Put __dir__ after empty qstr for builtin dir() to work
            order = -190000
        elif ident.startswith("__"):
            order -= 100000
        qstrs[ident] = (order, ident, qstr)

print_qstr_data(qcfgs, qstrs)