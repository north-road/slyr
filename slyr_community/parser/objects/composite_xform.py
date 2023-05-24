#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class CompositeXForm(Object):
    """
    CompositeXForm
    """

    @staticmethod
    def cls_id():
        return '44923ebb-d988-4847-9b29-11aa8e6e132c'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.transforms = []

    @staticmethod
    def compatible_versions():
        return [1, 2]

    def read(self, stream: Stream, version):
        stream.read_ushort('unknown', expected=0)
        count = stream.read_int('count')
        for i in range(count):
            stream.read_object('transform {}'.format(i + 1))

        if version >= 2:
            stream.read_ushort('unknown flag', expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'transforms': [t.to_dict() for t in self.transforms]
        }
