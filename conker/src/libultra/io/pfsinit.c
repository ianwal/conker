#include <ultra64.h>
#include "functions.h"
#include "variables.h"
#include "siint.h"
#include "controller.h"
#include "os_cont.h"
#include "os_message.h"

// Doesn't look like it matches libultra?
// https://decomp.me/scratch/ggitU
#pragma GLOBAL_ASM("asm/nonmatchings/libultra/io/pfsinit/osPfsInit.s")


// Doesn't look like it matches libultra?
// https://decomp.me/scratch/A2qyT
#pragma GLOBAL_ASM("asm/nonmatchings/libultra/io/pfsinit/__osPfsGetStatus.s")
