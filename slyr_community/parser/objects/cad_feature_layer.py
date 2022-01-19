#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class CadFeatureLayer(Object):
    """
    CadFeatureLayer
    """

    @staticmethod
    def cls_id():
        return 'e0f384b6-e0c1-11d2-9b30-00c04fa33299'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.layer = None
        self.drawing_object = None
        self.visible = True
        self.name = ''
        self.datasource_type = ''
        self.dataset_name = None

    @staticmethod
    def compatible_versions():
        return [2, 4]

    def read(self, stream: Stream, version):
        self.layer = stream.read_object('layer')
        self.drawing_object = stream.read_object('drawing object')

        count = stream.read_int('unknown count')
        for i in range(count):
            stream.read_ushort('unknown flag {}'.format(i + 1), expected=(0, 65535))

        if version > 2:
            stream.read_string('unknown', expected='')
            stream.read_double('unknown', expected=0)
            stream.read_double('unknown', expected=0)

        # copy some stuff from the layer
        if self.layer:
            self.visible = self.layer.visible
            self.name = self.layer.name
            self.datasource_type = self.layer.datasource_type
            self.dataset_name = self.layer.dataset_name

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'layer': self.layer.to_dict() if self.layer else None,
            'cad_drawing_object': self.drawing_object.to_dict() if self.drawing_object else None
        }
