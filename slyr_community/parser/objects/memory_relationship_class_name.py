#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..object_registry import REGISTRY
from ..stream import Stream


class MemoryRelationshipClassName(Object):
    """
    MemoryRelationshipClassName
    """

    @staticmethod
    def cls_id():
        return '6dba211b-ebdb-11d3-9f84-00c04f6bc886'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ''
        self.destination_name = None
        self.origin_name = None
        self.origin_primary_key = ''
        self.origin_foreign_key = ''
        self.backward_path_label = ''
        self.forward_path_label = ''

    def read(self, stream: Stream, version):
        self.name = stream.read_string('name')
        stream.read_string('unknown', expected='')
        stream.read_string('unknown', expected='Memory relationship class')
        stream.read_int('unknown', expected=2)  # cardinality??
        stream.read_int('unknown', expected=1)  # notification?
        stream.read_int('unknown', expected=0)  # is attributed/composite?

        self.destination_name = stream.read_object('destination name')
        self.origin_name = stream.read_object('origin name')

        self.forward_path_label = stream.read_string('forward label')
        self.backward_path_label = stream.read_string('backward label')
        self.origin_primary_key = stream.read_string('origin primary key')
        self.origin_foreign_key = stream.read_string('origin foreign key')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'name': self.name,
            'destination_name': self.destination_name.to_dict() if self.destination_name else None,
            'origin_name': self.origin_name.to_dict() if self.origin_name else None,
            'origin_primary_key': self.origin_primary_key,
            'origin_foreign_key': self.origin_foreign_key,
            'forward_path_label': self.forward_path_label,
            'backward_path_label': self.backward_path_label
        }

    @classmethod
    def from_dict(cls, definition: dict) -> 'MemoryRelationshipClassName':
        res = MemoryRelationshipClassName()
        res.name = definition['name']
        res.destination_name = REGISTRY.create_object_from_dict(definition['destination_name'])
        res.origin_name = REGISTRY.create_object_from_dict(definition['origin_name'])
        res.origin_primary_key = definition['origin_primary_key']
        res.origin_foreign_key = definition['origin_foreign_key']
        res.forward_path_label = definition['forward_path_label']
        res.backward_path_label = definition['backward_path_label']
        return res
