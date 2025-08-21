#include <ultra64.h>
#include "functions.h"
#include "variables.h"
#include "piint.h"

u32 osPiGetStatus()
{
    return IO_READ(PI_STATUS_REG);
}
