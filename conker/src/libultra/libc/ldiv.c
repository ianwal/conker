#include <ultra64.h>
#include "functions.h"
#include "variables.h"
#include "stdlib.h"

ldiv_t ldiv(long num, long denom) {
    ldiv_t ret;

    ret.quot = num / denom;
    ret.rem = num - denom * ret.quot;

    if (ret.quot < 0 && ret.rem > 0) {
        ret.quot += 1;
        ret.rem -= denom;
    }

    return ret;
}
