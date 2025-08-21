#include <ultra64.h>
#include "functions.h"
#include "variables.h"


s32 __osSiRawWriteIo(u32 devAddr, u32 data) {
    // assert((devAddr & 0x3) == 0); // TODO: Fix assert()

    if (__osSiDeviceBusy()) {
        return -1;
    }

    IO_WRITE(devAddr, data);
    return 0;
}
