#!/usr/bin/env python
"""
Serializable object subclass

NEAR COMPLETE INTERPRETATION - all useful components

"""

from ..object import Object
from ..stream import Stream


class CadAnnotationLayer(Object):
    """
    CadAnnotationLayer
    """

    @staticmethod
    def cls_id():
        return 'e1b71879-a5df-11d4-a215-444553547777'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.visible = True
        self.coverage_layer = None
        self.text_symbols = []
        self.description = ''
        self.name = ''

        # used when a zoom range has been set previously, but is currently disabled
        self.stored_zoom_max = 0
        self.stored_zoom_min = 0

    @staticmethod
    def compatible_versions():
        return [4]

    def read(self, stream: Stream, version):
        self.coverage_layer = stream.read_object('coverage layer')
        self.name = self.coverage_layer.name
        self.visible = self.coverage_layer.visible

        stream.read_object('cad drawing object')

        count = stream.read_int('unknown count')
        for i in range(count):
            stream.read_ushort('unknown {}'.format(i + 1))

        self.description = stream.read_string('description')
        self.stored_zoom_max = stream.read_double('stored zoom max')
        self.stored_zoom_min = stream.read_double('stored zoom min')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'coverage_layer': self.coverage_layer.to_dict() if self.coverage_layer else None,
            'stored_zoom_min': self.stored_zoom_min,
            'stored_zoom_max': self.stored_zoom_max,
            'text_symbols': [s.to_dict() for s in self.text_symbols],
            'description': self.description
        }
