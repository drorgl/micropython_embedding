#include <stdio.h> //printf

void mp_hal_stdout_tx_strn_cooked(const char *str, size_t len) {
     printf("%.*s", len, str);
}

void mp_hal_stdout_tx_strn(const char *str, size_t len) {
    mp_hal_stdout_tx_strn_cooked(str, len);
}


void mp_hal_stdout_tx_str(const char *str){
     printf("%s",str);
}

int mp_hal_stdin_rx_chr(){
     return 0;
}

void mp_hal_set_interrupt_char(char c) {
     
}
