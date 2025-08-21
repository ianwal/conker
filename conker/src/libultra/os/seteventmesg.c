#include <ultra64.h>
#include "functions.h"
#include "variables.h"
#include "macros.h"
#include "osint.h"

// TODO: Migrate bss, remove extern from __osEventStateTab
// https://github.com/decompals/ultralib/blob/48f9f9084e06036f1a613187186c8b0f5b68ce40/src/os/seteventmesg.c#L6
// __OSEventState __osEventStateTab[OS_NUM_EVENTS] ALIGNED(0x8);

extern __OSEventState __osEventStateTab[OS_NUM_EVENTS];

#if 0 // BUILD_VERSION >= VERSION_J
u32 __osPreNMI = FALSE;
#endif

void osSetEventMesg(OSEvent event, OSMesgQueue* mq, OSMesg msg) {
    register u32 saveMask;
    __OSEventState* es;

#ifdef _DEBUG
    if (event >= OS_NUM_EVENTS) {
        __osError(ERR_OSSETEVENTMESG, 1, event);
        return;
    }
#endif

    saveMask = __osDisableInt();

    es = &__osEventStateTab[event];

    es->messageQueue = mq;
    es->message = msg;

#if 0 // BUILD_VERSION >= VERSION_J
    if (event == OS_EVENT_PRENMI) {
        if (__osShutdown && !__osPreNMI) {
            osSendMesg(mq, msg, OS_MESG_NOBLOCK);
        }
        __osPreNMI = TRUE;
    }
#endif

    __osRestoreInt(saveMask);
}
