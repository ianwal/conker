import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
from pprint import pprint
import logging
import tempfile
import shutil
import json
import tqdm
import yaml
from clang.cindex import Index, CursorKind, StorageClass

# Algorithm:
# 1. Input a C file
# 1. Take input asm file.
# 1. Decompile the input asm file using m2c.
# 1. Process the ASM file and fix up as much as possible. Ex. replace ? with s32.
# 1. Write the input asm file back into the C file.
# 1. Try to compile.

log = logging.getLogger(__name__)


# I just realized splat does this for you when you update yaml to C and build, lol. Don't use this.
def convert_s_to_c(asm_file: Path, section: str) -> str:
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

    def to_pragma(fn: str, name: str, section: str):
        return f'#pragma GLOBAL_ASM("asm/nonmatchings/{section}_{name}/{fn}.s")'

    return (
        "\n".join(headers)
        + "\n\n"
        + "\n\n".join([to_pragma(fn, str(asm_file).split("/")[-1].replace(".s", ""), section) for fn in functions])
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
                            "raw_line": line,
                            "segment": "game",  # TODO: MAKE THIS NOT HARDCODED!!
                        }
                    )
            except yaml.YAMLError as exc:
                print(f"ERROR: {exc}")
                pass  # Skip lines that don't parse correctly

    return res


def get_extern_variables_raw(file: Path):
    """Get all symbols marked extern from a given header/source file."""

    def find_vars(node):
        vars = []
        for c in node.get_children():
            if c.kind == CursorKind.VAR_DECL:
                vars.append(
                    {
                        "name": c.spelling,
                        "type": c.type.spelling,
                        "line": c.location.line,
                        "storage_class": c.storage_class,
                    }
                )
            vars.extend(find_vars(c))
        return vars

    index = Index.create()
    tu = index.parse(
        file,
        args=[
            "-x",
            "c",
            "-std=c89",
            # "-I.",
            # "-I/workspaces/conker/conker/include/2.0L/ultra64.h",
            # "-I/workspaces/conker/conker/include/2.0L",
            # "-I/workspaces/conker/conker/include/",
            # "-I/workspaces/conker/conker/include/libc",
            # "-D_LANGUAGE_C",
        ],
    )

    # Optional: print diagnostics
    for diag in tu.diagnostics:
        print(f"[Diagnostic] {diag}")

    variables = find_vars(tu.cursor)
    res = []
    for var in variables:
        # print(f"{var['name']} ({var['type']}) - Line {var['line']}")
        res.append(var)
    return res


def get_extern_symbols(file: Path):
    """Get all symbols marked extern from a given header/source file."""

    def find_vars(node):
        vars = []
        for c in node.get_children():
            if c.kind == CursorKind.VAR_DECL:
                vars.append(
                    {
                        "name": c.spelling,
                        "type": c.type.spelling,
                        "line": c.location.line,
                        "is_extern": c.storage_class == StorageClass.EXTERN,
                    }
                )
            vars.extend(find_vars(c))
        return vars

    index = Index.create()
    tu = index.parse(
        file,
        args=[
            "-x",
            "c",
            "-std=c11",
            "-I.",
            "-I/workspaces/conker/conker/include/2.0L/ultra64.h",
            "-I/workspaces/conker/conker/include/2.0L",
            "-I/workspaces/conker/conker/include/",
            "-I/workspaces/conker/conker/include/libc",
            "-D_LANGUAGE_C",
        ],
    )

    # Optional: print diagnostics
    for diag in tu.diagnostics:
        print(f"[Diagnostic] {diag}")

    variables = find_vars(tu.cursor)
    res = []
    for var in variables:
        print(f"{var['name']} ({var['type']}) - Line {var['line']} - extern: {var['is_extern']}")
        res.append(var["name"])
    return res


@dataclass
class GlobalAsmPragma:
    c_file: Path  # The C File that the pragma is in
    line_no: Path  # The line number in the C file that the pragma is located at.
    asm_path: Path  # The path stored in the GLOBAL_ASM pragma

    def to_dict(self):
        return {"c_file": str(self.c_file), "line_no": self.line_no, "asm_path": str(self.asm_path)}

    @staticmethod
    def from_dict(data):
        return GlobalAsmPragma(
            c_file=Path(data["c_file"]), line_no=int(data["line_no"]), asm_path=Path(data["asm_path"])
        )


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
    if not asm_path.exists():
        raise ValueError(
            f"ASM path doesn't exist: {asm_path}. Make sure you ran `make extract` and that the file has a #pragma GLOBAL_ASM for the specified asm file."
        )
    cmd = ["python3", DECOMPILER, asm_path]
    out = subprocess.run(cmd, capture_output=True, check=True)
    # TODO: Handle decompile failures. They can happen.
    # Example:
    #     Traceback (most recent call last):
    #   File "/workspaces/conker/autodecomp.py", line 422, in <module>
    #   File "/workspaces/conker/autodecomp.py", line 332, in main
    #     raw_decompiled_fn = decompile_fn(pragma.asm_path)
    #                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #   File "/workspaces/conker/autodecomp.py", line 225, in decompile_fn
    #     out = subprocess.run(cmd, capture_output=True, check=True)
    #           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #   File "/usr/lib/python3.12/subprocess.py", line 571, in run
    #     raise CalledProcessError(retcode, process.args,
    # subprocess.CalledProcessError: Command '['python3', PosixPath('/workspaces/conker/tools/mips_to_c/m2c.py'), PosixPath('/workspaces/conker/conker/asm/nonmatchings/game_50D80/func_1502460C.s')]' returned non-zero exit status 1.
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
        lines.insert(i + pragma.line_no, line + "\n")
    lines.pop(pragma.line_no - 1)  # the global_asm line
    with open(c_file, "w") as f:
        f.writelines(lines)


def replace_line(file: Path, new_line: str, line_no: int):
    with open(file) as f:
        lines = f.readlines()
    assert line_no > 0
    lines.insert(line_no, "\n")
    lines.insert(line_no, new_line)
    lines.pop(line_no - 1)  # the global_asm line
    with open(file, "w") as f:
        f.writelines(lines)


def generate_mips_context(c_file: Path):
    cmd = [
        "python3",
        Path(__file__).parent / "conker/tools/ctx.py",
        c_file,
    ]
    subprocess.run(cmd, check=True)
    return Path(__file__).parent / "conker/ctx.c"


def update_yaml_to_c(file: Path, line_stuff: dict):
    with open(file, "r") as f:
        lines = f.readlines()

    lines[line_stuff["line_no"] - 1] = line_stuff["raw_line"].replace(
        "asm", f"c, {line_stuff['segment']}_{line_stuff['address'][2:].upper()}"
    )  # TODO: game --> {section}

    with open(file, "w+t") as f:
        f.writelines(lines)


def main():
    parser = argparse.ArgumentParser(
        prog="autodecomp",
        description="Autodecompiles MIPS code. Currently the goal is to get standalone free-functions working.",
        epilog="Text at the bottom of help",
    )
    parser.add_argument("cfile", help="The C file to decompile.", type=Path, nargs="?")
    args = parser.parse_args()
    print(args)
    # pragmas = get_globalasmpragmas(args.cfile)

    # Build to regenerate the ASM and clean everything.
    subprocess.run("./build.sh", check=True)

    CREATE_C_FILE = True
    if CREATE_C_FILE:
        yaml_file = Path(__file__).parent / "conker/conker.us.yaml"
        asm_yaml_stuff = find_asm_lines(yaml_file, "subsegments")
        target_address = "0x50D80"
        filtered_asm_yaml_stuff = list(filter(lambda x: x["address"].lower() == target_address.lower(), asm_yaml_stuff))
        single_filtered_asm_yaml_stuff = filtered_asm_yaml_stuff[
            0
        ]  # TODO: I want to do this iteratively, but for now do one.
        print(single_filtered_asm_yaml_stuff)
        # convert_s_to_c(
        #    Path(__file__).parent / f"conker/asm/{asm_yaml_stuff[0]['address'][2:].upper()}.s", asm_yaml_stuff[0]["segment"]
        # )
        update_yaml_to_c(yaml_file, single_filtered_asm_yaml_stuff)
        # Build to make splat generate the C file from the updated YAML (really I only need "make extract")
        subprocess.run("./build.sh", check=True)
        c_file_name = f"{single_filtered_asm_yaml_stuff['segment']}_{single_filtered_asm_yaml_stuff['address'][2:].upper()}"  # TODO: Hardcoded stuff I think
        c_file = Path(__file__).parent / "conker/src" / f"{c_file_name}.c"  # TODO: Hardcoded section I think
    else:
        c_file = args.cfile

    assert c_file
    pragmas = get_globalasmpragmas(c_file)
    pprint(pragmas)
    return
    if not pragmas:
        print(f"No #pragma GLOBAL_ASM found in {args.cfile}.")
    for pragma in tqdm.tqdm(pragmas, desc="Auto-decomp", colour="#00ff00"):
        # Build to regenerate the ASM and clean everything.
        subprocess.run("./build.sh", check=True)

        raw_decompiled_fn = decompile_fn(pragma.asm_path)
        log.info(f"Raw decompiled fn:\n{raw_decompiled_fn}")

        # Do processing to make a best attempt to make the decompiled code compilable.

        # Replace any unknown variables with s32.
        decompiled_fn = raw_decompiled_fn.replace("?", "s32")
        log.info(f"Cleaned up decompiled fn:\n{decompiled_fn}")

        # Remove any duplicate or conflicting extern's from known include files.
        # This avoids "previously declared variable" compiler errors.
        # lll = get_declared_variables()
        # log.info(get_extern_variables_raw(pragma.c_file))

        log.info("Generating MIPS context")
        # TODO: Only generate context up to the line in the file. If stuff is declared in that file AFTER the newly decompiled function,
        #       we can't see it in this function, so we don't want it to show up in the context.
        ctx_variables = get_extern_variables_raw(generate_mips_context(pragma.c_file))
        log.info(ctx_variables)
        pre_decomp_variables = get_extern_variables_raw(pragma.c_file)
        log.info(len(pre_decomp_variables))

        success = True
        with tempfile.TemporaryDirectory() as d:
            file_backup = Path(d) / pragma.c_file.name
            shutil.copy2(pragma.c_file, file_backup)
            try:
                # Replace the pragma in the file
                replace_pragma_with_c(pragma.c_file, pragma, CCode(decompiled_fn.split("\n")))
                post_decomp_variables = get_extern_variables_raw(pragma.c_file)
                log.info(len((post_decomp_variables)))
                # for each variable, if the variable was there before WITH THE SAME TYPE, ignore it.
                # if it has a different type, then find it and remove it.
                vars_to_remove = []
                pre_decomp_variable_names = tuple([var["name"] for var in pre_decomp_variables])
                ctx_variable_names = tuple(var["name"] for var in ctx_variables)
                for post_decomp_var in post_decomp_variables:
                    if post_decomp_var["name"] not in pre_decomp_variable_names and post_decomp_var["name"] not in [
                        ctx_variable_names
                    ]:
                        vars_to_remove.append(post_decomp_var)
                # log.info(f"Vars to remove: {vars_to_remove}")
                log.info(len(vars_to_remove))
                for var in vars_to_remove:
                    replace_line(pragma.c_file, "// REMOVED", var["line"])
                log.info(f"Replaced '{len(vars_to_remove)}' lines.")

                # Try to build
                subprocess.run("./build.sh", check=True)
            except Exception:
                success = False
                # If anything bad happens, restore the file, then build.
                log.error(f"Replacement failed. Restoring file from backup: {pragma.c_file}")
                shutil.copy2(file_backup, pragma.c_file)
                # Build to regenerate the ASM for the next try.
                subprocess.run("./build.sh", check=True)
            shutil.copy2(file_backup, pragma.c_file)
            # Build to regenerate the ASM for the next try.
            subprocess.run("./build.sh", check=True)

            # Write the result to a JSON.
            json_file = Path(__file__).parent / "success.json"
            if success:
                log.info(f"Auto-decomp succeeded for: {pragma}")
            else:
                log.error(f"Auto-decomp failed for: {pragma}")
                json_file = Path(__file__).parent / "fail.json"

            asm_list: list[GlobalAsmPragma] = []
            if json_file.exists():
                with open(json_file, "r") as f:
                    data = json.load(f)
                    asm_list: list[GlobalAsmPragma] = [GlobalAsmPragma.from_dict(entry) for entry in data]
            asm_list.append(pragma)

            with open(json_file, "w") as f:
                json.dump([entry.to_dict() for entry in asm_list], f, indent=2)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG)
    main()
