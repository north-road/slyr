#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..object_registry import REGISTRY
from ..stream import Stream


class RouteEventSourceName(Object):
    """
    RouteEventSourceName
    """

    @staticmethod
    def cls_id():
        return '63be9174-b8c7-11d3-9f7c-00c04f6bdf06'

    def __init__(self):
        super().__init__()
        self.name = ''
        self.name_string = ''
        self.dataset_name = None
        self.event_table_name = None
        self.route_measure_line_properties = None

    def read(self, stream: Stream, version):
        self.name = stream.read_string('layer name?')
        self.name_string = stream.read_string('name string')
        self.dataset_name = stream.read_object('workspace name')
        self.event_table_name = stream.read_object('event table name')
        self.route_measure_line_properties = stream.read_object('route measure line properties')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'name': self.name,
            'name_string': self.name_string,
            'workspace_name': self.dataset_name.to_dict() if self.dataset_name else None,
            'event_table_name': self.event_table_name.to_dict() if self.event_table_name else None,
            'route_measure_line_properties': self.route_measure_line_properties.to_dict() if self.route_measure_line_properties else None,
        }

    @classmethod
    def from_dict(cls, definition: dict) -> 'RouteEventSourceName':
        res = RouteEventSourceName()
        res.name = definition['name']
        res.name_string = definition['name_string']
        res.dataset_name = REGISTRY.create_object_from_dict(definition['workspace_name'])
        res.event_table_name = REGISTRY.create_object_from_dict(definition['event_table_name'])
        res.route_measure_line_properties = REGISTRY.create_object_from_dict(
            definition['route_measure_line_properties'])
        return res
