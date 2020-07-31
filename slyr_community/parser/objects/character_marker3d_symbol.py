#!/usr/bin/env python
"""
Serializable object subclass

NEAR COMPLETE INTERPRETATION - all useful components

"""

from slyr_community.parser.objects.symbol_layer import SymbolLayer
from slyr_community.parser.stream import Stream
from slyr_community.parser.objects.units import Units


class CharacterMarker3DSymbol(SymbolLayer):
    """
    CharacterMarker3DSymbol
    """

    @staticmethod
    def cls_id():
        return '6e8ec8f7-e90a-11d5-a129-00508bd60cb9'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.color = None
        self.unicode = 0
        self.units = Units.DISTANCE_INCHES
        self.angle = 0
        self.depth = 0
        self.size = 0
        self.normalized_origin_x = 0
        self.normalized_origin_y = 0
        self.normalized_origin_z = 0
        self.x_offset = 0
        self.y_offset = 0
        self.z_offset = 0
        self.font = None
        self.character_marker_symbol = None
        self.vertical_orientation = False
        self.width = 0
        self.maintain_aspect_ratio = False
        self.billboard_display = False
        self.x_rotation = 0
        self.y_rotation = 0

    @staticmethod
    def compatible_versions():
        return [4]

    def read(self, stream: Stream, version):
        self.color = stream.read_object('color')
        self.unicode = stream.read_int('unicode')
        self.units = stream.read_int('units')
        self.angle = stream.read_double('angle')
        self.size = stream.read_double('size')
        self.depth = stream.read_double('depth')
        self.normalized_origin_x = stream.read_double('normalized origin x')
        self.normalized_origin_y = stream.read_double('normalized origin y')
        self.normalized_origin_z = stream.read_double('normalized origin z')

        self.x_offset = stream.read_double('x offset')
        self.y_offset = stream.read_double('y offset')
        self.z_offset = stream.read_double('z offset')
        self.font = stream.read_object('font')

        self.read_symbol_level(stream)

        stream.read_ushort('unknown', expected=65535)
        self.character_marker_symbol = stream.read_object('character marker')
        self.vertical_orientation = stream.read_uchar('vertical orientation') != 0
        self.x_rotation = stream.read_double('x rotation')
        self.y_rotation = stream.read_double('y rotation')
        self.width = stream.read_double('width')

        self.maintain_aspect_ratio = stream.read_ushort('maintain aspect ratio') != 0
        self.billboard_display = stream.read_ushort('billboard display') != 0

    def to_dict(self):
        return {
            'color': self.color.to_dict() if self.color else None,
            'unicode': self.unicode,
            'units': Units.distance_unit_to_string(self.units),
            'angle': self.angle,
            'depth': self.depth,
            'size': self.size,
            'normalized_origin_x': self.normalized_origin_x,
            'normalized_origin_y': self.normalized_origin_y,
            'normalized_origin_z': self.normalized_origin_z,
            'x_offset': self.x_offset,
            'y_offset': self.y_offset,
            'z_offset': self.z_offset,
            'font': self.font.to_dict() if self.font else None,
            'character_marker_symbol': self.character_marker_symbol.to_dict() if self.character_marker_symbol else None,
            'vertical_orientation': self.vertical_orientation,
            'width': self.width,
            'maintain_aspect_ratio': self.maintain_aspect_ratio,
            'billboard_display': self.billboard_display,
            'x_rotation': self.x_rotation,
            'y_rotation': self.y_rotation
        }
