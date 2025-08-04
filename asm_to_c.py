from pathlib import Path
import yaml

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


def find_asm_lines(yaml_file, section):
    asm_line_numbers = []

    with open(yaml_file, "r") as f:
        lines = f.readlines()
        data = yaml.safe_load("".join(lines))

    in_section = False
    res = []
    for idx, line in enumerate(lines):
        stripped = line.strip()

        # Check if we're entering the subsegments section
        if stripped.startswith(f"{section}:"):
            in_section = True
            continue

        # Exit section block when we hit something else at the same indentation level or less
        if in_section and (not stripped.startswith("-") and stripped != ""):
            in_section = False
            continue

        # While inside the section list, check for 'asm' as second element
        if in_section and stripped.startswith("- ["):
            try:
                # Try to parse the line as a YAML list
                parsed = yaml.safe_load(stripped.lstrip("- "))
                if isinstance(parsed, list) and len(parsed) > 1 and len(parsed) < 3 and parsed[1] == "asm":
                    asm_line_numbers.append(idx + 1)  # +1 because line numbers are 1-based
                    res.append(
                        {
                            "address": hex(parsed[0]),
                            "line_no": idx + 1,
                            "raw_line": {line},
                        }
                    )
            except yaml.YAMLError as exc:
                print(f"ERROR: {exc}")
                pass  # Skip lines that don't parse correctly

    return res


def main():
    # print(asm_to_c("/workspaces/conker/conker/asm/1E34C0.s", "game"))
    asm_lines = find_asm_lines("/workspaces/conker/conker/conker.us.yaml", "subsegments")


if __name__ == "__main__":
    main()
