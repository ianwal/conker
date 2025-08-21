#include <ultra64.h>
#include "functions.h"
#include "variables.h"
#include "viint.h"

__OSViContext *__osViGetCurrentContext(void)
{
    return __osViCurr;
}
