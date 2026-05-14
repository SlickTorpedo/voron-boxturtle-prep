#!/usr/bin/env python3
"""
BoxTurtle STL Sorter & Multiplier

Sorts BoxTurtle STL files into folders by material/color and duplicates
files based on the _xN suffix so you can just drag a whole folder into
your slicer and hit print.

Naming conventions it understands:
  - [a]_filename.stl  → accent color
  - tpu in the name   → TPU folder
  - _x4, _x8, etc.    → duplicated into that many copies
  - everything else    → primary color

Usage:
  python boxturtle_stl_sorter.py /path/to/stl/folder
  python boxturtle_stl_sorter.py /path/to/stl/folder --output /path/to/output

Output structure:
  output/
    primary/
    accent/
    tpu/
"""

import argparse
import os
import re
import shutil
from pathlib import Path


def classify_file(filename: str) -> str:
    """Determine which folder a file belongs in."""
    lower = filename.lower()
    if "tpu" in lower:
        return "tpu"
    if lower.startswith("[a]_"):
        return "accent"
    return "primary"


def parse_quantity(filename: str) -> int:
    """Extract the xN quantity from a filename, default 1."""
    match = re.search(r"_x(\d+)", filename, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 1


def clean_name(filename: str) -> str:
    """Strip the [a]_ prefix and _xN suffix to get a clean base name."""
    name = filename
    # Remove [a]_ prefix (case-insensitive)
    if name.lower().startswith("[a]_"):
        name = name[4:]
    # Remove _xN suffix (before .stl)
    name = re.sub(r"_x\d+", "", name, flags=re.IGNORECASE)
    return name


def process_files(input_dir: Path, output_dir: Path, dry_run: bool = False):
    """Sort and multiply STL files into organized folders."""
    # Always search recursively — BoxTurtle STLs are nested in subdirs
    stl_files = sorted(input_dir.rglob("*.stl"))

    if not stl_files:
        print(f"No .stl files found in {input_dir}")
        return

    # Set up output folders
    folders = {
        "primary": output_dir / "primary",
        "accent": output_dir / "accent",
        "tpu": output_dir / "tpu",
    }

    if not dry_run:
        for folder in folders.values():
            folder.mkdir(parents=True, exist_ok=True)

    # Track stats
    stats = {"primary": 0, "accent": 0, "tpu": 0}
    total_files = 0

    # Track used names per folder to avoid collisions
    used_names: dict[str, set[str]] = {k: set() for k in folders}

    print(f"Processing {len(stl_files)} STL file(s) from {input_dir}\n")
    print(f"{'Source File':<45} {'→ Folder':<10} {'Qty':<5} {'Output Names'}")
    print("─" * 100)

    for stl in stl_files:
        category = classify_file(stl.name)
        qty = parse_quantity(stl.name)
        base = clean_name(stl.name)
        stem = Path(base).stem
        suffix = Path(base).suffix or ".stl"

        output_names = []
        if qty == 1:
            final_name = f"{stem}{suffix}"
            # Handle collision
            if final_name in used_names[category]:
                i = 1
                while f"{stem}_{i}{suffix}" in used_names[category]:
                    i += 1
                final_name = f"{stem}_{i}{suffix}"

            used_names[category].add(final_name)
            output_names.append(final_name)

            if not dry_run:
                shutil.copy2(stl, folders[category] / final_name)
        else:
            for n in range(1, qty + 1):
                final_name = f"{stem}_{n}{suffix}"
                # Handle collision (unlikely but safe)
                while final_name in used_names[category]:
                    n_alt = int(re.search(r"_(\d+)\.", final_name).group(1)) + 1  # type: ignore
                    final_name = f"{stem}_{n_alt}{suffix}"

                used_names[category].add(final_name)
                output_names.append(final_name)

                if not dry_run:
                    shutil.copy2(stl, folders[category] / final_name)

        stats[category] += len(output_names)
        total_files += len(output_names)

        # Truncate long output name lists for display
        names_display = ", ".join(output_names[:3])
        if len(output_names) > 3:
            names_display += f", ... ({len(output_names)} total)"

        print(f"{stl.name:<45} {'→ ' + category:<10} {qty:<5} {names_display}")

    # Summary
    print("\n" + "─" * 100)
    print(f"\nDone! {total_files} total files across {len(stl_files)} source STLs\n")
    for cat, count in stats.items():
        if count > 0:
            print(f"  {folders[cat]}/  →  {count} file(s)")

    if dry_run:
        print("\n  (Dry run — no files were actually copied)")


def main():
    parser = argparse.ArgumentParser(
        description="Sort & multiply BoxTurtle STL files into material/color folders"
    )
    parser.add_argument("input", type=Path, help="Folder containing BoxTurtle STL files")
    parser.add_argument(
        "--output", "-o", type=Path, default=None,
        help="Output folder (default: <input>/sorted)"
    )
    parser.add_argument(
        "--dry-run", "-n", action="store_true",
        help="Preview what would happen without copying files"
    )
    args = parser.parse_args()

    input_dir = args.input.resolve()
    if not input_dir.is_dir():
        print(f"Error: {input_dir} is not a directory")
        return

    output_dir = (args.output or input_dir / "sorted").resolve()

    if output_dir == input_dir:
        print("Error: output directory can't be the same as input")
        return

    process_files(input_dir, output_dir, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
