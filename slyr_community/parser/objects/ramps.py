#!/usr/bin/env python
"""
Color ramps

COMPLETE INTERPRETATION
"""

from slyr_community.parser.object import Object


class ColorRamp(Object):
    """
    Base class for color ramps
    """

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.ramp_name_type = ''

    def to_dict(self) -> dict:  # pylint: disable=method-hidden
        """
        Returns a dictionary representation of the color
        :return:
        """
        return {}


class RandomColorRamp(ColorRamp):
    """
    Random color ramp
    """

    @staticmethod
    def cls_id():
        return 'beb87094-c0b4-11d0-8379-080009b996cc'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.same_everywhere = False
        self.val_min = 0
        self.val_max = 100
        self.sat_min = 0
        self.sat_max = 100
        self.hue_min = 0
        self.hue_max = 360

    def read(self, stream, version):
        self.ramp_name_type = stream.read_stringv2('ramp name type')

        stream.read(4)
        self.same_everywhere = bool(stream.read_ushort('Same everywhere'))
        stream.read(4)
        self.val_min = stream.read_ushort('val min')
        self.val_max = stream.read_ushort('val max')
        self.sat_min = stream.read_ushort('sat min')
        self.sat_max = stream.read_ushort('sat max')
        self.hue_min = stream.read_ushort('hue min')
        self.hue_max = stream.read_ushort('hue max')

    def to_dict(self):  # pylint: disable=method-hidden
        return {'value_range': [self.val_min, self.val_max], 'saturation_range': [self.sat_min, self.sat_max],
                'hue_range': [self.hue_min, self.hue_max], 'same_everywhere': self.same_everywhere}


class PresetColorRamp(ColorRamp):
    """
    Preset color ramp
    """

    @staticmethod
    def cls_id():
        return 'beb8709a-c0b4-11d0-8379-080009b996cc'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.ramp_name_type = ''
        self.colors = []

    def children(self):
        res = super().children()
        res.extend(self.colors)
        return res

    def read(self, stream, version):
        self.ramp_name_type = stream.read_stringv2('ramp name type')

        stream.read(4)

        color_count = stream.read_uint('Number of colors')
        for i in range(color_count):
            self.colors.append(stream.read_object('Color {}'.format(i + 1)))

    def to_dict(self):  # pylint: disable=method-hidden
        return {'colors': [c.to_dict() for c in self.colors]}


class MultiPartColorRamp(ColorRamp):
    """
    Multi-part color ramp
    """

    @staticmethod
    def cls_id():
        return 'beb87099-c0b4-11d0-8379-080009b996cc'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.parts = []
        self.part_lengths = []

    @staticmethod
    def compatible_versions():
        return [1, 2]

    def children(self):
        res = super().children()
        for p in self.parts:
            if p:
                res.append(p)
        return res

    def read(self, stream, version):
        self.ramp_name_type = stream.read_stringv2('ramp name type')
        count = stream.read_uint('Number of parts')
        for i in range(count):
            self.parts.append(stream.read_object('Part {}'.format(i + 1)))

        if version > 1:
            for i in range(count):
                self.part_lengths.append(stream.read_double('Length {}'.format(i + 1)))

    def to_dict(self):  # pylint: disable=method-hidden
        return {'parts': [p.to_dict() for p in self.parts],
                'part_lengths': self.part_lengths}


class AlgorithmicColorRamp(ColorRamp):
    """
    Algorithmic color ramp
    """

    ALGORITHM_CIELAB = 1
    ALGORITHM_HSV = 0
    ALGORITHM_LABLCH = 2

    @staticmethod
    def cls_id():
        return 'beb8709b-c0b4-11d0-8379-080009b996cc'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.ramp_name_type = ''
        self.algorithm = None
        self.color1 = None
        self.color2 = None

    @staticmethod
    def compatible_versions():
        return [1]

    def children(self):
        res = super().children()
        if self.color1:
            res.append(self.color1)
        if self.color2:
            res.append(self.color2)
        return res

    def read(self, stream, version):
        self.ramp_name_type = stream.read_stringv2('ramp name type')
        self.algorithm = stream.read_uint('Algorithm')
        self.color1 = stream.read_object('Color 1')
        self.color2 = stream.read_object('Color 2')

    def to_dict(self):  # pylint: disable=method-hidden
        return {'color1': self.color1.to_dict(),
                'color2': self.color2.to_dict(),
                'algorithm': self.algorithm}
