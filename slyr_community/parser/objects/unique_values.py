#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class UniqueValues(Object):
    """
    UniqueValues
    """

    @staticmethod
    def cls_id():
        return '9c81f1c7-792b-467e-ac80-069e4fdf4def'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.values = []

    def read(self, stream: Stream, version):
        stream.read_ushort('unknown', expected=0)
        count = stream.read_int('count')
        for i in range(count):
            variant_type = stream.read_ushort('type {}'.format(i+1))
            stream.read_ushort('unknown')  # , expected=(0, 19, 329))
            stream.read_int('unknown')  # , expected=(0, 50878752))
            stream.read_int('unknown')  # sometimes 0, sometimes same as value?
            stream.read_ushort('unknown')  # , expected=(0, 57824, 62320))
            stream.read_ushort('unknown')  # , expected=(0, 18, 19))
            value = stream.read_variant(variant_type=variant_type, debug_string='value')
            count = stream.read_int('count')
            self.values.append([value, count])

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'values': self.values
        }
