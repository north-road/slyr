#!/usr/bin/env python

# /***************************************************************************
# crs.py
# ----------
# Date                 : March 2020
# copyright            : (C) 2020 by Nyall Dawson
# email                : nyall.dawson@gmail.com
#
#  ***************************************************************************/
#
# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

"""
Numeric format conversion
"""

from typing import Optional


try:
    from qgis.core import QgsBasicNumericFormat
except ImportError:
    QgsBasicNumericFormat = None

from ..parser.objects.numeric_format import NumericFormat
from .context import Context


class NumericFormatConverter:
    """
    Converts NumericFormat to QgsNumericFormat
    """

    @staticmethod
    def convert_format(numeric_format: NumericFormat, context: Context):
        """
        Converts NumericFormat to QgsNumericFormat
        """
        if not numeric_format:
            return None

        if numeric_format.__class__.__name__ not in (
            "NumericFormat",
            "CIMNumericFormat",
        ):
            context.push_warning(
                "{} format conversion is not yet supported".format(
                    numeric_format.__class__.__name__
                ),
                level=Context.WARNING,
            )
            return None

        res = QgsBasicNumericFormat()

        res.setNumberDecimalPlaces(numeric_format.rounding_value or 0)
        if numeric_format.rounding == 0:
            res.setRoundingType(QgsBasicNumericFormat.RoundingType.DecimalPlaces)
        elif numeric_format.rounding == 1:
            res.setRoundingType(QgsBasicNumericFormat.RoundingType.SignificantFigures)

        res.setShowThousandsSeparator(numeric_format.thousands)
        res.setShowPlusSign(numeric_format.show_plus_sign)
        res.setShowTrailingZeros(numeric_format.zero_pad)
        return res

    @staticmethod
    def decimal_precision_from_format(numeric_format: NumericFormat) -> Optional[int]:
        """
        Extracts the decimal precision from a numeric format
        """
        if numeric_format.__class__.__name__ == "NumericFormat":
            return numeric_format.rounding_value
        elif numeric_format.__class__.__name__ == "LatLonFormat":
            return numeric_format.rounding_value

        return None
