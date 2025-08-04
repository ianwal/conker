from pathlib import Path

# /workspaces/conker/conker/asm/1E34C0.s

# - [0x122650, asm] --> conker/conker/src/game/done/game_122650.c, asm/nonmatchings/game/done/game_122650/func_150F51E8.s

# TODO: Update yaml for the section to do - [0x1e34c0, c, game_1E34C0]


def to_pragma(fn: str, name: str, section: str):
    return f'#pragma GLOBAL_ASM("asm/nonmatchings/{section}_{name}/{fn}.s")'


def asm_to_c(asm_file: Path, section: str) -> str:
    """Take an entire .s file and convert it into a C file."""
    with open(asm_file) as f:
        asm = f.readlines()
    functions = []
    for line in asm:
        if line.startswith("glabel"):
            fn = line.split(" ")[1].strip()
            functions.append(fn)
    print(functions)
    print(asm_file)
    headers = ["#include <ultra64.h>", '#include "functions.h"', '#include "variables.h"']

    return (
        "\n".join(headers)
        + "\n\n"
        + "\n\n".join([to_pragma(fn, asm_file.split("/")[-1].replace(".s", ""), section) for fn in functions])
    )


def main():
    print(asm_to_c("/workspaces/conker/conker/asm/1E34C0.s", "game"))


if __name__ == "__main__":
    main()
