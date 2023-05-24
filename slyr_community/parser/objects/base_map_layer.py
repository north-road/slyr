#!/usr/bin/env python
"""
Serializable object subclass

NEAR COMPLETE INTERPRETATION - all useful components
"""

from ..object import Object
from ..exceptions import UnknownClsidException
from ..stream import Stream


class BaseMapLayer(Object):
    """
    BaseMapLayer
    """

    @staticmethod
    def cls_id():
        return 'da4122bf-7b07-4158-88b0-19d342bed8ba'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ''
        self.visible = True
        self.description = ''
        self.crs = None
        self.shader_array = None
        self.children = []
        self.extensions = []
        self.zoom_min = 0
        self.zoom_max = 0

        # used when a zoom range has been set previously, but is currently disabled
        self.stored_zoom_max = 0
        self.stored_zoom_min = 0
        self.transparency = 0

        self.show_tips = False
        self.expanded = True
        self.weight = 0
        self.dim_percentage = 0

    @staticmethod
    def compatible_versions():
        return [11]

    def read(self, stream: Stream, version):
        self.name = stream.read_string('name')

        self.visible = stream.read_ushort('visible') != 0
        self.show_tips = stream.read_ushort('show tips') != 0

        self.zoom_max = stream.read_double('zoom max')
        self.zoom_min = stream.read_double('zoom min')

        self.expanded = stream.read_ushort('expanded') != 0

        stream.read_double('unknown')  # ,expected=0)
        stream.read_double('unknown')  # ,expected=0)

        self.crs = stream.read_object('crs')
        self.shader_array = stream.read_object('shader array')

        self.transparency = stream.read_ushort('transparency')

        count = stream.read_int('unknown', expected=(0, 1))
        for i in range(count):
            stream.read_int('size?')
            stream.read_ushort('unknown', expected=0)
            stream.read_int('unknown', expected=1)
            stream.read_int('unknown', expected=0)
            stream.read_int('unknown', expected=0)
            stream.read_int('unknown', expected=0)
            stream.read_int('unknown', expected=0)
            map_count = stream.read_int('map count?')
            for i in range(map_count):
                stream.read_object('unknown (map?)')

        self.dim_percentage = stream.read_ushort('dim percentage')

        count = stream.read_int('count')
        for i in range(count):
            size = stream.read_int('size')
            stream.read_int('unknown', expected=0)
            start = stream.tell()
            self.children.append(stream.read_object('child {}'.format(i + 1)))
            assert stream.tell() == size + start, 'got size {} expected {}'.format(stream.tell() - start, size)

        remote_count = stream.read_int('remote object count')
        for i in range(remote_count):
            size = stream.read_int('size {}'.format(i)) + 20  # 20 = object header size
            pos = stream.tell()
            stream.read_int('unknown', expected=0)
            try:
                obj = stream.read_object('remote object', allow_reference=False)
                self.extensions.append(obj)
                assert stream.tell() == pos + size, (size, stream.tell() - pos)
            except UnknownClsidException:
                # don't know this object
                stream.read(size - 20)
            # NOTE - ServerLayerExtension includes layer copyright text

        self.description = stream.read_string('description')
        self.stored_zoom_max = stream.read_double('stored zoom max')
        self.stored_zoom_min = stream.read_double('stored zoom min')

        self.weight = stream.read_double('layer weight')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'name': self.name,
            'visible': self.visible,
            'description': self.description,
            'zoom_min': self.zoom_min,
            'zoom_max': self.zoom_max,
            'stored_zoom_min': self.stored_zoom_min,
            'stored_zoom_max': self.stored_zoom_max,
            'crs': self.crs.to_dict() if self.crs else None,
            'shader_array': self.shader_array.to_dict() if self.shader_array else None,
            'children': [c.to_dict() for c in self.children],
            'extensions': [e.to_dict() for e in self.extensions],
            'transparency': self.transparency,
            'expanded': self.expanded,
            'show_tips': self.show_tips,
            'weight': self.weight,
            'dim_percentage': self.dim_percentage
        }
