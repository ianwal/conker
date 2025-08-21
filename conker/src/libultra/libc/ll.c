#include <ultra64.h>
#include "functions.h"
#include "variables.h"


#pragma GLOBAL_ASM("asm/nonmatchings/libultra/libc/ll/__ull_rshift.s")

#pragma GLOBAL_ASM("asm/nonmatchings/libultra/libc/ll/__ull_rem.s")

#pragma GLOBAL_ASM("asm/nonmatchings/libultra/libc/ll/__ull_div.s")

#pragma GLOBAL_ASM("asm/nonmatchings/libultra/libc/ll/__ll_lshift.s")

#pragma GLOBAL_ASM("asm/nonmatchings/libultra/libc/ll/__ll_rem.s")

#pragma GLOBAL_ASM("asm/nonmatchings/libultra/libc/ll/__ll_div.s")

#pragma GLOBAL_ASM("asm/nonmatchings/libultra/libc/ll/__ll_mul.s")

#pragma GLOBAL_ASM("asm/nonmatchings/libultra/libc/ll/__ull_divremi.s")

#pragma GLOBAL_ASM("asm/nonmatchings/libultra/libc/ll/__ll_mod.s")

#pragma GLOBAL_ASM("asm/nonmatchings/libultra/libc/ll/__ll_rshift.s")

// TODO: Below matches 100% with -O1, but we need -mips3 which requires some extra steps to add in the Makefile
//       to fix linking and set the o32 ABI bit. This is not a specific problem to conker.
// From https://github.com/decompals/ultralib/blob/48f9f9084e06036f1a613187186c8b0f5b68ce40/src/libc/ll.c

// unsigned long long __ull_rshift(unsigned long long a0, unsigned long long a1) {
//     return a0 >> a1;
// }
// 
// unsigned long long __ull_rem(unsigned long long a0, unsigned long long a1) {
//     return a0 % a1;
// }
// 
// unsigned long long __ull_div(unsigned long long a0, unsigned long long a1) {
//     return a0 / a1;
// }
// 
// unsigned long long __ll_lshift(unsigned long long a0, unsigned long long a1) {
//     return a0 << a1;
// }
// 
// long long __ll_rem(unsigned long long a0, long long a1) {
//     return a0 % a1;
// }
// 
// long long __ll_div(long long a0, long long a1) {
//     return a0 / a1;
// }
// 
// unsigned long long __ll_mul(unsigned long long a0, unsigned long long a1) {
//     return a0 * a1;
// }
// 
// void __ull_divremi(unsigned long long* div, unsigned long long* rem, unsigned long long a2, unsigned short a3) {
//     *div = a2 / a3;
//     *rem = a2 % a3;
// }
// 
// long long __ll_mod(long long a0, long long a1) {
//     long long tmp = a0 % a1;
// 
//     if ((tmp < 0 && a1 > 0) || (tmp > 0 && a1 < 0)) {
//         tmp += a1;
//     }
// 
//     return tmp;
// }
// 
// long long __ll_rshift(long long a0, long long a1) {
//     return a0 >> a1;
// }