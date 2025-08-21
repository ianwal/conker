# Notes

## libultra version

According to [destroythread.c](conker/src/libultra/os/destroythread.c) ifdef, `BUILD_VERSION >= VERSION_J` is NOT true, so CBFD
must use < `VERSION_J`

Also this game contains leodiskinit.c, which was removed in 2.0J.

Currently, I don't have the libultra preprocessor defines set, so I am changing these to compile correctly:

`#if BUILD_VERSION >= VERSION_J` => `#if 0 // BUILD_VERSION >= VERSION_J`

`#if BUILD_VERSION >= VERSION_J` => `#if 1 // BUILD_VERSION < VERSION_J`

At some point these should be reverted and the actual defines should be set for libultra.
