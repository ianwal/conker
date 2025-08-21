#ifndef __MACROS_H__
#define __MACROS_H__

#define ALIGN2(val) ((((s32)val) + 0x1) & ~0x1)
#define ALIGN4(val) ((((s32)val) + 0x3) & ~0x3)
#define ALIGN8(val) ((((s32)val) + 0x7) & ~0x7)
#define ALIGN16(val) ((((s32)val) + 0xF) & ~0xF)

#define ALIGNU16(val) ((((u32)val) + 0xF) & ~0xF)

#define ALIGNED(x) __attribute__((aligned(x)))

#define ARRLEN(x) ((s32)(sizeof(x) / sizeof(x[0])))

#define STUBBED_PRINTF(x) ((void)(x))

#define UNUSED __attribute__((unused))

#ifndef __GNUC__
#define __attribute__(x)
#endif

#define STACK(stack, size) \
    u64 stack[ALIGN8(size) / sizeof(u64)]

#define STACK_START(stack) \
    ((u8*)(stack) + sizeof(stack))

#endif
