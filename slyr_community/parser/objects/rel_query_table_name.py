#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream
from ..object_registry import REGISTRY


class RelQueryTableName(Object):
    """
    RelQueryTableName
    """

    @staticmethod
    def cls_id():
        return 'dab3ee10-0f92-455d-8aa2-3d4ade5b2f7d'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ''
        self.filter = None
        self.workspace_name = None

    @staticmethod
    def compatible_versions():
        return [2, 3]

    def read(self, stream: Stream, version):
        self.name = stream.read_string('name')
        stream.read_string('unknown', expected='')

        self.workspace_name = stream.read_object('workspace name')

        stream.read_ushort('unknown', expected=0)
        self.filter = stream.read_object('filter')

        # probably an object...
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)

        stream.read_string('sub fields?', expected='*')
        stream.read_ushort('unknown flag')
        stream.read_ushort('unknown flag', expected=0)
        if version > 2:
            stream.read_ushort('unknown flag', expected=65535)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'name': self.name,
            'workspace_name': self.workspace_name.to_dict() if self.workspace_name else None,
            'filter': self.filter.to_dict() if self.filter else None
        }

    @classmethod
    def from_dict(cls, definition: dict) -> 'RelQueryTableName':
        res = RelQueryTableName()
        res.name = definition['name']
        res.workspace_name = REGISTRY.create_object_from_dict(definition['workspace_name'])
        res.filter = REGISTRY.create_object_from_dict(definition['filter'])
        return res