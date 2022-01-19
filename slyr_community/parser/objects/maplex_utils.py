#!/usr/bin/env python
"""
Maplex utilities and common enums
"""


class MaplexUtils:
    UNIT_MAP = 0
    UNIT_MM = 1
    UNIT_INCH = 2
    UNIT_POINT = 3
    UNIT_PERCENT = 4

    @staticmethod
    def unit_to_string(unit):
        if unit == MaplexUtils.UNIT_MAP:
            return 'map_unit'
        elif unit == MaplexUtils.UNIT_MM:
            return 'mm'
        elif unit == MaplexUtils.UNIT_INCH:
            return 'inch'
        elif unit == MaplexUtils.UNIT_POINT:
            return 'point'
        elif unit == MaplexUtils.UNIT_PERCENT:
            return 'percent'
        return None
