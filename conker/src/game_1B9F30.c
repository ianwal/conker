#include <ultra64.h>
#include "functions.h"
#include "variables.h"


#pragma GLOBAL_ASM("asm/nonmatchings/game_1B9F30/func_1518CA80.s")

extern void (*D_8008D5D0[])(void);

typedef struct {
    char pad0[0x14];          // 0x00
    s32 unk14;                 // 0x14
    char pad18[0x34 - 0x18];  // 0x18
    s16 unk34;                 // 0x34
    s16 unk36;                 // 0x36
    union {
        s16 unk38;             // 0x38
        struct {
            char _pad[3];
            u8 unk3B;
        };
    };
} Struct1518CCA8;

void func_1518CCA8(Struct1518CCA8* arg0) {
    s32 temp;

    temp = arg0->unk14;
    arg0->unk34 = arg0->unk34 + (((u32) (temp & 0xFFFF0000)) >> 16);
    arg0->unk36 = arg0->unk36 + (temp & 0xFFFF);

    if (arg0->unk38 != 0) {
        return;
    }

    temp = arg0->unk3B & 0xF;
    if (temp != 0) {
        D_8008D5D0[temp]();
    }
}
