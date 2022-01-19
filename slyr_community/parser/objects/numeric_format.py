#!/usr/bin/env python
"""
Numeric field formats

PARTIAL INTERPRETATION - some common subclasses not implemented yet.
Implemented subclasses are robust.
"""
from ..object import Object
from ..stream import Stream


class NumericFormat(Object):
    """
    Numeric format
    """

    ALIGNMENT = {
        0: 'ALIGN_RIGHT',
        1: 'ALIGN_LEFT'
    }

    ROUNDING = {
        0: 'ROUND_NUMBER_OF_DECIMALS',
        1: 'ROUND_NUMBER_OF_SIGNIFICANT_DIGITS'
    }

    @staticmethod
    def cls_id():
        return '7e4f4719-8e54-11d2-aad8-000000000'

    def __init__(self):
        super().__init__()
        self.alignment = 0
        self.alignment_width = 12
        self.rounding = 0
        self.rounding_value = 6
        self.show_plus_sign = False
        self.zero_pad = False
        self.thousands = False

    @staticmethod
    def compatible_versions():
        return [1]

    def read(self, stream: Stream, version):
        self.rounding = stream.read_uint('rounding')
        self.rounding_value = stream.read_uint('rounding value')
        self.alignment = stream.read_ulong('alignment')
        self.alignment_width = stream.read_ulong('alignment width')
        self.thousands = stream.read_ushort('thousands') != 0
        self.zero_pad = stream.read_ushort('zero pad') != 0
        self.show_plus_sign = stream.read_ushort('show plus sign') != 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'alignment': NumericFormat.ALIGNMENT[self.alignment],
            'alignment_width': self.alignment_width,
            'rounding': NumericFormat.ROUNDING[self.rounding],
            'rounding_value': self.rounding_value,
            'show_plus_sign': self.show_plus_sign,
            'zero_pad': self.zero_pad,
            'thousands': self.thousands,
        }


class FractionFormat(Object):
    """
    FractionFormat
    """

    OPTION = {
        0: 'SPECIFY_DIGITS',
        1: 'SPECIFY_DENOMINATOR'
    }

    @staticmethod
    def cls_id():
        return '7e4f471c-8e54-11d2-aad8-000000000'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.option = 0
        self.digits = 1

    def read(self, stream: Stream, version):
        self.option = stream.read_int('option')
        self.digits = stream.read_int('digits')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'option': FractionFormat.OPTION[self.option],
            'digits': self.digits
        }


class DirectionFormat(Object):
    """
    DirectionFormat
    """

    DIRECTION_TYPES = {
        1: 'DIRECTION_TYPE_NORTH_AZIMUTH',
        2: 'DIRECTION_TYPE_SOUTH_AZIMUTH',
        3: 'DIRECTION_TYPE_POLAR',
        4: 'DIRECTION_TYPE_QUADRANT',
    }

    UNITS = {
        2: 'UNITS_DECIMAL_DEGREES',
        3: 'UNITS_DEGREES_MINUTES_SECONDS',
        9101: 'UNITS_RADIANS',
        9105: 'UNITS_GRADIANS',
        9106: 'UNITS_GONS'
    }

    FORMAT = {
        0: 'FORMAT_DEGREES_MINUTES_SECONDS',
        1: 'FORMAT_QUADRANT_BEARING'
    }

    @staticmethod
    def cls_id():
        return '36d7e361-b440-4feb-b2ac-fede1a2fd7a7'

    def __init__(self):
        super().__init__()
        self.direction_type = 1
        self.decimal_places = 0
        self.units = 2
        self.format = 0

    def read(self, stream: Stream, version):
        self.units = stream.read_uint('units')
        self.direction_type = stream.read_uint('direction type')
        self.format = stream.read_uint('format')
        self.decimal_places = stream.read_uint('decimal places')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'direction_type': DirectionFormat.DIRECTION_TYPES[self.direction_type],
            'decimal_places': self.decimal_places,
            'units': DirectionFormat.UNITS[self.units],
            'format': DirectionFormat.FORMAT[self.format]
        }


class AngleFormat(NumericFormat):
    """
    AngleFormat
    """

    @staticmethod
    def cls_id():
        return '7e4f471e-8e54-11d2-aad8-000000000'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.field_in_degrees = False
        self.display_in_degrees = False

    @staticmethod
    def compatible_versions():
        return [3]

    def read(self, stream: Stream, version):
        self.field_in_degrees = stream.read_ushort('field_in_degrees') == 65535
        super_version = stream.read_ushort('super version')
        super().read(stream, super_version)
        self.display_in_degrees = stream.read_ushort('display in degrees') == 65535

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res['field_in_degrees'] = self.field_in_degrees
        res['display_in_degrees'] = self.display_in_degrees
        return res


class PercentageFormat(NumericFormat):
    """
    PercentageFormat
    """

    @staticmethod
    def cls_id():
        return '7e4f471b-8e54-11d2-aad8-000000000'

    def __init__(self):
        super().__init__()
        self.adjust_percentage = False

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        self.adjust_percentage = stream.read_ushort('adjust percentage') != 0
        super_version = stream.read_ushort('super version')
        super().read(stream, super_version)

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res['adjust_percentage'] = self.adjust_percentage
        return res


class CustomNumberFormat(Object):
    """
    CustomNumberFormat
    """

    @staticmethod
    def cls_id():
        return '7e4f4722-8e54-11d2-aad8-000000000'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.format = ''

    def read(self, stream: Stream, version):
        self.format = stream.read_string('format')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'format': self.format
        }


class CurrencyFormat(Object):
    """
    CurrencyFormat
    """

    @staticmethod
    def cls_id():
        return '7e4f471a-8e54-11d2-aad8-000000000'

    def read(self, stream: Stream, version):
        pass

    def to_dict(self):  # pylint: disable=method-hidden
        return {
        }


class LatLonFormat(NumericFormat):
    """
    LatLonFormat
    """

    @staticmethod
    def cls_id():
        return '7e4f471d-8e54-11d2-aad8-000000000'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.show_directions = False
        self.is_latitude = False
        self.show_zero_minutes = False
        self.show_zero_seconds = False

    @staticmethod
    def compatible_versions():
        return [3, 4]

    def read(self, stream: Stream, version):
        self.show_directions = stream.read_ushort('show directions') != 0
        self.is_latitude = stream.read_ushort('is latitude') != 0
        self.show_zero_minutes = stream.read_ushort('show zero minutes') != 0
        self.show_zero_seconds = stream.read_ushort('show zero seconds') != 0

        super_version = stream.read_ushort('super version')
        super().read(stream, super_version)

        if version > 3:
            stream.read_ushort('unknown', expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res['show_directions'] = self.show_directions
        res['is_latitude'] = self.is_latitude
        res['show_zero_minutes'] = self.show_zero_minutes
        res['show_zero_seconds'] = self.show_zero_seconds
        return res


class RateFormat(NumericFormat):
    """
    RateFormat
    """

    @staticmethod
    def cls_id():
        return '7e4f4721-8e54-11d2-aad8-000000000'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.rate = 0
        self.suffix = ''

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        self.rate = stream.read_double('rate')
        self.suffix = stream.read_string('suffix')
        super_version = stream.read_ushort('super version')
        super().read(stream, super_version)

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res['rate'] = self.rate
        res['suffix'] = self.suffix
        return res


class ScientificFormat(Object):
    """
    ScientificFormat
    """

    @staticmethod
    def cls_id():
        return '7e4f471f-8e54-11d2-aad8-000000000'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.decimals = 0

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        self.decimals = stream.read_int('decimals')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'decimals': self.decimals
        }
