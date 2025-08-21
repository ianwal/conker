#include <ultra64.h>
#include "functions.h"
#include "variables.h"

// From https://github.com/decompals/ultralib/blob/48f9f9084e06036f1a613187186c8b0f5b68ce40/src/libc/string.c
// TODO: This file should be compiled with -O3

void* memcpy(void* dest, const void* src, size_t count) {
    u8* dst = (u8*)dest;
    const u8* source = (const u8*)src;

    while(count > 0) {
        *dst++ = *source++;
        count--;
    }
    return dest;
}

size_t strlen(const u8 *str) {
    const u8* p = str;

    while(*p != '\0') {
        p++;
    }
    return p - str;
}

#pragma GLOBAL_ASM("asm/nonmatchings/libultra/libc/string/strchr.s")
// char* strchr(const char* s, int c) {
//     const char ch = c;
//     while (*s != ch) {
//         if (*s == 0) {
//             return 0;
//         }
//         s++;
//     }
//     return (char*)s;
// }
