#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class RepresentationRule(Object):
    """
    RepresentationRule
    """

    @staticmethod
    def cls_id():
        return '1079e40a-83c1-467b-b828-e5c06ef5f6b7'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.effects = []
        self.layers = []
        self.map_level = 0

    def read(self, stream: Stream, version):
        stream.read_ushort('unknown', expected=2)
        count = stream.read_int('count')
        for i in range(count):
            stream.read_string('unknown', expected='Move')
            stream.read_int('unknown', expected=22)
            stream.read_int('unknown', expected=0)
            self.effects.append(stream.read_object('effect {}'.format(i + 1)))

        total_objects = stream.read_int('total objects')
        count = stream.read_int('layer count', expected=total_objects - len(self.effects))
        for i in range(count):
            self.layers.append(stream.read_object('layer {}'.format(i + 1)))

        stream.read_int('unknown', expected=0)
        count = stream.read_int('unknown count', expected=len(self.effects) + len(self.layers))
        for i in range(count):
            stream.read_int('unknown {}'.format(i + 1), expected=i + 1)
        self.map_level = stream.read_int('map level')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
        }
