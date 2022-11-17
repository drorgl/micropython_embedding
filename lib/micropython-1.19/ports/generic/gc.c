
#include <stdio.h>

#include "py/mpstate.h"
#include "py/gc.h"

#include "shared/runtime/gchelper.h"

#if MICROPY_ENABLE_GC

typedef struct _mmap_region_t {
    void *ptr;
    size_t len;
    struct _mmap_region_t *next;
} mmap_region_t;

void mp_unix_mark_exec(void) {
    for (mmap_region_t *rg = MP_STATE_VM(mmap_region_head); rg != NULL; rg = rg->next) {
        gc_collect_root(rg->ptr, rg->len / sizeof(mp_uint_t));
    }
}

void gc_collect(void) {
    // gc_dump_info();

    gc_collect_start();
    gc_helper_collect_regs_and_stack();
    #if MICROPY_PY_THREAD
    mp_thread_gc_others();
    #endif
    #if MICROPY_EMIT_NATIVE
    mp_unix_mark_exec();
    #endif
    gc_collect_end();

    // printf("-----\n");
    // gc_dump_info();
}

#endif // MICROPY_ENABLE_GC
