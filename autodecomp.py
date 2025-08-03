import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
from pprint import pprint
import logging

# Algorithm:
# 1. Input a C file
# 1. Take input asm file.
# 1. Decompile the input asm file using m2c.
# 1. Process the ASM file and fix up as much as possible. Ex. replace ? with s32.
# 1. Write the input asm file back into the C file.
# 1. Try to compile.

log = logging.getLogger(__name__)


@dataclass
class GlobalAsmPragma:
    c_file: Path  # The C File that the pragma is in
    line_no: Path  # The line number in the C file that the pragma is located at.
    asm_path: Path  # The path stored in the GLOBAL_ASM pragma


def get_globalasmpragmas(c_file: Path):
    """Extract all the #pragma GLOBAL_ASM() lines for a C file."""
    with open(c_file) as f:
        lines = f.readlines()

    pragmas: list[GlobalAsmPragma] = []
    for line_no, line in enumerate(lines, start=1):
        if line.startswith("#pragma GLOBAL_ASM"):
            asm_path = re.findall(r'"([^"]*)"', line)[0]
            asm_path = Path(__file__).parent / "conker" / asm_path  # TODO: this is hardcoded and forces script path.
            pragma = GlobalAsmPragma(c_file, line_no, asm_path)
            pragmas.append(pragma)
    return pragmas


def decompile_fn(asm_path: Path):
    """Decompiles an ASM file."""
    DECOMPILER = Path(__file__).parent / "tools/mips_to_c/m2c.py"
    cmd = ["python3", DECOMPILER, asm_path]
    out = subprocess.run(cmd, capture_output=True)
    return out.stdout.decode()


def main():
    parser = argparse.ArgumentParser(
        prog="autodecomp",
        description="Autodecompiles MIPS code.",
        epilog="Text at the bottom of help",
    )
    parser.add_argument("cfile", help="The C file to decompile.", type=str)
    args = parser.parse_args()
    print(args)
    pragmas = get_globalasmpragmas(args.cfile)
    pprint(pragmas)
    if pragmas:
        pragmas = pragmas[:1]  # FIXME: I just want to test one right now.
        for pragma in pragmas:
            raw_decompiled_fn = decompile_fn(pragma.asm_path)

            log.info(f"Raw decompiled fn:\n{raw_decompiled_fn}")

            # Best attempt to make it compile
            decompiled_fn = raw_decompiled_fn.replace("?", "s32")

            log.info(f"Cleaned up decompiled fn:\n{decompiled_fn}")
    else:
        print(f"No #pragma GLOBAL_ASM found in {args.cfile}.")


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG)
    main()
