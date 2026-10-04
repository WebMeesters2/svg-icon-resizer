# Changelog

## 0.2.0 - 2026-10-04

### Added

- Fault-tolerant batch conversion from `icons/` to `icons/square/`.
- Dependency-free browser viewer for side-by-side SVG page inspection.
- Explicit page boundaries, alternate backgrounds, SVG metadata, filtering, and keyboard navigation in the viewer.

### Changed

- Local source and generated icon SVGs are excluded from Git.
- Batch conversion now attempts every input before reporting aggregate failures.

## 0.1.0 - 2026-10-04

### Added

- Python CLI for centering SVG artwork in a padded square viewport.
- Fast GraphicsMagick-based visible drawing measurement while preserving the original SVG markup.
- Configurable padding and minimum visible-height warning.
- Compatibility handling for SVG gradient paints during measurement.
- Unit tests and documented validation commands.
