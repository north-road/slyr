#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..object_registry import REGISTRY
from ..stream import Stream


class Fields(Object):
    """
    Fields
    """

    @staticmethod
    def cls_id():
        return 'f94f7535-9fdf-11d0-bec7-00805f7c4268'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.fields = []

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        count = stream.read_int('count')
        for i in range(count):
            self.fields.append(stream.read_object('field {}'.format(i + 1)))

        for i, _ in enumerate(self.fields):
            stream.read_int('unknown', expected=(i, 0xffffffff))

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'fields': [f.to_dict() for f in self.fields]
        }

    @classmethod
    def from_dict(cls, definition: dict) -> 'Fields':
        res = Fields()
        for f in definition['fields']:
            res.fields.append(REGISTRY.create_object_from_dict(f))
        return res
