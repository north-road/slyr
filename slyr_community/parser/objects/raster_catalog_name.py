#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from ..object_registry import REGISTRY


class RasterCatalogName(Object):
    """
    RasterCatalogName
    """

    @staticmethod
    def cls_id():
        return '33ff62fc-d7d6-48e8-82d9-77c0aadbf5d1'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.workspace_name = None
        self.name = ''
        self.name_string = ''
        self.datasource_type = ''
        self.shape_field_name = ''
        self.shape_type = 0
        self.feature_type = 0

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        self.name = stream.read_string('name')
        self.name_string = stream.read_string('name string')
        self.datasource_type = stream.read_string('category')
        self.shape_field_name = stream.read_string('shape field name')

        self.shape_type = stream.read_int('shape type')
        self.feature_type = stream.read_int('feature type')
        stream.read_ushort('unknown', expected=0)

        self.workspace_name = stream.read_object('workspace name')

        stream.read_ushort('unknown', expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'workspace_name': self.workspace_name.to_dict() if self.workspace_name else None,
            'name': self.name,
            'name_string': self.name_string,
            'datasource_type': self.datasource_type,
            'shape_field_name': self.shape_field_name,
            'shape_type': self.shape_type,
            'feature_type': self.feature_type,
        }

    @classmethod
    def from_dict(cls, definition: dict) -> 'RasterCatalogName':
        res = RasterCatalogName()
        res.name = definition['name']
        res.name_string = definition['name_string']
        res.datasource_type = definition['datasource_type']
        res.shape_field_name = definition['shape_field_name']
        res.shape_type = definition['shape_type']
        res.feature_type = definition['feature_type']
        res.workspace_name = REGISTRY.create_object_from_dict(definition['workspace_name'])
        return res
