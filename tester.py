from clang.cindex import Index, CursorKind, StorageClass
import sys
from pathlib import Path


def get_extern_symbols(file: Path):
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
    for var in variables:
        print(f"{var['name']} ({var['type']}) - Line {var['line']} - extern: {var['is_extern']}")
    return [var["name"] for var in variables]


get_extern_symbols(sys.argv[1])
