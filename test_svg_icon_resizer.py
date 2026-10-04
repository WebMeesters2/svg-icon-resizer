"""Tests for the SVG viewport calculations and markup rewrite."""

import unittest
from unittest.mock import patch
from pathlib import Path
import subprocess

from svg_icon_resizer import (
    ResizeError,
    drawing_bounds,
    rewrite_viewport,
    square_view_box,
    svg_view_box,
)


class SquareViewBoxTests(unittest.TestCase):
    def test_wide_drawing_is_centered_with_padding(self) -> None:
        self.assertEqual(square_view_box((10, 20, 100, 40), 0.1), (0, -20, 120, 120))

    def test_tall_drawing_is_centered_with_padding(self) -> None:
        self.assertEqual(square_view_box((5, 10, 20, 50), 0.0), (-10, 10, 50, 50))

    def test_negative_padding_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            square_view_box((0, 0, 10, 10), -0.1)


class RewriteViewportTests(unittest.TestCase):
    def test_existing_root_dimensions_are_replaced(self) -> None:
        source = '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="20"><path d="M0 0"/></svg>'
        output = rewrite_viewport(source, (-5, -5, 30, 30))
        self.assertIn('viewBox="-5 -5 30 30"', output)
        self.assertIn('width="30"', output)
        self.assertIn('height="30"', output)
        self.assertIn('<path d="M0 0"/>', output)

    def test_non_svg_xml_is_rejected(self) -> None:
        with self.assertRaises(ResizeError):
            rewrite_viewport("<html/>", (0, 0, 1, 1))

    def test_view_box_accepts_spaces_and_commas(self) -> None:
        source = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-10, 20 100,50"/>'
        self.assertEqual(svg_view_box(source), (-10, 20, 100, 50))

    def test_missing_view_box_is_rejected(self) -> None:
        with self.assertRaises(ResizeError):
            svg_view_box('<svg xmlns="http://www.w3.org/2000/svg" width="10"/>')


class DrawingBoundsTests(unittest.TestCase):
    @patch("svg_icon_resizer.shutil.which", return_value="/usr/bin/gm")
    @patch("svg_icon_resizer.subprocess.run")
    def test_gradient_paint_is_simplified_for_measurement(self, run, _which) -> None:
        run.return_value = subprocess.CompletedProcess([], 0, "400 200 200x100+100+50", "")
        svg = '<svg viewBox="0 0 40 20"><path fill="url(#gradient)"/></svg>'

        bounds = drawing_bounds(Path("logo.svg"), svg)

        self.assertEqual(bounds, (10, 5, 20, 10))
        self.assertEqual(run.call_args.kwargs["input"], '<svg viewBox="0 0 40 20"><path fill="black"/></svg>')
        self.assertIn("svg:-", run.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
