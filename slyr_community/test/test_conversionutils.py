# pylint: disable=bad-continuation,too-many-lines

"""
Test Conversion Utils
"""

import unittest
import os

from .test_case import SlyrTestCase

from ..converters.utils import ConversionUtils
from qgis.PyQt.QtCore import QVariant
from qgis.core import NULL


class TestConversionUtils(SlyrTestCase):
    """
    Test ConversionUtils
    """

    def test_safe_filename(self):
        """
        Test converting strings to safe filenames
        """
        self.assertEqual(
            ConversionUtils.safe_filename("abc DEF 12A.def"), "abc_DEF_12A_def"
        )
        self.assertEqual(
            ConversionUtils.safe_filename("abc §DEF 12üA.def"), "abc__DEF_12u_A_def"
        )



if __name__ == "__main__":
    unittest.main()
