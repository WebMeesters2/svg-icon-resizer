# svg-icon-resizer

Create padded, square SVG icons without rasterizing or deforming their artwork.

The Python CLI uses the lightweight GraphicsMagick command-line renderer to
measure the visible drawing, then changes only the root SVG viewport. Existing
paths, groups, gradients, text, and other vector elements remain intact.

## Requirements

- Python 3.9 or newer
- GraphicsMagick available as `gm`

GraphicsMagick is deliberately used only for measurement. Its SVG writer is
incomplete (and is unavailable in some builds), so the program never asks it
to generate the output. Python updates the original vector document instead.

## Usage

```bash
python3 svg_icon_resizer.py input.svg output.svg
```

The default adds padding equal to 10% of the drawing's longest dimension on
each side. Both relevant values are configurable:

```bash
python3 svg_icon_resizer.py input.svg output.svg \
  --padding 0.10 \
  --minimum-height-ratio 0.30 \
  --measurement-scale 4
```

`--minimum-height-ratio` reports very wide logos whose visible height occupies
less than the requested share of the square. Such a logo cannot simultaneously
fit in the square, retain its aspect ratio, and meet that minimum; the program
preserves the whole undistorted logo and prints a warning.

`--measurement-scale` controls the temporary raster size used only to find the
visible edges. A higher value gives finer sub-pixel bounds at the cost of more
CPU and memory. The SVG must contain a `viewBox` so pixel measurements can be
mapped back to its vector coordinate system.

To process several files with Bash:

```bash
mkdir -p square
for icon in icons/*.svg; do
  python3 svg_icon_resizer.py "$icon" "square/$(basename "$icon")"
done
```

Input and output must be different paths, preventing accidental replacement of
the original. Run `python3 svg_icon_resizer.py --help` for all options.

## Validation

```bash
python3 -m compileall .
python3 -m unittest discover
```
