#!/usr/bin/env python
"""
Serializable object subclass
"""

from slyr_community.parser.objects.symbol_layer import SymbolLayer
from slyr_community.parser.stream import Stream


class SimpleMarker3DSymbol(SymbolLayer):
    """
    SimpleMarker3DSymbol
    """
    TETRAHEDRON = 0
    CUBE = 1
    CONE = 2
    CYLINDER = 3
    DIAMOND = 4
    SPHERE = 5
    SPHERE_FRAME = 6

    @staticmethod
    def cls_id():
        return '773f7270-aefb-11d5-8112-00c04fa0adf8'

    @staticmethod
    def type_to_string(symbol_type) -> str:
        """
        Converts a symbol type to a string representation
        """
        type_map = {
            SimpleMarker3DSymbol.TETRAHEDRON: 'tetrahedron',
            SimpleMarker3DSymbol.CUBE: 'cube',
            SimpleMarker3DSymbol.CONE: 'cone',
            SimpleMarker3DSymbol.CYLINDER: 'cylinder',
            SimpleMarker3DSymbol.DIAMOND: 'diamond',
            SimpleMarker3DSymbol.SPHERE: 'sphere',
            SimpleMarker3DSymbol.SPHERE_FRAME: 'sphere_frame',
        }
        assert symbol_type in type_map
        return type_map[symbol_type]

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.width = 0
        self.color = None
        self.quality = 0
        self.billboard_display = False
        self.x_offset = 0
        self.y_offset = 0
        self.z_offset = 0
        self.keep_aspect_ratio = True
        self.dx = 0
        self.dy = 0
        self.dz = 0
        self.depth_y = 0
        self.size_z = 0
        self.z_rotation = 0
        self.x_rotation = 0
        self.y_rotation = 0
        self.type = 0

    @staticmethod
    def compatible_versions():
        return [6]

    def read(self, stream: Stream, version):
        self.color = stream.read_object('color')
        self.size_z = stream.read_double('size z')
        self.type = stream.read_int('type', expected=(0, 1, 2, 3, 4, 5, 6))
        self.quality = stream.read_double('quality')  # 0->1

        self.symbol_level = SymbolLayer.read_symbol_level(stream)

        self.z_rotation = stream.read_double('z rotation')
        self.x_offset = stream.read_double('x offset')
        self.y_offset = stream.read_double('y offset')
        self.z_offset = stream.read_double('z offset')
        stream.read_ushort('unknown', expected=65535)

        self.dx = stream.read_double('dx')
        self.dy = stream.read_double('dy')
        self.dz = stream.read_double('dz')

        self.x_rotation = stream.read_double('x rotation')
        self.y_rotation = stream.read_double('y rotation')

        self.width = stream.read_double('width')

        self.depth_y = stream.read_double('depth y')
        self.keep_aspect_ratio = stream.read_ushort('keep aspect ratio') != 0
        self.billboard_display = stream.read_ushort('display front face') != 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'width': self.width,
            'quality': self.quality,
            'color': self.color.to_dict() if self.color else None,
            'symbol_type': SimpleMarker3DSymbol.type_to_string(self.type),
            'billboard_display': self.billboard_display,
            'x_offset': self.x_offset,
            'y_offset': self.y_offset,
            'z_offset': self.z_offset,
            'keep_aspect_ratio': self.keep_aspect_ratio,
            'dx': self.dx,
            'dy': self.dy,
            'dz': self.dz,
            'depth_y': self.depth_y,
            'size_z': self.size_z,
            'z_rotation': self.z_rotation,
            'x_rotation': self.x_rotation,
            'y_rotation': self.y_rotation
        }
