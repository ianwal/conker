#include <ultra64.h>
#include "functions.h"
#include "variables.h"


// TODO: Migrate .bss and data
// From https://github.com/decompals/ultralib/blob/48f9f9084e06036f1a613187186c8b0f5b68ce40/src/io/piacs.c#L4

// #define PI_Q_BUF_LEN 1
// u32 __osPiAccessQueueEnabled;
// static OSMesg piAccessBuf[PI_Q_BUF_LEN];
// OSMesgQueue __osPiAccessQueue ALIGNED(0x8);

#define PI_Q_BUF_LEN 1
extern u32 __osPiAccessQueueEnabled;
extern OSMesg piAccessBuf[PI_Q_BUF_LEN];
extern OSMesgQueue __osPiAccessQueue;

void __osPiCreateAccessQueue(void) {
    __osPiAccessQueueEnabled = 1;
    osCreateMesgQueue(&__osPiAccessQueue, piAccessBuf, PI_Q_BUF_LEN);
    osSendMesg(&__osPiAccessQueue, NULL, OS_MESG_NOBLOCK);
}

void __osPiGetAccess(void) {
    OSMesg dummyMesg;
    if (!__osPiAccessQueueEnabled) {
        __osPiCreateAccessQueue();
    }
    osRecvMesg(&__osPiAccessQueue, &dummyMesg, OS_MESG_BLOCK);
}

void __osPiRelAccess(void) {
    osSendMesg(&__osPiAccessQueue, NULL, OS_MESG_NOBLOCK);
}
