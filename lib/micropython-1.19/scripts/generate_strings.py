import subprocess
from source_file_extractor import get_search_files

def makeqstrdefs(library_root, compiler_flags, generated_folder, src_filter):
    print("compiler_flags", compiler_flags, src_filter)
    makeversionhdr_cmd = "python ../py/makeversionhdr.py " + generated_folder + "/mpversion.h"
    print("running", makeversionhdr_cmd)
    subprocess.call(makeversionhdr_cmd)

    def divide_chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    

    source_files = get_search_files(library_root, src_filter)
    # print("source files", source_files)
    
    source_files_chunks = list(divide_chunks(source_files, 100))

    for source_files_chunk in source_files_chunks:

        makeqstrdefs_cc_cmd = "python ../py/makeqstrdefs.py pp " + compiler_flags["cc_cmd"] + " -E output " +  \
            generated_folder + "/qstr.i.last cflags " + compiler_flags["defines"] +" "+ compiler_flags["c_flags"] +" "+  \
            compiler_flags["includes"] + " cxxflags " + compiler_flags["defines"] +" "+ compiler_flags["c_flags"] +" "+ compiler_flags["includes"] + \
            " sources " + " ".join(source_files_chunk)

        print("running", makeqstrdefs_cc_cmd)
        subprocess.call(makeqstrdefs_cc_cmd)

        makeqstrdefs_split_qstr_cmd = "python ../py/makeqstrdefs.py split qstr " + generated_folder + "/qstr.i.last " + generated_folder + "/qstr _"
        print("running", makeqstrdefs_split_qstr_cmd)
        subprocess.call(makeqstrdefs_split_qstr_cmd)

        makeqstrdefs_split_module_cmd = "python ../py/makeqstrdefs.py split module " + generated_folder + "/qstr.i.last " + generated_folder + "/module _"
        print("running", makeqstrdefs_split_module_cmd)
        subprocess.call(makeqstrdefs_split_module_cmd)
    
def makeqstrdefs_cat(generated_folder):
    makeqstrdefs_cat_qstr_cmd ="python ../py/makeqstrdefs.py cat qstr _ " + generated_folder + "/qstr " + generated_folder + "/qstrdefs.collected.h"
    print("running", makeqstrdefs_cat_qstr_cmd)
    subprocess.call(makeqstrdefs_cat_qstr_cmd)




def makeqstrdefs_cat_module(generated_folder):
    makeqstrdefs_cat_module_cmd ="python ../py/makeqstrdefs.py cat module _ " + generated_folder + "/module " + generated_folder + "/moduledefs.collected"
    print("running", makeqstrdefs_cat_module_cmd)
    subprocess.call(makeqstrdefs_cat_module_cmd)


def makemoduledefs(generated_folder):
    moduledefs_filename = "" + generated_folder + "/moduledefs.h"
    f = open(moduledefs_filename, "w")
    makemoduledefs_cmd = "python ../py/makemoduledefs.py " + generated_folder + "/moduledefs.collected"
    print("running", makemoduledefs_cmd, "into", moduledefs_filename)
    subprocess.call(makemoduledefs_cmd, stdout=f)


def qstrdefs_preprocessed(compiler_flags, generated_folder):
    qstrdefs_preprocessed_filename = "" + generated_folder + "/qstrdefs.preprocessed.h"
    f = open(qstrdefs_preprocessed_filename, "w")
    preprocess_qstrdefs_cmd = compiler_flags["cc_cmd"] + " " + compiler_flags["defines"] +" "+ compiler_flags["c_flags"] +" "+ compiler_flags["includes"] + " -E ../py/qstrdefs.h  " + generated_folder + "/qstrdefs.collected.h ../ports/unix/qstrdefsport.h"
    print("running", preprocess_qstrdefs_cmd, "into", qstrdefs_preprocessed_filename)
    subprocess.call(preprocess_qstrdefs_cmd, stdout=f)



def qstrdefs_generated(generated_folder):
    qstrdefs_generated_filename = "" + generated_folder + "/qstrdefs.generated.h"
    f = open(qstrdefs_generated_filename, "w")
    makeqstrdata_cmd = "python ../py/makeqstrdata.py " + generated_folder + "/qstrdefs.preprocessed.h"
    print("running", makeqstrdata_cmd, "into", qstrdefs_generated_filename)
    subprocess.call(makeqstrdata_cmd, stdout=f)


def generate_strings(library_root, compiler_flags, generated_folder, src_filter):
    makeqstrdefs(library_root,compiler_flags,generated_folder, src_filter)
    makeqstrdefs_cat(generated_folder)
    makeqstrdefs_cat_module(generated_folder)
    makemoduledefs(generated_folder)
    qstrdefs_preprocessed(compiler_flags,generated_folder )
    qstrdefs_generated(generated_folder)