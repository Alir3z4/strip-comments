#include <stdio.h>

// Line comment
void hello(const char* name) {
    printf("Hello, %s\n", name); /* inline block */
}

/* block comment */
#define X 1

struct Point {
    int x;
    int y;
};
