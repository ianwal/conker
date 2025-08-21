#include <ultra64.h>
#include "functions.h"
#include "variables.h"
#include "macros.h"

// TODO: Migrate bss and data and make these variables defined in here.
// See https://github.com/decompals/ultralib/blob/48f9f9084e06036f1a613187186c8b0f5b68ce40/src/io/siacs.c#L4
// #define SI_Q_BUF_LEN 1
// static OSMesg siAccessBuf[SI_Q_BUF_LEN] ALIGNED(0x8);
// OSMesgQueue __osSiAccessQueue ALIGNED(0x8);
// u32 __osSiAccessQueueEnabled = 0;

#define SI_Q_BUF_LEN 1
extern OSMesg siAccessBuf[SI_Q_BUF_LEN] ALIGNED(0x8);
extern OSMesgQueue __osSiAccessQueue ALIGNED(0x8);
extern u32 __osSiAccessQueueEnabled;

void __osSiCreateAccessQueue(void) {
    __osSiAccessQueueEnabled = 1;
    osCreateMesgQueue(&__osSiAccessQueue, siAccessBuf, SI_Q_BUF_LEN);
    osSendMesg(&__osSiAccessQueue, NULL, OS_MESG_NOBLOCK);
}

void __osSiGetAccess(void) {
    OSMesg dummyMesg;
    if (!__osSiAccessQueueEnabled) {
        __osSiCreateAccessQueue();
    }
    osRecvMesg(&__osSiAccessQueue, &dummyMesg, OS_MESG_BLOCK);
}

void __osSiRelAccess(void) {
    osSendMesg(&__osSiAccessQueue, NULL, OS_MESG_NOBLOCK);
}
