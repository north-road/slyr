#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from ..exceptions import UnknownClsidException, NotImplementedException, CustomExtensionClsidException


class GroupLayer(Object):
    """
    GroupLayer
    """

    @staticmethod
    def cls_id():
        return 'edad6647-1810-11d1-86ae-0000f8751720'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ''
        self.visible = True
        self.expanded = False
        self.max_scale = 0
        self.min_scale = 0
        # used when a zoom range has been set previously, but is currently disabled
        self.stored_zoom_max = 0
        self.stored_zoom_min = 0
        self.children = []
        self.description = ''
        self.transparency = 0
        self.display_filter = None
        self.use_symbol_levels = False

    @staticmethod
    def compatible_versions():
        return [4, 9, 11, 12]

    def __repr__(self):
        if self.ref_id is not None:
            return '<GroupLayer: {} ({})>'.format(self.name, self.ref_id)
        else:
            return '<GroupLayer: {}>'.format(self.name)

    def read(self, stream: Stream, version):
        self.name = stream.read_string('name')
        self.visible = stream.read_ushort('visible') == 0xffff

        # expanded?
        stream.read_ushort('unknown flag')
        stream.read_ushort('unknown', expected=0)

        self.max_scale = stream.read_double('max scale')
        self.min_scale = stream.read_double('min scale')

        count = stream.read_int('count')
        for i in range(count):
            size = -1
            start = stream.tell()

            if version > 9:
                size = stream.read_int('size') + 8
                stream.read_int('unknown', expected=0)

            try:
                self.children.append(stream.read_object('layer {}'.format(i + 1), expected_size=size))
            except CustomExtensionClsidException as e:
                self.children.append(e.custom_object)
                stream.seek(start + size)

            if not stream.tolerant and size >= 0:
                assert stream.tell() == start + size, (stream.tell(), start + size)

        self.expanded = stream.read_ushort('expanded') != 0
        stream.read_ushort('unknown', expected=0)
        stream.read_int('unknown', expected=0)

        stream.read_double('unknown', expected=0)
        stream.read_ushort('unknown', expected=0)
        stream.read_double('unknown', expected=(-1, 1, 50, 97, 98, 99, 100, 150, 200, 1000, 180000))

        if version > 4:
            remote_count = stream.read_int('remote object count')
            for i in range(remote_count):
                size = stream.read_int('size {}'.format(i)) + 20  # 20 = object header size
                pos = stream.tell()
                stream.read_int('unknown', expected=0)
                try:
                    obj = stream.read_object('remote object', allow_reference=False)
                    assert stream.tell() == pos + size, (size, stream.tell() - pos)
                except NotImplementedException:
                    # don't know this object
                    stream.read(size - 20)
                except (NotImplementedException, UnknownClsidException):
                    # don't know this object
                    stream.read(size - 20)

            self.description = stream.read_string('description')

            self.use_symbol_levels = stream.read_ushort('use symbol levels') != 0
            self.stored_zoom_max = stream.read_double('stored zoom max')
            self.stored_zoom_min = stream.read_double('stored zoom min')

            if version > 9:
                stream.read_ushort('symbol level related flag?')
                self.transparency = stream.read_ushort('transparency')
                stream.read_ushort('checked flag?')
                stream.read_ushort('unknown', expected=0)
                if version >= 12:
                    self.display_filter = stream.read_object('display filter')
            elif version <= 9:
                stream.read_ushort('unknown', expected=65535)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'name': self.name,
            'visible': self.visible,
            'expanded': self.expanded,
            'max_scale': self.max_scale,
            'min_scale': self.min_scale,
            'stored_zoom_min': self.stored_zoom_min,
            'stored_zoom_max': self.stored_zoom_max,
            'children': [c.to_dict() for c in self.children],
            'description': self.description,
            'transparency': self.transparency,
            'display_filter': self.display_filter.to_dict() if self.display_filter else None,
            'use_symbol_levels': self.use_symbol_levels
        }
