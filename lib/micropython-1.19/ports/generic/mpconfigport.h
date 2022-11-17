// Options to control how MicroPython is built for this port,
// overriding defaults in py/mpconfig.h.

// Board-specific definitions
#include "mpconfigboard.h"

#include <stdint.h>


#define MICROPY_ENABLE_GC                   (1)
#define MICROPY_ENABLE_PYSTACK      (1)
#define MICROPY_FLOAT_IMPL                  (MICROPY_FLOAT_IMPL_FLOAT)
#define MICROPY_PY_MATH                         (1)
#define MICROPY_PY_MATH_SPECIAL_FUNCTIONS (1)
#define MICROPY_PY_MATH_ISCLOSE     (1)
#define MICROPY_PY_CMATH            (1)
#define MICROPY_PY_IO               (0)
#define MICROPY_PY_IO_FILEIO        (0)
#define MICROPY_VFS_POSIX           (0)
#define MICROPY_VFS_POSIX_FILE      (0)
#define MICROPY_PY_SYS              (0)
#define MICROPY_PY_SYS_PS1_PS2      (0)

typedef int32_t mp_int_t; // must be pointer size
typedef uint32_t mp_uint_t; // must be pointer size
typedef long mp_off_t;
#define UINT_FMT "%u"
#define INT_FMT "%d"


#define MICROPY_PORT_ROOT_POINTERS \
    const char *readline_hist[50]; \
    void *mmap_region_head;

#ifndef MICROPY_CONFIG_ROM_LEVEL
#define MICROPY_CONFIG_ROM_LEVEL            (MICROPY_CONFIG_ROM_LEVEL_EXTRA_FEATURES)
#endif

#if !(defined(MICROPY_GCREGS_SETJMP) || defined(__x86_64__) || defined(__i386__) || defined(__thumb2__) || defined(__thumb__) || defined(__arm__))
// Fall back to setjmp() implementation for discovery of GC pointers in registers.
#define MICROPY_GCREGS_SETJMP (1)
#define MICROPY_NLR_SETJMP                  (1)
#endif

#define MP_STATE_PORT MP_STATE_VM


// workaround for xtensa-esp32-elf-gcc esp-2020r3, which can generate wrong code for loops
// see https://github.com/espressif/esp-idf/issues/9130
// this was fixed in newer versions of the compiler by:
//   "gas: use literals/const16 for xtensa loop relaxation"
//   https://github.com/jcmvbkbc/binutils-gdb-xtensa/commit/403b0b61f6d4358aee8493cb1d11814e368942c9
#if defined(MICROPY_EMIT_XTENSA) || defined(MICROPY_EMIT_XTENSAWIN)
#define MICROPY_COMP_CONST_FOLDING_COMPILER_WORKAROUND (1)
#endif

// optimisations
#define MICROPY_OPT_COMPUTED_GOTO           (1)


// very slow
// #define MICROPY_LONGINT_IMPL                (MICROPY_LONGINT_IMPL_MPZ)
// #define MP_SSIZE_MAX (0x7fffffff)


// type definitions for the specific machine
#define MICROPY_MAKE_POINTER_CALLABLE(p) ((void *)((mp_uint_t)(p)))


// Functions that should go in IRAM
#ifdef ESP_PLATFORM 
#include "esp_attr.h"

#define MICROPY_WRAP_MP_BINARY_OP(f) IRAM_ATTR f
#define MICROPY_WRAP_MP_EXECUTE_BYTECODE(f) IRAM_ATTR f
#define MICROPY_WRAP_MP_LOAD_GLOBAL(f) IRAM_ATTR f
#define MICROPY_WRAP_MP_LOAD_NAME(f) IRAM_ATTR f
#define MICROPY_WRAP_MP_MAP_LOOKUP(f) IRAM_ATTR f
#define MICROPY_WRAP_MP_OBJ_GET_TYPE(f) IRAM_ATTR f
#define MICROPY_WRAP_MP_SCHED_EXCEPTION(f) IRAM_ATTR f
#define MICROPY_WRAP_MP_SCHED_KEYBOARD_INTERRUPT(f) IRAM_ATTR f

#endif
