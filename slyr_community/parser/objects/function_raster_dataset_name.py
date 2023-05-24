#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class FunctionRasterDatasetName(Object):
    """
    FunctionRasterDatasetName
    """
    @staticmethod
    def cls_id():
        return 'eb07e8cc-ee78-438a-a2c1-ba80455acb02'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.full_name = ''
        self.name_string = ''
        self.category = ''
        self.workspace_name = None
        self.function = None
        self.properties = None
        self.browse_name = ''
        self.raster = None

    @staticmethod
    def compatible_versions():
        return [7]

    def read(self, stream: Stream, version):
        self.full_name = stream.read_string('full name')
        self.name_string = stream.read_string('name string')
        self.category = stream.read_string('category')
        self.workspace_name = stream.read_object('workspace name')
        stream.read_string('path?')
        self.function = stream.read_object('function')
        stream.read_int('unknown', expected=0)
        self.raster = stream.read_object('source raster?')
        self.properties = stream.read_object('properties')
        self.browse_name = stream.read_string('browse name')
        stream.read_string('unknown', expected='')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'full_name': self.full_name,
            'name_string': self.name_string,
            'category': self.category,
            'workspace_name': self.workspace_name.to_dict() if self.workspace_name else None,
            'function': self.function.to_dict() if self.function else None,
            'properties': self.properties.to_dict() if self.properties else None,
            'browse_name': self.browse_name,
            'raster': self.raster.to_dict() if self.raster else None
        }
