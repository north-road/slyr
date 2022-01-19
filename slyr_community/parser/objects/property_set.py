#!/usr/bin/env python
"""
PropertySet

Think of it like a dictionary with typed values.
PARTIAL INTERPRETATION - most common object types are implemented and robust
"""

from ..object import Object
from ..stream import Stream


class PropertySet(Object):
    """
    A set of properties (dict)
    """

    @staticmethod
    def cls_id():
        return '588e5a11-d09b-11d1-aa7c-00c04fa33a15'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.properties = {}

    @staticmethod
    def compatible_versions():
        return [1]

    @staticmethod
    def read_value(stream: Stream):
        key = stream.read_string('key')
        value = stream.read_variant()
        return key, value

    def read(self, stream: Stream, version):
        length = stream.read_uint('length')
        for _ in range(length):
            key, value = PropertySet.read_value(stream)
            self.properties[key] = value

    def to_dict(self):  # pylint: disable=method-hidden
        return self.properties

    @classmethod
    def from_dict(cls, definition: dict) -> 'PropertySet':
        res = PropertySet()
        for k, v in definition.items():
            if k in ('type', 'version'):
                continue

            res.properties[k] = v
        return res
