# Micropython Embedding

Micropython initialization, execution and disposal can be a bit complicated in multiple threads environment.

- initialize heap and stack for each instance of micropython
- execute and stop execution
- memory cleanup of removed instances

## Initialization
- mp_init / gc_init

- mp_stack_set_limit


# Porting Functions
- hal printf/stdio
- mp_hal_ticks_ms(), mp_hal_ticks_us() and mp_hal_ticks_cpu() 
- mp_hal_delay_ms() and mp_hal_delay_us()



# Multiple Threads
```c
#if MICROPY_PY_THREAD
extern mp_state_thread_t *mp_thread_get_state(void);
#define MP_STATE_THREAD(x) (mp_thread_get_state()->x)
#else
#define MP_STATE_THREAD(x)  MP_STATE_MAIN_THREAD(x)
#endif
```

## mp_obj_type_t / mp_obj_list_append / mp_obj_list_get
```c
mp_obj_t list = mp_obj_new_list(0, NULL);
for (int addr = 0x08; addr < 0x78; ++addr) {
    if (ret == 0) {
        mp_obj_list_append(list, MP_OBJ_NEW_SMALL_INT(addr));
    }
}
return list;

mp_uint_t path_num;
mp_obj_t *path_items;
mp_obj_list_get(mp_sys_path, &path_num, &path_items);
```


# Execution

### Example
```c
    mp_sched_lock();
    gc_lock();
    nlr_buf_t nlr;
    if (nlr_push(&nlr) == 0) {
        mp_call_function_1(callback, MP_OBJ_FROM_PTR(tim));
        nlr_pop();
    } else {
        mp_obj_print_exception(&mp_plat_print, MP_OBJ_FROM_PTR(nlr.ret_val));
    }
    gc_unlock();
    mp_sched_unlock();
```

## Stopping
- mp_sched_keyboard_interrupt - raises an interrupt in the VM to top the current execution
But it's also possible to add hooks in the port to poll for incoming chars and check for ctrl-C, eg in the javascript port, MICROPY_VM_HOOK_POLL calls mp_js_hook() which checks for ctrl-C (should also be checked in MICROPY_EVENT_POLL_HOOK).

## Cleanup
- mp_deinit()

## Error Handling
- mp_obj_print_exception
```c
if (nlr_push(&nlr) == 0) {
    mp_parse_node_t pn = mp_parse(lex, MP_PARSE_FILE_INPUT);
    mp_obj_t module_fun = mp_compile(pn, lex->source_name, MP_EMIT_OPT_NONE, false);
    mp_call_function_0(module_fun);
    nlr_pop();
    return 0;
} else {
    // exception
    return (mp_obj_t)nlr.ret_val;
}

// and 
void nlr_jump_fail(void *val) {
    printf("FATAL: uncaught NLR %p\n", val);
    exit(1);
}
```

## Possible Extension Libraries
https://awesome-micropython.com/


# MicroPython Library
MicroPython library was installed using the following procedure
- download https://github.com/micropython/micropython/archive/refs/tags/v1.19.zip 
- expand to lib folder
- copy lib/micropython/scripts and library.json from this project


# Cleanup
Install doit
```
pip install doit
```

```
pio run -e esp32 -t clean
doit clean_micropython -e espressif32
doit clean_micropython -e espressif32 -e native-win32
```

# References:
- https://github.com/dhylands/micropython/blob/d68ae1e947dfd6db84e86ad134dd213f397ec43e/ports/stm32/c_sample.c
- https://github.com/dhylands/micropython/commit/b801dbd39eb323494f946c13362f4957f5d7281b#diff-df49b8225f13d9413a25e35e9c46acdfR24
- https://github.com/micropython/micropython/blob/master/examples/embedding/hello-embed.c
- https://www.snaums.de/static/resources/2017-12-mpy.pdf
- https://github.com/micropython/micropython/pull/9529/files
- https://github.com/micropython/micropython/pull/5964/files
