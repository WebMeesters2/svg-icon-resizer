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

To process every SVG in `icons/`:

```bash
./convert-all-icons.sh
```

Results are written to `icons/square/`. The batch script continues when an
individual icon fails, prints a final summary and the failed paths, and exits
with status 1 after the batch if any conversion failed. An empty input folder
is treated as a successful no-op.

Input and output must be different paths, preventing accidental replacement of
the original. Run `python3 svg_icon_resizer.py --help` for all options.

## Browser viewer

Open `viewer.html` directly in a current browser on Windows or Linux, then
choose the `icons/` folder. No web server or installation is required.

The viewer pairs each `icons/*.svg` source with `icons/square/*.svg`, displays
them side by side, and draws a yellow border around each SVG page. It also
provides:

- checkerboard, light, and dark canvas backgrounds;
- source and output `viewBox`, width, height, and file size;
- a warning when a converted output is missing or its page is not square;
- filename filtering, adjustable preview size, and arrow-key navigation.

Browsers do not allow a local page to scan folders automatically. Choose the
folder again to refresh the viewer after running `convert-all-icons.sh`.

## Validation

```bash
python3 -m compileall .
python3 -m unittest discover
node --check viewer.js
```
