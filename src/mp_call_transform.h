#pragma once

#include "py/builtin.h"
#include "py/compile.h"
#include "py/runtime.h"
#include "py/gc.h"
#include "py/stackctrl.h"
#include "py/persistentcode.h"
#include "py/mperrno.h"

#include <malloc.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

struct _mp_instance
{
    size_t stack_size;
    size_t heap_size;

    uint8_t *stack;
    uint8_t *heap;
};

typedef struct _mp_instance mp_instance_t;

mp_instance_t *mp_instance_init(size_t stack_size, size_t heap_size)
{
    mp_instance_t *instance = (mp_instance_t *)malloc(sizeof(mp_instance_t));
    instance->stack_size = stack_size;
    instance->heap_size = heap_size;

    instance->stack = (uint8_t *)malloc(instance->stack_size);
    instance->heap = (uint8_t *)malloc(instance->heap_size);

    mp_stack_ctrl_init();
    mp_stack_set_limit(instance->stack_size);

    // Initialize heap
    gc_init(instance->heap, instance->heap + instance->heap_size);
    mp_pystack_init(instance->stack, instance->stack + instance->stack_size);

    // Initialize interpreter
    mp_init();

    return instance;
}

void mp_instance_deinit(mp_instance_t *instance)
{
    mp_deinit();

    free(instance->stack);
    free(instance->heap);
}

static void stderr_print_strn(void *env, const char *str, size_t len)
{
    (void)env;
    printf("%.*s", len, str);
}

static const mp_print_t mp_stderr_print = {NULL, stderr_print_strn};

mp_obj_t mp_execute(mp_instance_t *instance, const char *fragment)
{
    nlr_buf_t nlr;
    if (nlr_push(&nlr) == 0)
    {
        qstr src_name = 1 /*MP_QSTR_*/;
        mp_lexer_t *lex = mp_lexer_new_from_str_len(src_name, fragment, strlen(fragment), false);
        qstr source_name = lex->source_name;
        mp_parse_tree_t pt = mp_parse(lex, MP_PARSE_FILE_INPUT);
        mp_obj_t module_fun = mp_compile(&pt, source_name, false);
        mp_call_function_0(module_fun);

        nlr_pop();
        return NULL;
    }
    else
    {
        mp_obj_print_exception(&mp_stderr_print, MP_OBJ_FROM_PTR(nlr.ret_val));
        return (mp_obj_t)nlr.ret_val;
    }
}

void dump_locals()
{
    printf("locals");
    mp_obj_dict_t *locals = mp_locals_get();
    mp_obj_print(locals, PRINT_STR);
    printf("\r\n");
}

void dump_globals()
{
    printf("globals");
    mp_obj_dict_t *globals = mp_globals_get();
    mp_obj_print(globals, PRINT_STR);
    printf("\r\n");
}

mp_obj_t get_object_by_name(mp_obj_t dict, const char *name)
{
    return mp_obj_dict_get(dict, mp_obj_new_str(name, strlen(name)));
}

mp_obj_t mp_call_function(mp_obj_t func, size_t argc, const mp_obj_t *argv)
{
    nlr_buf_t nlr;
    if (nlr_push(&nlr) == 0)
    {
        mp_obj_t retval = mp_call_function_n_kw(func, argc, 0, argv);
        nlr_pop();
        return retval;
    }
    else
    {
        mp_obj_print_exception(&mp_stderr_print, MP_OBJ_FROM_PTR(nlr.ret_val));
        return (mp_obj_t)nlr.ret_val;
    }
}

void dump_mp_obj(mp_obj_t obj)
{
    if (obj == NULL)
    {
        printf("null");
    }
    const mp_obj_type_t *type = mp_obj_get_type(obj);
    if (type != NULL)
    {
        printf("type %s: ", mp_obj_get_type_str(obj));
        mp_obj_print(obj, PRINT_STR);
    }
    else
    {
        printf("unknown type");
    }
}
