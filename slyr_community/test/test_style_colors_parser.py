# pylint: disable=bad-continuation,too-many-lines

"""
Test color entity parsing from styles
"""

import unittest
import os
from ..parser.initalize_registry import initialize_registry
from ..parser.stream import Stream

expected = {
    "colors_bin": {
        "HSV 60 40 30.bin": {
            "color": {
                "type": "HsvColor",
                "B": 46,
                "G": 77,
                "R": 76,
                "dither": False,
                "is_null": False,
                "version": 1,
            },
        },
        "Gray 47.bin": {
            "color": {
                "type": "GrayColor",
                "B": 47,
                "G": 47,
                "R": 47,
                "dither": False,
                "is_null": False,
                "version": 1,
            },
        },
        "CMYK 10 20 30 40.bin": {
            "color": {
                "type": "CmykColor",
                "C": 10,
                "K": 40,
                "M": 20,
                "Y": 30,
                "dither": False,
                "is_null": False,
                "version": 4,
            },
        },
        "Name - Hot Pink.bin": {
            "color": {
                "type": "HlsColor",
                "B": 181,
                "G": 107,
                "R": 255,
                "dither": False,
                "is_null": False,
                "version": 1,
            },
        },
        "RGB 255 0 0.bin": {
            "color": {
                "type": "RgbColor",
                "B": 0,
                "G": 0,
                "R": 255,
                "dither": False,
                "is_null": False,
                "version": 1,
            },
        },
    }
}

initialize_registry()


class TestStyleColorParser(unittest.TestCase):
    """
    Test style color parsing
    """

    maxDiff = None

    def run_symbol_checks(self, path):
        """
        Checks all bin symbols against expectations
        """

        blobs = []
        for fn in os.listdir(path):
            file = os.path.join(path, fn)
            if os.path.isfile(file):
                blobs.append(file)

        for file in blobs:
            print(file)
            group, symbol_name = os.path.split(file)
            path, group = os.path.split(group)

            with open(file, "rb") as f:
                expected_symbol = expected[group][symbol_name]
                if "skip" in expected_symbol:
                    continue
                stream = Stream(f, debug=False)

                color = stream.read_object()

                self.assertEqual(expected_symbol["color"], color.to_dict())

    def test_colors(self):
        """
        Test line symbol parsing
        """
        path = os.path.join(os.path.dirname(__file__), "styles", "colors_bin")
        self.run_symbol_checks(path)


if __name__ == "__main__":
    unittest.main()
