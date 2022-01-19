#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class ArrayOfFilterDef(Object):
    """
    ArrayOfFilterDef
    """

    @staticmethod
    def cls_id():
        return '3131151a-4b5c-4526-98be-711746b03df8'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    def read(self, stream: Stream, version):
        stream.read_int('count?', expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
        }

    @classmethod
    def from_dict(cls, definition: dict) -> 'ArrayOfFilterDef':
        res = ArrayOfFilterDef()
        return res