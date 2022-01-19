#!/usr/bin/env python
"""
TableName

PARTIAL INTERPRETATION -- mostly complete, should be robust
"""

from ..object import Object
from ..object_registry import REGISTRY
from ..stream import Stream


class TableName(Object):
    """
    TableName
    """

    @staticmethod
    def cls_id():
        return '06783db1-e5ee-11d1-b0a2-0000f8780820'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ''
        self.category = ''
        self.workspace_name = None
        self.datasource_type = ''

    def read(self, stream: Stream, version):
        self.name = stream.read_string('name')
        self.category = stream.read_string('category', expected='')
        self.datasource_type = stream.read_string('type')
        self.workspace_name = stream.read_object('workspace name')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'name': self.name,
            'category': self.category,
            'datasource_type': self.datasource_type,
            'workspace_name': self.workspace_name.to_dict() if self.workspace_name else None
        }

    @classmethod
    def from_dict(cls, definition: dict) -> 'TableName':
        res = TableName()
        res.name = definition['name']
        res.category = definition['category']
        res.datasource_type = definition['datasource_type']
        res.workspace_name = REGISTRY.create_object_from_dict(definition['workspace_name'])
        return res


class FgdbTableName(Object):
    """
    FgdbTableName
    """

    @staticmethod
    def cls_id():
        return '846c88c5-6cc5-49c7-a6fe-8fa03d79bd07'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ''
        self.category = ''
        self.workspace_name = None
        self.datasource_type = ''

    def read(self, stream: Stream, version):
        stream.read_ushort('unknown flag')
        stream.read_ushort('unknown', expected=1)

        self.name = stream.read_string('name')
        self.category = stream.read_string('category')
        assert self.category == ''  # not sure this actually IS category?
        self.datasource_type = stream.read_string('type')
        self.workspace_name = stream.read_object('workspace name')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'name': self.name,
            'category': self.category,
            'datasource_type': self.datasource_type,
            'workspace_name': self.workspace_name.to_dict() if self.workspace_name else None
        }

    @classmethod
    def from_dict(cls, definition: dict) -> 'FgdbTableName':
        res = FgdbTableName()
        res.name = definition['name']
        res.category = definition['category']
        res.datasource_type = definition['datasource_type']
        res.workspace_name = REGISTRY.create_object_from_dict(definition['workspace_name'])
        return res
