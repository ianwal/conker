// TODO: This matches perfectly, but doesn't match in the game.
// https://decomp.me/scratch/eXEp3
// See libultra https://github.com/decompals/ultralib/blob/48f9f9084e06036f1a613187186c8b0f5b68ce40/src/gu/normalize.c
#pragma GLOBAL_ASM("asm/nonmatchings/libultra/gu/guNormalize/guNormalize.s")

// void guNormalize(float *x, float *y, float *z)
// {
//     float	m;
// 
//     m = 1/sqrtf((*x)*(*x) + (*y)*(*y) + (*z)*(*z));
//     *x *= m;
//     *y *= m;
//     *z *= m;
// }
