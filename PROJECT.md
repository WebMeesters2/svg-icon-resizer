# Project Notes

## Purpose

This project converts SVG icons to square SVG files for Home Assistant buttons
and other places where square icons are preferred. It preserves vector content
and aspect ratio while making padding and narrow-logo warnings configurable.

## Analysis

Okay, i have a challenge:

### IST:

1. Obtain an svg logo from a website
2. open it in Inkscape
3. select the image
4. make sure all image-elements are in one group, so later editing will not deform the image
5. shrink the page to the selection with Ctrl-Shift-R
6. open the page-settings with Ctrl-Shift-D
7. Depending on the form of the content i do either
    a. If (almost) square I resize the page to give the content 10% padding, make the page 100% square, so horizontal and vertical dimensions equal. Then center the image on the page and save.
    b. If the image is wide, then make the padding 10% on the horizontal axis, make the vertical size the same. If the vertical content-size becomes less than 30% of the image, make the vertical size leading and resize so the vertical size is about 30%
8. center the image on the page
9. save

That is quite a tedious thing to do if you have many logo's to do.

### SOLL:

Do this programmatically, preferably using Bash + Graphicsmagick, but I heard that has some issues with SVG, so creating a tailor-made program is also an option. Make sure the above values are configurable.

## Architecture

- Main entry point: `svg_icon_resizer.py`; `convert-all-icons.sh` is the fault-tolerant batch wrapper.
- Local visual inspection: `viewer.html`, `viewer.css`, and `viewer.js` provide a dependency-free browser comparison of source and square SVG pages.
- Important data/config files: none; configuration is supplied through CLI options.
- Runtime boundary: Python invokes GraphicsMagick to render and measure visible bounds, maps those pixels to the source `viewBox`, then rewrites only the SVG root viewport.

## Documentation

- Primary user documentation: `README.md`
- Technical/project documentation: `PROJECT.md`
- Examples/templates: usage and viewer instructions in `README.md`
- Protected examples/templates that must not be changed: none documented

## Development Workflow

- Preferred shell/tools: Bash and Python 3; GraphicsMagick is the SVG measurement engine.
- Main setup command: none; the Python implementation uses only the standard library.
- Main build command: none
- Main deployment command: none
- Deliverables are defined by: `README.md`, `PROJECT.md`, and user instructions.

## Validation

- Syntax/compile check: `python3 -m compileall .`
- Test command: `python3 -m unittest discover`
- Lint/typecheck command: `node --check viewer.js` for browser JavaScript syntax
- Other project-specific checks: run the CLI against a representative SVG when GraphicsMagick is available.

## Release Process

- Version source: `svg_icon_resizer.__version__`
- Release notes location: `CHANGELOG.md` and versioned notes under `releases/`; use `.github/RELEASE_NOTES_TEMPLATE.md` for published releases.
- Tagging/deployment steps: commit the validated release, create an annotated `vX.Y.Z` tag, then push the branch and tag.

## Local Rules

- Preserve the source SVG's vector elements; do not use a raster round trip.
- Use GraphicsMagick only to measure a temporary rendering, never to write the output SVG.
- Inputs must define a `viewBox` so raster measurements map back to SVG coordinates.
- Input and output paths must differ.
- `convert-all-icons.sh` reads `icons/*.svg`, writes `icons/square/*.svg`, and attempts every input before reporting aggregate failure.
- The browser viewer must remain usable from `file://` without a build step, web server, or external assets.
- Preserve aspect ratio and the complete drawing even when the configured minimum height ratio is geometrically impossible.

## Open Questions

- Whether future releases need a graphical interface.
- Whether padding should eventually support a unit other than a fraction of the longest drawing dimension.
