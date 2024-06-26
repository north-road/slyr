#!/usr/bin/env python
"""
Serializable object subclass
"""

from .geometry import Geometry
from ..stream import Stream


class Polyline(Geometry):
    """
    Polyline
    """

    @staticmethod
    def cls_id():
        return '30707210-52d5-11d0-a8f2-00608c85ede5'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.parts = []

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):  # pylint: disable=too-many-locals
        size = stream.read_int('size')
        start = stream.tell()
        wkb_type = stream.read_int('wkb type?', expected=(3, 536870962))

        self.x_min = stream.read_double('x min')
        self.y_min = stream.read_double('y min')
        self.x_max = stream.read_double('x max')
        self.y_max = stream.read_double('y max')

        parts = stream.read_int('parts')
        total_vertices = stream.read_int('total vertices')
        if total_vertices > 0:
            index = stream.read_int('first index', expected=0)
            counts = []
            for p in range(1, parts):
                next_index = stream.read_int('index {}'.format(p + 1))
                counts.append(next_index - index)
                index = next_index
            counts.append(total_vertices - index)

            for count in counts:
                part = []
                for i in range(count):
                    x = stream.read_double('x {}'.format(i + 1))
                    y = stream.read_double('y {}'.format(i + 1))
                    part.append((x, y))
                self.parts.append(part)

            if wkb_type == 536870962:
                self.read_curve_points(stream)

        if stream.tell() != size + start:
            stream.log('skipping unknown bytes')
            stream.read(size + start - stream.tell())

        assert stream.tell() == size + start, (stream.tell() - start, size)

        self.crs = stream.read_object('crs')

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res['parts'] = self.parts
        return res
