# voron-boxturtle-prep

A simple Python script that takes the BoxTurtle STL download and turns it into sorted, ready-to-print folders — no more manually counting `_x4` files or guessing which parts are accent vs primary.

## The Problem

The BoxTurtle STL configurator gives you a zip with nested subdirectories and files like `[a]_guidler_x4.stl`. That means you need to:

- Figure out which files are accent color, primary color, or TPU
- Manually duplicate every `_xN` file to the right quantity
- Dig through subdirectories (Extruder, Idlers, Skirts, Spooler, etc.)

This script does all of that for you in one command.

## What It Does

- Flattens all STLs from nested subdirectories into one place
- Sorts files into `primary/`, `accent/`, and `tpu/` folders
- Expands `_x4`, `_x8`, etc. into individual copies (`motor_plate_1.stl`, `motor_plate_2.stl`, ...)
- Strips the `[a]_` prefix and `_xN` suffix so filenames are clean

Just drag a folder into your slicer and hit print.

## Usage

```bash
python3 boxturtle_stl_sorter.py ~/Downloads/STLs/Base_Build
```

Output goes to a `sorted/` folder by default:

```
sorted/
  primary/    # Main color parts
  accent/     # [a]_ prefixed parts
  tpu/        # Parts with "tpu" in the name
```

### Options

```bash
# Preview without copying anything
python3 boxturtle_stl_sorter.py ~/Downloads/STLs/Base_Build --dry-run

# Custom output location
python3 boxturtle_stl_sorter.py ~/Downloads/STLs/Base_Build --output ~/Desktop/BoxTurtle_Ready
```

## Naming Conventions

| Source filename | Folder | Copies |
|---|---|---|
| `hub.stl` | `primary/` | 1 |
| `[a]_hub.stl` | `accent/` | 1 |
| `extruder_housing_x4.stl` | `primary/` | 4 |
| `[a]_guidler_x4.stl` | `accent/` | 4 |
| `tpu_collet_x4.stl` | `tpu/` | 4 |

## Requirements

Python 3.8+ — no dependencies, just the standard library.

## Credits

Built for the [Armored Turtle BoxTurtle](https://github.com/ArmoredTurtle/BoxTurtle) project. Not affiliated with or endorsed by Armored Turtle.
