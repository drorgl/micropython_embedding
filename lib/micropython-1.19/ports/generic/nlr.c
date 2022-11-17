#include <stdio.h>

void nlr_jump_fail(void *val) {
    fprintf(stderr, "FATAL: uncaught NLR %p\n", val);
}