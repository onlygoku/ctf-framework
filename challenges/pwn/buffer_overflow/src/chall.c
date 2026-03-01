#include <stdio.h>
#include <stdlib.h>

void win() {
    char flag[64];
    FILE *f = fopen("/flag.txt", "r");
    if (!f) { puts("Flag file not found!"); exit(1); }
    fgets(flag, 64, f);
    printf("Flag: %s\n", flag);
}

void vulnerable() {
    char buf[64];
    printf("Input: ");
    gets(buf);  // Intentionally vulnerable
    printf("You said: %s\n", buf);
}

int main() {
    setbuf(stdout, NULL);
    vulnerable();
    return 0;
}
