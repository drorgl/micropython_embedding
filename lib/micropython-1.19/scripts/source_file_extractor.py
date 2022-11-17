import os,glob, re

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
