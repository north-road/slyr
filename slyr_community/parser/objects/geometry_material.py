#!/usr/bin/env python
"""
Serializable object subclass
"""

from slyr_community.parser.object import Object
from slyr_community.parser.stream import Stream
from slyr_community.parser.objects.picture import BmpPicture


class GeometryMaterial(Object):
    """
    GeometryMaterial
    """

    @staticmethod
    def cls_id():
        return '0e6f4b27-2bd0-11d6-a4cc-444553547777'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.transparency = 0
        self.color = None
        self.transparent_texture_color = None
        self.picture = None

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        has_picture = stream.read_int('has picture') != 0
        stream.read_int('unknown')
        stream.read_int('unknown')
        stream.read_int('unknown')
        stream.read_int('unknown')
        stream.read_int('unknown')
        stream.read_int('unknown')
        stream.read_int('unknown')
        stream.read_int('unknown')
        self.transparency = stream.read_double('transparency')
        self.color = stream.read_object('color')
        self.transparent_texture_color = stream.read_object('transparent texture color')
        if has_picture:
            self.picture = BmpPicture()
            self.picture.read(stream, 1)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'transparency': self.transparency,
            'color': self.color.to_dict() if self.color else None,
            'transparent_texture_color': self.transparent_texture_color.to_dict() if self.transparent_texture_color else None,
            'picture': self.picture.to_dict() if self.picture else None
        }
