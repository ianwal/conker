#include <ultra64.h>
#include "functions.h"
#include "variables.h"

// TODO: Migrate .bss and .data
// struct __osThreadTail __osThreadTail = { NULL, -1 };
// OSThread* __osRunQueue = (OSThread*)&__osThreadTail;
// OSThread* __osActiveQueue = (OSThread*)&__osThreadTail;
// OSThread* __osRunningThread = NULL;
// OSThread* __osFaultedThread = NULL;

extern struct __osThreadTail __osThreadTail;
extern OSThread* __osRunQueue;
extern OSThread* __osActiveQueue;
extern OSThread* __osRunningThread;
extern OSThread* __osFaultedThread;

void __osDequeueThread(register OSThread** queue, register OSThread* t) {
    register OSThread* pred;
    register OSThread* succ;

    pred = (OSThread*)queue;
    succ = pred->next;

    while (succ != NULL) {
        if (succ == t) {
            pred->next = t->next;
#ifdef _DEBUG
            t->next = NULL;
#endif
            return;
        }
        pred = succ;
        succ = pred->next;
    }
}
