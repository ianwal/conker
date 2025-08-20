#!/bin/bash

# personal @ianwall script for running the permuter.

FN_NAME=func_1518CCA8 # Change this as needed

./tools/decomp-permuter/permuter.py nonmatchings/$FN_NAME -j 8 \
    --no-context-output \
    --best-only
