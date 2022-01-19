#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class StrArray(Object):
    """
    StrArray
    """

    @staticmethod
    def cls_id():
        return 'a7f92065-36ce-47b6-a463-4763da947cc2'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.strings = []

    def read(self, stream: Stream, version):
        count = stream.read_int('count')
        for i in range(count):
            self.strings.append(stream.read_string('string {}'.format(i + 1)))

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'strings': self.strings
        }

    @classmethod
    def from_dict(cls, definition: dict) -> 'StrArray':
        res = StrArray()
        res.strings = definition['strings']
        return res
