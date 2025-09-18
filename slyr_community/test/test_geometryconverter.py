# pylint: disable=bad-continuation,too-many-lines

"""
Test geometry conversion
"""

import unittest

from qgis.core import (
    QgsPoint,
)

from .test_case import SlyrTestCase
from ..converters.geometry import GeometryConverter


class TestGeometryConverter(SlyrTestCase):
    """
    Test Geometry Conversion
    """

    def test_is_ccw(self):
        """
        Test is_clockwise_arc
        """
        # Both points in the 1st quadrant
        # Points on a unit circle in the 1st quadrant
        self.assertTrue(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(0.707, 0.707), QgsPoint(0.866, 0.5), QgsPoint(0, 0)
            )
        )
        self.assertFalse(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(0.866, 0.5), QgsPoint(0.707, 0.707), QgsPoint(0, 0)
            )
        )
        # 2nd quadrant
        self.assertFalse(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(-0.707, 0.707), QgsPoint(-0.866, 0.5), QgsPoint(0, 0)
            )
        )
        self.assertTrue(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(-0.866, 0.5), QgsPoint(-0.707, 0.707), QgsPoint(0, 0)
            )
        )
        # 3rd quadrant
        self.assertTrue(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(-0.707, -0.707), QgsPoint(-0.866, -0.5), QgsPoint(0, 0)
            )
        )
        self.assertFalse(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(-0.866, -0.5), QgsPoint(-0.707, -0.707), QgsPoint(0, 0)
            )
        )
        # 4th quadrant
        self.assertFalse(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(0.707, -0.707), QgsPoint(0.866, -0.5), QgsPoint(0, 0)
            )
        )
        self.assertTrue(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(0.866, -0.5), QgsPoint(0.707, -0.707), QgsPoint(0, 0)
            )
        )

        # adjacent quadrants
        # 1st to 2nd quadrant
        self.assertFalse(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(0.707, 0.707), QgsPoint(-0.707, 0.707), QgsPoint(0, 0)
            )
        )
        self.assertTrue(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(-0.707, 0.707), QgsPoint(0.707, 0.707), QgsPoint(0, 0)
            )
        )
        # 2nd to 3rd quadrant
        self.assertFalse(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(-0.707, 0.707), QgsPoint(-0.707, -0.707), QgsPoint(0, 0)
            )
        )
        self.assertTrue(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(-0.707, -0.707), QgsPoint(-0.707, 0.707), QgsPoint(0, 0)
            )
        )
        # 3rd to 4th quadrant
        self.assertFalse(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(-0.707, -0.707), QgsPoint(0.707, -0.707), QgsPoint(0, 0)
            )
        )
        self.assertTrue(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(0.707, -0.707), QgsPoint(-0.707, -0.707), QgsPoint(0, 0)
            )
        )
        # 4th to 1st quadrant
        self.assertFalse(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(0.707, -0.707), QgsPoint(0.707, 0.707), QgsPoint(0, 0)
            )
        )
        self.assertTrue(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(0.707, 0.707), QgsPoint(0.707, -0.707), QgsPoint(0, 0)
            )
        )

        # opposite quadrants
        # 1st to 3rd quadrant
        self.assertFalse(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(0.707, 0.707), QgsPoint(-0.866, -0.5), QgsPoint(0, 0)
            )
        )
        self.assertTrue(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(-0.866, -0.5), QgsPoint(0.707, 0.707), QgsPoint(0, 0)
            )
        )
        # 2nd to 4th quadrant
        self.assertTrue(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(-0.707, 0.707), QgsPoint(0.866, -0.5), QgsPoint(0, 0)
            )
        )
        self.assertFalse(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(0.866, -0.5), QgsPoint(-0.707, 0.707), QgsPoint(0, 0)
            )
        )

        # on axes
        # Positive X-axis to positive Y-axis
        self.assertFalse(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(1, 0), QgsPoint(0, 1), QgsPoint(0, 0)
            )
        )
        self.assertTrue(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(0, 1), QgsPoint(1, 0), QgsPoint(0, 0)
            )
        )
        # Negative X-axis to negative Y-axis
        self.assertFalse(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(-1, 0), QgsPoint(0, -1), QgsPoint(0, 0)
            )
        )
        self.assertTrue(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(0, -1), QgsPoint(-1, 0), QgsPoint(0, 0)
            )
        )
        # Negative Y-axis to positive X-axis
        self.assertFalse(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(0, -1), QgsPoint(1, 0), QgsPoint(0, 0)
            )
        )
        self.assertTrue(
            GeometryConverter.is_clockwise_arc(
                QgsPoint(1, 0), QgsPoint(0, -1), QgsPoint(0, 0)
            )
        )


if __name__ == "__main__":
    unittest.main()
