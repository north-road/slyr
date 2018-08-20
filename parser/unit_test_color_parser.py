import unittest
from color_parser import (cielab_to_xyz, xyz_to_rgb, cielab_to_rgb)


class TestColorParser(unittest.TestCase):
    """The LAB values are obtained from the color selector in ArcMap"""

    def test_lab_to_rgb_red(self):
        r, g, b = cielab_to_rgb(
            56.547017615341,
            76.8994334713463,
            68.1034442713808)

        self.assertEqual(255.0, r)
        self.assertEqual(0.0, g)
        self.assertEqual(0.0, b)

    def test_lab_to_rgb_green(self):
        r, g, b = cielab_to_rgb(
            85.6070742290004,
            -91.4861929759672,
            73.9622026853808)

        self.assertEqual(0.0, r)
        self.assertEqual(255.0, g)
        self.assertEqual(0.0, b)

    def test_lab_to_rgb_blue(self):
        r, g, b = cielab_to_rgb(
            34.6689828323685,
            71.1255602213487,
            -101.887893082443)

        self.assertEqual(0.0, r)
        self.assertEqual(0.0, g)
        self.assertEqual(255.0, b)

    def test_lab_to_rgb_grey(self):
        r, g, b = cielab_to_rgb(
            60.3512433104593,
            0.0,
            0.0)

        self.assertEqual(127.0, r)
        self.assertEqual(127.0, g)
        self.assertEqual(127.0, b)

    def test_lab_to_rgb_random_pink(self):
        r, g, b = cielab_to_rgb(
            61.3159233343074,
            87.5007924739545,
            -47.2983051839587)

        self.assertEqual(242.0, r)
        self.assertEqual(13.0, g)
        self.assertEqual(232.0, b)

    def test_lab_to_rgb_lut(self):
        r, g, b = cielab_to_rgb(
            0.869,
            14.067,
            -21.3789)

        self.assertEqual(0, r)
        self.assertEqual(2, g)
        self.assertEqual(20, b)

    def test_lab_to_rgb_lut2(self):
        r, g, b = cielab_to_rgb(
            32.6742, 51.5019, 45.4267)

        self.assertEqual(131, r)
        self.assertEqual(2, g)
        self.assertEqual(2, b)

    def test_lab_to_rgb_lut3(self):
        r, g, b = cielab_to_rgb(
            32.67421111111, 51.50189999999, 45.4267000001)

        self.assertEqual(131, r)
        self.assertEqual(2, g)
        self.assertEqual(2, b)


if __name__ == '__main__':
    unittest.main()
