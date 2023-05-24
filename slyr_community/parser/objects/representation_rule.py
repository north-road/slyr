#!/usr/bin/env python
"""
Serializable object subclass
"""
from collections import defaultdict
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
        self.field_overrides = defaultdict(dict)
        self.map_level = 0

    def read(self, stream: Stream, version):
        stream.read_ushort('unknown', expected=2)

        count = stream.read_int('effect count')
        for i in range(count):
            stream.read_string('effect name {}'.format(i+1))
            size = stream.read_int('size {}'.format(i+1))
            stream.read_int('unknown', expected=0)
            start = stream.tell()
            self.effects.append(stream.read_object('effect {}'.format(i + 1)))
            assert stream.tell() == start + size

        total_objects = stream.read_int('total objects')
        count = stream.read_int('layer count', expected=total_objects - len(self.effects))
        for i in range(count):
            self.layers.append(stream.read_object('layer {}'.format(i + 1)))

        field_override_count = stream.read_int('field override count')
        for i in range(field_override_count):
            # note effect_index is 1 based
            effect_index = stream.read_int('effect_index {}'.format(i+1))
            attribute_index = stream.read_int('attribute index {}'.format(i+1))
            field_name = stream.read_string('field name {}'.format(i+1))
            self.field_overrides[effect_index][attribute_index] = field_name

        count = stream.read_int('unknown count', expected=len(self.effects) + len(self.layers))
        for i in range(count):
            stream.read_int('unknown {}'.format(i + 1), expected=i + 1)

        self.map_level = stream.read_int('map level')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'effects': [e.to_dict() for e in self.effects],
            'layers': [e.to_dict() for e in self.layers],
            'field_overrides': dict(self.field_overrides),
            'map_level': self.map_level
        }
