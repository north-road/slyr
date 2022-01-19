#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class Place(Object):
    """
    Place
    """

    @staticmethod
    def cls_id():
        return 'f7017459-cab9-4b55-ad77-53123008e097'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ''
        self.extent = None

    def read(self, stream: Stream, version):
        self.name = stream.read_stringv2('name')
        self.extent = stream.read_object('extent')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'name': self.name,
            'extent': self.extent.to_dict() if self.extent else None
        }
