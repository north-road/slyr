#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class TopologyLayer(Object):
    """
    TopologyLayer
    """

    @staticmethod
    def cls_id():
        return 'de98bad5-135e-4b36-9653-57b5513fb7b2'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ''
        self.visible = False
        self.show_tips = False
        self.zoom_min = None
        self.zoom_max = None
        self.dataset_name = None
        self.area_error_renderer = None
        self.line_error_renderer = None
        self.point_error_renderr = None
        self.area_exception_renderer = None
        self.line_exception_renderer = None
        self.point_exception_renderer = None
        self.dirty_area_renderer = None

    @staticmethod
    def compatible_versions():
        return [5]

    def read(self, stream: Stream, version):
        self.name = stream.read_string('name')
        self.visible = stream.read_ushort('visible') != 0
        self.show_tips = stream.read_ushort('show tips') != 0
        stream.read_ushort('unknown', expected=65535)

        self.zoom_max = stream.read_double('zoom max')
        self.zoom_min = stream.read_double('zoom min')

        self.dataset_name = stream.read_object('dataset name')

        self.area_error_renderer = stream.read_object('area error renderer')
        self.line_error_renderer = stream.read_object('line error renderer')
        self.point_error_renderr = stream.read_object('point error renderer')
        self.area_exception_renderer = stream.read_object('area expection renderer')
        self.line_exception_renderer = stream.read_object('line exception renderer')
        self.point_exception_renderer = stream.read_object('point exception renderer')
        self.dirty_area_renderer = stream.read_object('dirty area renderer')
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)

        stream.read_ushort('unknown', expected=0)
        stream.read_ushort('unknown', expected=65535)
        stream.read_ushort('unknown', expected=65535)

        count = stream.read_int('unknown count')
        for i in range(count):
            stream.read_int('unknown {}'.format(i + 1))
            stream.read_ushort('unknown {}'.format(i + 1))

    def to_dict(self):  # pylint: disable=method-hidden
        return {
        }
