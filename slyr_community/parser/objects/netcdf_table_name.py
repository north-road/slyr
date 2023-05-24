#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from ..object_registry import REGISTRY


class NetCDFTableName(Object):
    """
    NetCDFTableName
    """
    @staticmethod
    def cls_id():
        return '2d597a23-a989-43c1-9b1b-19e75bbfb78f'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ''
        self.name_string = ''
        self.category = ''
        self.variable_list = None
        self.dimension_list = None
        self.workspace_name = None

    def read(self, stream: Stream, version):
        self.name = stream.read_string('name')
        self.name_string = stream.read_string('name string')
        self.category = stream.read_string('category')

        self.workspace_name = stream.read_object('workspace name')
        self.variable_list = stream.read_object('variable list')
        self.dimension_list = stream.read_object('dimension list')
        stream.read_object('unknown string array')
        stream.read_object('unknown long array')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'name': self.name,
            'name_string': self.name_string,
            'workspace_name': self.workspace_name.to_dict() if self.workspace_name else None,
            'category': self.category,
            'variable_list': self.variable_list.to_dict() if self.variable_list else None,
            'dimension_list': self.dimension_list.to_dict() if self.dimension_list else None
        }

    @classmethod
    def from_dict(cls, definition: dict) -> 'NetCDFTableName':
        res = NetCDFTableName()
        res.name = definition['name']
        res.name_string = definition['name_string']
        res.workspace_name = REGISTRY.create_object_from_dict(definition['workspace_name'])
        res.category = definition['category']
        res.variable_list = REGISTRY.create_object_from_dict(definition['variable_list'])
        res.dimension_list = REGISTRY.create_object_from_dict(definition['dimension_list'])
        return res
