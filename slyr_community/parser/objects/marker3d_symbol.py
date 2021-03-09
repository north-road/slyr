#!/usr/bin/env python
"""
Serializable object subclass
"""
from slyr_community.parser.objects.symbol_layer import SymbolLayer
from slyr_community.parser.stream import Stream


class Marker3DSymbol(SymbolLayer):
    """
    Marker3DSymbol
    """

    @staticmethod
    def cls_id():
        return '773f7274-aefb-11d5-8112-00c04fa0adf8'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.color = None
        self.geometry = None
        self.display_face_front = True
        self.keep_aspect = True
        self.material_draping = True
        self.size_x = 0
        self.size_y = 0
        self.size_z = 0
        self.origin_x = 0
        self.origin_y = 0
        self.origin_z = 0
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_z = 0
        self.offset_x = 0
        self.offset_y = 0
        self.offset_z = 0
        self.picture = None

    @staticmethod
    def compatible_versions():
        return [6, 7, 8, 9]

    def read(self, stream: Stream, version):
        self.color = stream.read_object('color')
        self.size_z = stream.read_double('size z')

        self.geometry = stream.read_object('multipatch')

        stream.read_int('unknown', expected=9)

        self.origin_x = stream.read_double('origin x')
        self.origin_y = stream.read_double('origin y')
        self.origin_z = stream.read_double('origin z')
        self.material_draping = stream.read_ushort('no material draping') == 0

        stream.read_int('unknown', expected=13)
        stream.read_int('unknown', expected=0)

        self.rotation_z = stream.read_double('rotation z')
        self.offset_x = stream.read_double('offset x')
        self.offset_y = stream.read_double('offset y')
        self.offset_z = stream.read_double('offset z')

        stream.read_ushort('unknown', expected=65535)

        self.picture = stream.read_object('picture')

        self.rotation_x = stream.read_double('rotation x')
        self.rotation_y = stream.read_double('rotation y')
        self.size_x = stream.read_double('size x')
        self.size_y = stream.read_double('size y')
        self.keep_aspect = stream.read_ushort('keep aspect') != 0

        stream.read_ushort('unknown', expected=0)
        if version == 7:
            return

        self.display_face_front = stream.read_ushort('display face front') != 0
        if version < 7:
            stream.read_int('unknown', expected=0)
            stream.read_double('unknown')
            stream.read_ushort('unknown', expected=0)
            stream.read_ushort('unknown', expected=65535)

        if version > 8:
            stream.read_ushort('unknown', expected=0)
            stream.read_int('unknown', expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'color': self.color.to_dict() if self.color else None,
            'geometry': self.geometry.to_dict() if self.geometry else None,
            'display_face_front': self.display_face_front,
            'keep_aspect': self.keep_aspect,
            'material_draping': self.material_draping,
            'size_x': self.size_x,
            'size_y': self.size_y,
            'size_z': self.size_z,
            'origin_x': self.origin_x,
            'origin_y': self.origin_y,
            'origin_z': self.origin_z,
            'rotation_x': self.rotation_x,
            'rotation_y': self.rotation_y,
            'rotation_z': self.rotation_z,
            'offset_x': self.offset_x,
            'offset_y': self.offset_y,
            'offset_z': self.offset_z,
            'picture': self.picture.to_dict() if self.picture else None
        }
