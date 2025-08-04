import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
from pprint import pprint
import logging
import tempfile
import shutil

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
    out = subprocess.run(cmd, capture_output=True, check=True)
    return out.stdout.decode()


@dataclass
class CCode:
    """C code."""

    code: list[str]


def get_ccode(c_file: Path):
    with open(c_file) as f:
        return f.read()


def replace_pragma_with_c(c_file: Path, pragma: GlobalAsmPragma, decompiled_fn: CCode):
    "Replace the #pragma GLOBAL_ASM() with C code in the target file."
    with open(c_file) as f:
        lines = f.readlines()
    assert pragma.line_no > 0
    lines.insert(pragma.line_no, "\n")
    for i, line in enumerate(decompiled_fn.code):
        lines.insert(i + pragma.line_no, line)
    lines.pop(pragma.line_no - 1)  # the global_asm line
    print(lines)
    with open(c_file, "w") as f:
        f.writelines(lines)


def main():
    parser = argparse.ArgumentParser(
        prog="autodecomp",
        description="Autodecompiles MIPS code. Currently the goal is to get standalone free-functions working.",
        epilog="Text at the bottom of help",
    )
    parser.add_argument("cfile", help="The C file to decompile.", type=Path)
    args = parser.parse_args()
    print(args)
    pragmas = get_globalasmpragmas(args.cfile)
    pprint(pragmas)
    if pragmas:
        pragmas = pragmas[:1]  # FIXME: I just want to test one right now.
        for pragma in pragmas:
            raw_decompiled_fn = decompile_fn(pragma.asm_path)
            log.info(f"Raw decompiled fn:\n{raw_decompiled_fn}")

            # Do processing to make a best attempt to make the decompiled code compilable.

            # Replace any unknown variables with s32.
            decompiled_fn = raw_decompiled_fn.replace("?", "s32")
            log.info(f"Cleaned up decompiled fn:\n{decompiled_fn}")

            # Remove any duplicate or conflicting extern's from known include files.
            # This avoids "previously declared variable" compiler errors.
            def get_declared_variables():
                known_headers = [
                    Path(__file__).parent / "conker/include" / "variables.h",
                    # Path(__file__).parent / "conker/include" / "structs.h", # TODO
                    # Path(__file__).parent / "conker/include/" / "functions.h", # TODO
                ]  # TODO: Only check headers that are actually included in the c file.
                declared_symbols = []
                for header in known_headers:
                    with open(header) as f:
                        lines = f.readlines()

                    declared_symbols.extend(
                        re.findall(r"^\s*extern\s+[^()]+?\s+\**\w+\s*;", " ".join(lines), re.MULTILINE)
                    )
                res = []
                for line in declared_symbols:
                    line = line.replace("*", "")
                    line = line.replace(";", "")
                    line = line.replace("\n", "")
                    line = line.replace("[]", "")
                    line = line.replace("extern", "")
                    line = line.replace("//", "")
                    for t in ["void", "u8", "s8", "u16", "s16", "u32", "s32", "u64", "s64", "f32", "f64", "int"]:
                        line = line.replace(t, "")
                    line = re.sub(r"\[.*?\]", "", line)
                    line = re.sub(r"\/\*.*?\*\/", "", line)
                    res.append(line)
                return res

            lll = get_declared_variables()
            log.info(lll)
            with tempfile.TemporaryDirectory() as d:
                file_backup = Path(d) / pragma.c_file.name
                shutil.copy2(pragma.c_file, file_backup)
                try:
                    # Replace the pragma in the file
                    replace_pragma_with_c(pragma.c_file, pragma, CCode(decompiled_fn.split("\n")))

                    # Try to build
                except Exception:
                    # If anything bad happens, restore the file.
                    log.error(f"Replacement failed. Restoring file from backup: {pragma.c_file}")
                    shutil.copy2(file_backup, pragma.c_file)
                shutil.copy2(file_backup, pragma.c_file)

    else:
        print(f"No #pragma GLOBAL_ASM found in {args.cfile}.")


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG)
    main()
