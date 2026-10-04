#!/usr/bin/env python3
"""Center an SVG drawing on a configurable square viewport."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

__version__ = "0.2.0"


class ResizeError(RuntimeError):
    """Raised when an SVG cannot be measured or rewritten safely."""


def svg_view_box(svg: str) -> tuple[float, float, float, float]:
    """Read the coordinate system required to map rendered pixels back to SVG units."""
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as error:
        raise ResizeError(f"Input is not well-formed XML: {error}") from error
    value = root.get("viewBox")
    if value is None:
        raise ResizeError("SVG must have a viewBox attribute")
    try:
        numbers = tuple(float(part) for part in re.split(r"[\s,]+", value.strip()))
    except ValueError as error:
        raise ResizeError("SVG has an invalid viewBox") from error
    if len(numbers) != 4 or not all(math.isfinite(number) for number in numbers):
        raise ResizeError("SVG has an invalid viewBox")
    if numbers[2] <= 0 or numbers[3] <= 0:
        raise ResizeError("SVG viewBox width and height must be positive")
    return numbers


def drawing_bounds(
    input_path: Path,
    svg: str,
    graphicsmagick: str = "gm",
    measurement_scale: float = 4,
) -> tuple[float, float, float, float]:
    """Render with GraphicsMagick and map its pixel trim box to SVG coordinates."""
    if measurement_scale <= 0:
        raise ValueError("measurement scale must be greater than zero")
    executable = shutil.which(graphicsmagick)
    if executable is None:
        raise ResizeError(f"GraphicsMagick executable not found: {graphicsmagick}")

    # GraphicsMagick 1.3 rejects some otherwise valid SVG gradients. Bounds do
    # not depend on their colors, so replace paint-server colors only in the
    # temporary measurement input. The original markup is never changed.
    measurement_svg = re.sub(
        r"((?:fill|stroke)\s*(?:=|:)\s*([\"'])?)url\([^)]*\)",
        lambda match: f"{match.group(1)}black",
        svg,
        flags=re.IGNORECASE,
    )
    source = "svg:-" if measurement_svg != svg else str(input_path)
    result = subprocess.run(
        [
            executable,
            "convert",
            "-background",
            "none",
            source,
            "-resize",
            f"{measurement_scale * 100:g}%",
            "-format",
            "%w %h %@",
            "info:-",
        ],
        capture_output=True,
        text=True,
        input=measurement_svg if source == "svg:-" else None,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown GraphicsMagick error"
        raise ResizeError(f"Could not measure {input_path}: {detail}")

    match = re.fullmatch(
        r"\s*(\d+)\s+(\d+)\s+(\d+)x(\d+)([+-]\d+)([+-]\d+)\s*",
        result.stdout,
    )
    if match is None:
        raise ResizeError(f"GraphicsMagick returned invalid bounds for {input_path}")
    image_width, image_height, trim_width, trim_height, offset_x, offset_y = (
        int(value) for value in match.groups()
    )
    if image_width <= 0 or image_height <= 0 or trim_width <= 0 or trim_height <= 0:
        raise ResizeError(f"The drawing in {input_path} has no visible area")

    view_x, view_y, view_width, view_height = svg_view_box(svg)
    return (
        view_x + offset_x * view_width / image_width,
        view_y + offset_y * view_height / image_height,
        trim_width * view_width / image_width,
        trim_height * view_height / image_height,
    )


def square_view_box(
    bounds: tuple[float, float, float, float], padding: float
) -> tuple[float, float, float, float]:
    """Build a centered square viewBox with padding on every side."""
    if padding < 0:
        raise ValueError("padding must be zero or greater")
    x, y, width, height = bounds
    side = max(width, height) * (1 + 2 * padding)
    return (
        x + width / 2 - side / 2,
        y + height / 2 - side / 2,
        side,
        side,
    )


def _format_number(value: float) -> str:
    """Format an SVG coordinate without unnecessary trailing zeroes."""
    return f"{value:.12g}"


def _replace_attribute(tag: str, name: str, value: str) -> str:
    """Replace or append one attribute in an SVG root start tag."""
    pattern = re.compile(rf"(\s{re.escape(name)}\s*=\s*)([\"']).*?\2", re.DOTALL)
    if pattern.search(tag):
        return pattern.sub(lambda match: f'{match.group(1)}"{value}"', tag, count=1)
    insertion = tag.rfind("/>")
    if insertion < 0:
        insertion = tag.rfind(">")
    return f'{tag[:insertion]} {name}="{value}"{tag[insertion:]}'


def rewrite_viewport(svg: str, view_box: tuple[float, float, float, float]) -> str:
    """Return SVG text with a square root viewport and unchanged child markup."""
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as error:
        raise ResizeError(f"Input is not well-formed XML: {error}") from error
    if root.tag.rsplit("}", 1)[-1] != "svg":
        raise ResizeError("Input root element is not <svg>")

    match = re.search(r"<svg(?=\s|>)[^>]*>", svg, flags=re.IGNORECASE | re.DOTALL)
    if match is None:
        raise ResizeError("Could not locate the SVG root start tag")

    x, y, width, height = view_box
    numbers = " ".join(_format_number(value) for value in (x, y, width, height))
    tag = match.group(0)
    tag = _replace_attribute(tag, "viewBox", numbers)
    tag = _replace_attribute(tag, "width", _format_number(width))
    tag = _replace_attribute(tag, "height", _format_number(height))
    output = f"{svg[:match.start()]}{tag}{svg[match.end():]}"
    try:
        ET.fromstring(output)
    except ET.ParseError as error:
        raise ResizeError(f"Generated SVG is not well-formed XML: {error}") from error
    return output


def resize_file(
    input_path: Path,
    output_path: Path,
    padding: float,
    minimum_height_ratio: float,
    graphicsmagick: str,
    measurement_scale: float,
) -> str | None:
    """Measure and rewrite one SVG, returning an optional aspect-ratio warning."""
    if not 0 < minimum_height_ratio <= 1:
        raise ValueError("minimum height ratio must be greater than 0 and at most 1")
    svg = input_path.read_text(encoding="utf-8")
    bounds = drawing_bounds(input_path, svg, graphicsmagick, measurement_scale)
    view_box = square_view_box(bounds, padding)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rewrite_viewport(svg, view_box), encoding="utf-8")

    height_ratio = bounds[3] / view_box[3]
    if height_ratio < minimum_height_ratio:
        return (
            f"visible height is {height_ratio:.1%}, below the requested "
            f"{minimum_height_ratio:.1%}; increasing it would clip or distort this logo"
        )
    return None


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Center an SVG drawing in a padded square viewport without rasterizing it."
    )
    parser.add_argument("input", type=Path, help="source SVG file")
    parser.add_argument("output", type=Path, help="destination SVG file")
    parser.add_argument(
        "--padding",
        type=float,
        default=0.10,
        help="padding on each side as a fraction of the longest drawing dimension (default: 0.10)",
    )
    parser.add_argument(
        "--minimum-height-ratio",
        type=float,
        default=0.30,
        help="warn when visible content is less than this fraction of the square (default: 0.30)",
    )
    parser.add_argument(
        "--measurement-scale",
        type=float,
        default=4,
        help="raster measurement scale; higher is more precise but slower (default: 4)",
    )
    parser.add_argument(
        "--graphicsmagick",
        default="gm",
        help="GraphicsMagick executable name or path (default: gm)",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return its process exit status."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.input.resolve() == args.output.resolve():
        parser.error("input and output must be different files")
    if not args.input.is_file():
        parser.error(f"input file does not exist: {args.input}")
    try:
        warning = resize_file(
            args.input,
            args.output,
            args.padding,
            args.minimum_height_ratio,
            args.graphicsmagick,
            args.measurement_scale,
        )
    except (OSError, ResizeError, ValueError) as error:
        parser.exit(1, f"error: {error}\n")
    if warning:
        print(f"warning: {warning}", file=sys.stderr)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
