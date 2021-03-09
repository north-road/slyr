# pylint: disable=bad-continuation,too-many-lines

"""
Test symbol parsing
"""

import unittest
import os
import ast
import pprint
from slyr_community.parser.object_registry import ObjectRegistry
from slyr_community.parser.initalize_registry import initialize_registry
from slyr_community.parser.stream import Stream

expected = {
    'cmyk_bin': {
        'C 0 M 0 Y 0 B 100.bin': True,
        'C 0 M 0 Y 0 B 50.bin': True,
        'C 0 M 0 Y 100 B 0.bin': True,
        'C 0 M 0 Y 50 B 0.bin': True,
        'C 0 M 100 Y 0 B 0.bin': True,
        'C 0 M 50 Y 0 B 0.bin': True,
        'C 100 M 0 Y 0 B 0.bin': True,
        'C 15 M 24 Y 33 B 42.bin': True,
        'C 50 M 0 Y 0 B 0.bin': True
    },
    'color_symbol': {
        'color_symbol_blue_band_3.bin': True,
        'color_symbol_green_band_2.bin': True,
        'color_symbol_red_band_1.bin': True
    },
    'fill_bin': {
        '3D Texture fill R255 G0 B0.bin': True,
        'Abandoned irrigated perennial horticulture.bin': True,
        'Black CMYK.bin': True,
        'Black HSV.bin': True,
        'Black cm.bin': True,
        'Black dither non null  no outline.bin': True,
        'Black dither null.bin': True,
        'Black inches.bin': True,
        'Black mm.bin': True,
        'Black null.bin': True,
        'Black outline R0 G0 B0 disabled outline.bin': True,
        'Black outline R0 G0 B0 no color.bin': True,
        'Black outline R0 G0 B0.bin': True,
        'Black.bin': True,
        'Gradient fill Intervals 13 Percent 14 Angle 15.bin': True,
        'Gradient fill buffered.bin': True,
        'Gradient fill circular.bin': True,
        'Gradient fill rectangular.bin': True,
        'Gradient fill.bin': True,
        'Line fill angle 45 offset 3 separation 5.bin': True,
        'Line fill green outline.bin': True,
        'Line fill.bin': True,
        'Marker fill offset 3 4 separation 5 6.bin': True,
        'Marker fill random offset 3 4 separation 5 6.bin': True,
        'Marker fill.bin': True,
        'Picture Fill Circle Angle 45 Scale X 13 Y 14 Fore Red Back Blue.bin': True,
        'Picture Fill Circle Red Outline.bin': True,
        'Picture Fill Circle Swap FgBg.bin': True,
        'Picture Fill Circle X offset -37 Y offset -47 X sep 57 Y sep 67.bin': True,
        'Picture Fill Circle.bin': True,
        'Picture Fill EMF Red Transparent Color.bin': True,
        'Picture Fill EMF.bin': True,
        'Picture Fill Version 4.bin': True,
        'Picture Fill Version 7.bin': True,
        'Picture Fill Version 8 3.bin': True,
        'Picture fill.bin': False,  # This symbol is corrupt
        'R0 G0 B1 dither.bin': True,
        'R0 G0 B1.bin': True,
        'R0 G0 B255 dither.bin': True,
        'R0 G0 B255.bin': True,
        'R0 G1 B0 dither.bin': True,
        'R0 G1 B0.bin': True,
        'R0 G255 B0 dither.bin': True,
        'R0 G255 B0.bin': True,
        'R1 G0 B0 dither.bin': True,
        'R1 G0 B0.bin': True,
        'R1 G1 B1.bin': True,
        'R2 G2 B2.bin': False,  # Color tolerance results in slight difference to expected
        'R254 G254 B254.bin': True,
        'R255 G0 B0 HSV.bin': True,
        'R255 G0 B0 dither.bin': True,
        'R255 G0 B0 layer disabled.bin': True,
        'R255 G0 B0 locked.bin': True,
        'R255 G0 B0 two levels.bin': True,
        'R255 G0 B0 with cartographic line outline.bin': True,
        'R255 G0 B0.bin': True,
        'R255 G255 B255 dither.bin': True,
        'R255 G255 B255 outline R0 G0 B0 dash.bin': True,
        'R255 G255 B255 outline R0 G0 B0 dashdot.bin': True,
        'R255 G255 B255 outline R0 G0 B0 dashdotdot.bin': True,
        'R255 G255 B255 outline R0 G0 B0 dithered.bin': True,
        'R255 G255 B255 outline R0 G0 B0 dot.bin': True,
        'R255 G255 B255 outline R0 G0 B0 null.bin': True,
        'R255 G255 B255 outline R0 G0 B0 width 2.bin': True,
        'R255 G255 B255 outline R0 G0 B0.bin': True,
        'R255 G255 B255 outline R255 G255 B255.bin': True,
        'R255 G255 B255.bin': True,
        'Simple fill with simple outline.bin': True,
        'Simple fill with two layer outline.bin': True,
        'Two layer with two layer outlines.bin': True,
        'many layers.bin': True,
        'v10_5.bin': True
    },
    'hsv_bin': {
        'H 0 S 16 V 25.bin': True,
        'H 115 S 100 V 25.bin': True,
        'H 115 S 16 V 100.bin': True,
        'H 115 S 16 V 25.bin': True,
        'H 350 S 16 V 25.bin': True,
        'H 360 S 16 V 25.bin': True
    },
    'line_bin': {
        '3d simple line symbol width 8.bin': True,
        '3d texture line symbol width 8.bin': True,
        'Cartographic line 3 positions flip all.bin': True,
        'Cartographic line 3 positions flip first.bin': True,
        'Cartographic line 3 positions no flip.bin': True,
        'Cartographic line 4 positions flip first.bin': True,
        'Cartographic line 5 positions flip first.bin': True,
        'Cartographic line bevel join.bin': True,
        'Cartographic line both arrow all flipped.bin': True,
        'Cartographic line both arrow not flipped.bin': True,
        'Cartographic line both arrow.bin': True,
        'Cartographic line end arrow fixed angle.bin': True,
        'Cartographic line end arrow flip all.bin': True,
        'Cartographic line end arrow flip first.bin': True,
        'Cartographic line end arrow.bin': True,
        'Cartographic line offset -4.bin': True,
        'Cartographic line offset 5.bin': True,
        'Cartographic line round join.bin': True,
        'Cartographic line round width 4 disabled.bin': True,
        'Cartographic line round width 4.bin': True,
        'Cartographic line round.bin': True,
        'Cartographic line square pattern interval 7 pattern 0.bin': True,
        'Cartographic line square pattern interval 7 pattern 00.bin': True,
        'Cartographic line square pattern interval 7 pattern 000.bin': True,
        'Cartographic line square pattern interval 7 pattern 001.bin': True,
        'Cartographic line square pattern interval 7 pattern 01.bin': True,
        'Cartographic line square pattern interval 7 pattern 010.bin': True,
        'Cartographic line square pattern interval 7 pattern 011.bin': True,
        'Cartographic line square pattern interval 7 pattern 1.bin': True,
        'Cartographic line square pattern interval 7 pattern 10.bin': True,
        'Cartographic line square pattern interval 7 pattern 100.bin': True,
        'Cartographic line square pattern interval 7 pattern 101.bin': True,
        'Cartographic line square pattern interval 7 pattern 1010.bin': True,
        'Cartographic line square pattern interval 7 pattern 101001000010.bin': True,
        'Cartographic line square pattern interval 7 pattern 11.bin': True,
        'Cartographic line square pattern interval 7 pattern 110.bin': True,
        'Cartographic line square pattern interval 7 pattern 111.bin': True,
        'Cartographic line square pattern interval 7.bin': True,
        'Cartographic line square.bin': True,
        'Cartographic line start arrow all flipped.bin': True,
        'Cartographic line start arrow complex.bin': True,
        'Cartographic line start arrow fixed angle.bin': True,
        'Cartographic line start arrow not flipped.bin': True,
        'Cartographic line start arrow.bin': True,
        'Cartographic line symbol width 8.bin': True,
        'Dash dot dot.bin': True,
        'Dash dot.bin': True,
        'Dashed.bin': True,
        'Dotted.bin': True,
        'Hash line offset -9.bin': True,
        'Hash line round cap.bin': True,
        'Hash line round join.bin': True,
        'Hash line symbol width 8 angle 45.bin': True,
        'Hash line symbol width 8.bin': True,
        'Line disabled.bin': True,
        'Line locked.bin': True,
        'Marker line complex symbol.bin': True,
        'Marker line symbol width 8 interval.bin': True,
        'Marker line symbol width 8 offset -5.bin': True,
        'Marker line symbol width 8 round join.bin': True,
        'Marker line symbol width 8.bin': True,
        'Null.bin': True,
        'Picture Line Check Red_Blue.bin': True,
        'Picture Line Check Scale X 17 Y 19.bin': True,
        'Picture Line Check Swap FgBg.bin': True,
        'Picture Line Check Width 13.bin': True,
        'Picture Line Check.bin': True,
        'Picture line symbol width 8.bin': False,  # corrupt
        'Solid 1.bin': True,
        'Solid 2.bin': True,
        'Three levels.bin': True,
        'Two levels with tags.bin': True,
        'Two levels.bin': True
    },
    'linev2_bin': {
        'lines.bin': True,
        'lines2.bin': True
    },
    'marker_bin': {
        'Arrow marker 12 width 8 offset 7 6 angle 45 red.bin': True,
        'Arrow marker.bin': True,
        'Character marker R255 G0 B0.bin': True,
        'Character marker Unicode 254.bin': True,
        'Character marker angle -35.bin': True,
        'Character marker angle 35.bin': True,
        'Character marker arial.bin': True,
        'Character marker size 16.bin': True,
        'Character marker v2.bin': True,
        'Character marker xoffset 7 yoffset 9.bin': True,
        'Character marker.bin': True,
        'Picture Marker Version 4.bin': True,
        'Picture Marker Version 5.bin': True,
        'Picture Marker Version 8.bin': True,
        'Picture marker.bin': False,  # Symbol is corrupt
        'Picture symbol brick Angle 45 Offset X 13 Y 17.bin': True,
        'Picture symbol brick Red_Blue.bin': True,
        'Picture symbol brick swap FG_BG.bin': True,
        'Picture symbol brick.bin': True,
        'R255 G0 B0 X diamond size 8.bin': True,
        'R255 G0 B0 X marker size 8.bin': True,
        'R255 G0 B0 circle marker size 12 halo size 7 fill.bin': True,
        'R255 G0 B0 circle marker size 12 halo size 7.bin': True,
        'R255 G0 B0 circle marker size 12.bin': True,
        'R255 G0 B0 circle marker size 8 with outline.bin': True,
        'R255 G0 B0 circle marker size 8 xoffset 2.bin': True,
        'R255 G0 B0 circle marker size 8 yoffset 3.bin': True,
        'R255 G0 B0 circle marker size 8.bin': True,
        'R255 G0 B0 cross marker size 8.bin': True,
        'R255 G0 B0 square marker size 8.bin': True,
        'Two layers different outline.bin': True,
        'Two layers with halo.bin': True,
        'Two layers.bin': True
    },
    'ramps_bin': {
        'Algorithmic Color Ramp CIELAB.bin': True,
        'Algorithmic Color Ramp HSV.bin': True,
        'Algorithmic Color Ramp LabLch.bin': True,
        'Algorithmic Color Ramp Red to Green.bin': True,
        'Multi-part Color Ramp.bin': True,
        'Preset Color Ramp 13 colors R_G_B.bin': True,
        'Random Val 12-100 Sat 13-99 Hue 14-360.bin': True,
        'Random Val 12-52 Sat 13-53 Hue 14-54 same everywhere.bin': True,
        'Random Val 12-52 Sat 13-53 Hue 14-54.bin': True
    },
    'symbols3d_bin': {
        '3d simple marker red quality highest.bin': True,
        '3d character marker display face front.bin': True,
        '3d texture fill glacier angle 45.bin': True,
        '3d texture fill glacier.bin': True,
        '3d marker symbol red normalized origin .6 .7 .8.bin': True,
        '3d marker symbol red.bin': True,
        '3d marker symbol red no display face front.bin': True,
        '3d character marker red.bin': True,
        '3d simple marker red width 17.bin': True,
        '3d texture fill glacier height 5.bin': True,
        '3d character marker unicode 34.bin': True,
        '3d simple marker red Sphere Frame.bin': True,
        '3d marker symbol.bin': True,
        '3d simple line tube green width 2.7 quality max.bin': True,
        '3d simple marker red display front face.bin': True,
        '3d simple marker red offset x 11 y 21 z 31.bin': True,
        '3d character marker no keep aspect.bin': True,
        '3d texture fill glacier width 8.bin': True,
        '3d character marker offset 7 8 9.bin': True,
        '3d simple marker red no keep aspect.bin': True,
        '3d simple marker red Cone.bin': True,
        '3d character marker not vertical orientation.bin': True,
        '3d marker symbol red rotation 23 24 25.bin': True,
        '3d simple line wall green width 2.7.bin': True,
        '3d marker symbol red no keep aspect 12 x 14 y 16 z.bin': True,
        '3d marker symbol red rotate x clockwise.bin': True,
        '3d character marker rotation 14 15 16.bin': True,
        '3d simple line tube green width 2.7 quality min.bin': True,
        '3d simple marker red Cylinder.bin': True,
        '3d simple line strip green width 2.7.bin': True,
        '3d simple marker red normalized offset dx.4 dy .6 dz .8.bin': True,
        '3d character marker width 14 x size 16 y depth 0.8z.bin': True,
        '3d simple line tube green width 2.7.bin': True,
        '3d simple marker red quality lowest.bin': True,
        '3d line texture width 2.7 brick red transparent black.bin': True,
        '3d line texture width 2.7 brick vertical alignment.bin': True,
        '3d texture fill glacier red transparent black.bin': True,
        '3d character marker normalized offset 0.2 0.3 0.4.bin': True,
        '3d simple marker red Sphere.bin': True,
        '3d marker symbol red no material draping.bin': True,
        '3d simple marker red Tetrahedron.bin': True,
        '3d simple marker red depth y 23.bin': True,
        '3d simple marker red Diamond.bin': True,
        '3d line texture width 2.7 brick.bin': True,
        '3d simple marker red Cube.bin': True,
        '3d simple marker red size z 27.bin': True,
        '3d marker symbol red offset 21 22 23.bin': True,
        '3d simple marker red rotation x13 y 16 z 19.bin': True,
        '3d marker symbol red no keep aspect.bin': True,
        '3d texture fill glacier outline blue 3.bin': True,
    },

}
initialize_registry()


class TestSymbolParser(unittest.TestCase):
    """
    Test symbol parsing
    """

    maxDiff = None

    UPDATE = False

    @staticmethod
    def read_symbol(_io_stream):
        """
        Reads a symbol from the specified file
        """
        stream = Stream(_io_stream, False, tolerant=False)
        res = stream.read_object('symbol')
        assert stream.tell() == stream.end, (stream.tell, stream.end)
        return res

    def run_symbol_checks(self, path):  # pylint: disable=too-many-locals
        """
        Checks all bin symbols against expectations
        """

        blobs = []
        for fn in os.listdir(path):
            file = os.path.join(path, fn)
            if os.path.isfile(file):
                blobs.append(file)

        for file in blobs:
            folder, symbol_name = os.path.split(file)
            path, group = os.path.split(folder)

            if symbol_name not in expected[group]:
                print("'{}': False,".format(symbol_name))

        for file in blobs:
            print(file)
            folder, symbol_name = os.path.split(file)
            path, group = os.path.split(folder)

            base, _ = os.path.splitext(symbol_name)
            expected_file = os.path.join(folder, 'expected',
                                         base + '.txt')

            with open(file, 'rb') as f:
                expected_symbol = expected[group][symbol_name]
                if not expected_symbol:
                    continue

                symbol = self.read_symbol(f)
                if self.UPDATE:
                    with open(expected_file, 'w') as o:
                        pprint.pprint(symbol.to_dict(), o)
                else:
                    with open(expected_file, 'r') as o:
                        expected_res = ast.literal_eval(o.read())
                    self.assertEqual(expected_res, symbol.to_dict())

    def test_lines(self):
        """
        Test line symbol parsing
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'line_bin')
        self.run_symbol_checks(path)

    def test_fills(self):
        """
        Test fill symbol parsing
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'fill_bin')
        self.run_symbol_checks(path)

    def test_markers(self):
        """
        Test marker symbol parsing
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'marker_bin')
        self.run_symbol_checks(path)

    def test_hsv(self):
        """
        Test HSV symbol parsing
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'hsv_bin')
        self.run_symbol_checks(path)

    def test_cmyk(self):
        """
        Test CMYK symbol parsing
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'cmyk_bin')
        self.run_symbol_checks(path)

    def test_ramps(self):
        """
        Test color ramp parsing
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'ramps_bin')
        self.run_symbol_checks(path)

    def test_color_symbol(self):
        """
        Test color symbol parsing
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'color_symbol')
        self.run_symbol_checks(path)

    def test_linesv2(self):
        """
        Test simple lines v2
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'linev2_bin')
        self.run_symbol_checks(path)

    def test_symbols3d(self):
        """
        Test 3d symbols
        """
        path = os.path.join(os.path.dirname(
            __file__), 'styles', 'symbols3d_bin')
        self.run_symbol_checks(path)

    def test_clsid_parsing(self):
        """
        Test CLSID parsing
        """
        self.assertEqual(ObjectRegistry.clsid_to_hex('7914e603-c892-11d0-8bb6-080009ee4e41'),
                         b'03e6147992c8d0118bb6080009ee4e41')
        self.assertEqual(ObjectRegistry.hex_to_clsid(b'03e6147992c8d0118bb6080009ee4e41'),
                         '7914e603-c892-11d0-8bb6-080009ee4e41')
        self.assertEqual(ObjectRegistry.hex_to_clsid(b'f5883d531a0ad211b27f0000f878229e'),
                         '533d88f5-0a1a-11d2-b27f-0000f878229e')


if __name__ == '__main__':
    unittest.main()
