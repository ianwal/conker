# Notes

## libultra version

According to [destroythread.c](conker/src/libultra/os/destroythread.c) ifdef, `BUILD_VERSION >= VERSION_J` is NOT true, so CBFD
must use < `VERSION_J`
