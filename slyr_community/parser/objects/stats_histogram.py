#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class StatsHistogram(Object):
    """
    StatsHistogram
    """

    @staticmethod
    def cls_id():
        return 'ba3027c1-49ca-4788-8b5a-3a6b387de78c'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.min = 0
        self.max = 0
        self.mean = 0
        self.st_dev = 0

    @staticmethod
    def compatible_versions():
        return [1, 2, 4, 5]

    def read(self, stream: Stream, version):
        stream.read_ushort('unknown', expected=0)

        self.min = stream.read_double('min')
        self.max = stream.read_double('max')
        self.mean = stream.read_double('mean')
        self.st_dev = stream.read_double('st dev')

        # seems to be min/max again?? maybe range? or source min/max?
        stream.read_double('min again')
        stream.read_double('max again')

        if version == 1:
            # wrong!
            for i in range(256):
                stream.read_double('unknown {}'.format(i + 1))
        elif version in (2, 4):
            for i in range(256):
                stream.read_double('unknown {}'.format(i + 1))

            # looks like a scale?
            stream.read_double('unknown')

            if version > 2:
                stream.read_double('unknown')
                stream.read_int('unknown')
        else:
            count = stream.read_int('count?')
            for i in range(count):
                stream.read_double('unknown {}'.format(i + 1))

            stream.read_double('unknown')  # expected=(0, 15000, 40000, 495919.0, 130550))
            stream.read_double(
                'unknown')  # expected=(0, 1, 0.6196078431372549, 1.008130081300813, 1.0076923076923077, 1.0067567567567568, 1.005813953488372, 1.003921568627451))
            count = stream.read_int('unknown count')
            for i in range(count):
                stream.read_double('unknown')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'min': self.min,
            'max': self.max,
            'mean': self.mean,
            'st_dev': self.st_dev
        }
