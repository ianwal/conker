#include <ultra64.h>
#include "functions.h"
#include "variables.h"


s32 __osSpRawStartDma(s32 direction, u32 devAddr, void* dramAddr, u32 size) {
    // assert(((u32)devAddr & 0x7) == 0); // TODO: Fix assert()
    // assert(((u32)dramAddr & 0x7) == 0); // TODO: Fix assert()
    // assert(((u32)size & 0x7) == 0);    // TODO: Fix assert()

    if(!devAddr && !devAddr){} // TODO: Fix the asserts above so that we don't need this line.

    if (__osSpDeviceBusy()) {
        return -1;
    }

    IO_WRITE(SP_MEM_ADDR_REG, devAddr);
    IO_WRITE(SP_DRAM_ADDR_REG, osVirtualToPhysical(dramAddr));

    if (direction == OS_READ) {
        IO_WRITE(SP_WR_LEN_REG, size - 1);
    } else {
        IO_WRITE(SP_RD_LEN_REG, size - 1);
    }

    return 0;
}
