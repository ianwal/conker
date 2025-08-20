#!/bin/bash

# personal @ianwall script for setting up the permuter.
# Run this, then run run_permuter.sh

make -j

C_FILE="game_1B9F30.c"
ASM_FILE="asm/nonmatchings/game_1B9F30/func_1518CCA8.s"

./tools/decomp-permuter/import.py \
    "/workspaces/conker/conker/src/$C_FILE" \
    "/workspaces/conker/conker/$ASM_FILE"
