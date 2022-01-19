#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class CadLayer(Object):
    """
    CadLayer
    """

    @staticmethod
    def cls_id():
        return 'e299adbd-a5c3-11d2-9b10-00c04fa33299'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ''
        self.crs = None
        self.dataset_name = None
        self.drawing_object = None

    @staticmethod
    def compatible_versions():
        return [6, 8]

    def read(self, stream: Stream, version):
        self.name = stream.read_string('unknown dgn path')  # maybe layer name?

        stream.read_ushort('unknown', expected=(0, 65535))

        stream.read_double('unknown', expected=0)
        stream.read_double('unknown', expected=0)
        stream.read_int('unknown', expected=0)

        self.crs = stream.read_object('crs')

        stream.read_double('unknown', expected=0)

        self.dataset_name = stream.read_object('drawing name')
        self.drawing_object = stream.read_object('drawing object')

        stream.read_int('unknown', expected=0)
        stream.read_string('unknown', expected='')
        stream.read_double('unknown', expected=90)
        stream.read_int('unknown', expected=0)

        if version > 6:
            stream.read_string('unknown', expected='')

            stream.read_int('unknown', expected=0)
            stream.read_int('unknown', expected=0)
            stream.read_int('unknown', expected=0)
            stream.read_int('unknown', expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'name': self.name,
            'crs': self.crs.to_dict() if self.crs else None,
            'dataset_name': self.dataset_name.to_dict() if self.dataset_name else None,
            'drawing_object': self.drawing_object.to_dict() if self.drawing_object else None
        }
