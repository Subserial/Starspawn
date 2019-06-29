# Starspawn

Made with Love, Will, Hate and Fury.
Hides islands you haven't found yet.

Run with `python starspawn.py` to generate an image based on a save in the same folder.

## Flags
All flags are optional.
| Option | Flag | Argument | Description |
|---|---|---|---|---|
| File | -f, --file | path | Specify save file path (default: star.save) |
| Border | -b, --border | none | Enable tiling board in 2x2 |
| Scale | -s, --scale | float | Scale board linearly |
| Visible | -v, --visible | none | Reveal all tiles |
| Radius | -r, --radius | int | Set island detection radius (default 10) |
| Offset | -o, --offset | int, int | Shift board tiles before render |
| Auto | -a, --auto | none | Find offset based on unoccupied rows and columns |
| Tile | -t, --tile | none | Use custom 12x12 tileset (UNOFFICIAL, EXPERIMENTAL) |
| Pixel | -p, --pixel | none | Use pixel tileset |

## Requirements

Pillow (PIL fork) for python

## TODO:

Unexploded Hate blocks are not detected.
Finished gateways are not detected.
