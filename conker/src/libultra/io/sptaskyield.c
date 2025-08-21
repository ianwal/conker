#include <ultra64.h>
#include "functions.h"
#include "variables.h"


void osSpTaskYield(void) {
    __osSpSetStatus(SP_SET_YIELD);
}
