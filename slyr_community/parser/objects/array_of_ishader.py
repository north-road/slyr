#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class ArrayOfIShader(Object):
    """
    ArrayOfIShader
    """

    @staticmethod
    def cls_id():
        return 'e0bbdbaf-0059-449c-b6f1-edf1353a2c54'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.shaders = []

    def read(self, stream: Stream, version):
        count = stream.read_int('shader count')
        for i in range(count):
            self.shaders.append(stream.read_object('shader {}'.format(i + 1)))

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'shaders': [s.to_dict() for s in self.shaders]
        }
