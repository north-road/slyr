# pylint: disable=bad-continuation,too-many-lines

"""
Test Conversion Utils
"""

import unittest

from .test_case import SlyrTestCase

from qgis.core import QgsCoordinateReferenceSystem

from ..converters.context import Context
from ..converters.crs import CrsConverter
from ..parser.initalize_registry import initialize_registry

initialize_registry()


class TestCrsConverter(SlyrTestCase):
    """
    Test CRS Conversion
    """

    def test_crs_from_number(self):
        context = Context()
        self.assertIsNone(CrsConverter.crs_from_srs_number(None, context))
        self.assertIsNone(CrsConverter.crs_from_srs_number(0, context))
        self.assertIsNone(CrsConverter.crs_from_srs_number(-1111, context))
        self.assertEqual(
            CrsConverter.crs_from_srs_number(3857, context),
            QgsCoordinateReferenceSystem("EPSG:3857"),
        )
        self.assertEqual(
            CrsConverter.crs_from_srs_number(54042, context),
            QgsCoordinateReferenceSystem("ESRI:54042"),
        )


if __name__ == "__main__":
    unittest.main()
