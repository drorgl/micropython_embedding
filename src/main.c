#include "mp_call_transform.h"

#include <time.h>
#include <math.h>

void time_c_function()
{
    clock_t start, end;
    double cpu_time_used;

    start = clock();

    size_t iterations = 1000000;

    for (uint32_t i = 0; i < iterations; i++)
    {
        float a = i;
        float b = i;
        float value = (powf(a, 2) / sin(2 * M_PI / b)) - a / 2;
        (void)value;
    }

    end = clock();
    cpu_time_used = ((double)(end - start));
    printf("c %zu iterations took %f ms, %f per iteration\r\n", iterations, cpu_time_used, cpu_time_used / iterations);
}

int main(int argc, char **argv)
{
    time_c_function();

    mp_instance_t *instance = mp_instance_init(1024 * 5, 1024 * 5);

    const char *complex_expression = "\
import math;\r\n\
def transform(a,b):\r\n\
    return (a**2/math.sin(2*math.pi/b))-a/2\r\n\
";

    mp_execute(instance, complex_expression);

    mp_obj_t transform_function = get_object_by_name(mp_locals_get(), "transform");

    clock_t start, end;
    double cpu_time_used;

    start = clock();

    mp_obj_t args[2];

    size_t iterations = 1000000;

    for (uint32_t i = 1; i < iterations; i++)
    {
        args[0] = mp_obj_new_float(i);
        args[1] = mp_obj_new_float(i);

        mp_obj_t retval = mp_call_function(transform_function, 2, args);

        // dump_mp_obj(retval);
        // printf("\n");
    }

    end = clock();
    cpu_time_used = ((double)(end - start));
    printf("py %zu iterations took %f ms, %f per iteration\r\n", iterations, cpu_time_used, cpu_time_used / iterations);

    mp_instance_deinit(instance);

    return 0;
}

void app_main()
{
    main(0, NULL);
}
