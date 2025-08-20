import argparse
from pathlib import Path
import subprocess
import logging
import tqdm
import yaml

log = logging.getLogger(__name__)


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
        prog="asm-to-c",
        description="Update the YAML from ASM for all C files in a section.",
    )

    # Build to regenerate the ASM and clean everything.
    # If this fails, something is very wrong. This is a sanity check.
    subprocess.run("./build.sh", check=True)

    yaml_file = Path(__file__).parent / "conker/conker.us.yaml"
    asm_yaml_stuff = find_asm_lines(yaml_file, "subsegments")
    for single_filtered_asm_yaml_stuff in tqdm.tqdm(asm_yaml_stuff):
        update_yaml_to_c(yaml_file, single_filtered_asm_yaml_stuff)

    # make extract to convert the ASM to C using splat
    subprocess.run(["make", "extract"], cwd=Path(__file__).parent / "conker", check=True)

    # Sanity check
    subprocess.run("./build.sh", check=True)

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG)
    main()
