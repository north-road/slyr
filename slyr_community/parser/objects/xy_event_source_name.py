#!/usr/bin/env python
"""
XYEventSourceName

PARTIAL INTERPRETATION -- some unknowns, should be robust
"""

from ..object import Object
from ..stream import Stream
from ..object_registry import REGISTRY


class XYEventSourceName(Object):
    """
    XYEventSourceName
    """

    @staticmethod
    def cls_id():
        return '309aa920-eaec-11d3-9f8a-00c04f6bdf06'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ''
        self.feature_dataset_name = None
        self.event_properties = None
        self.crs = None

    def read(self, stream: Stream, version):
        self.name = stream.read_string('name')
        stream.read_string('unknown', expected='')  # maybe category?
        self.feature_dataset_name = stream.read_object('feature dataset name')
        self.event_properties = stream.read_object('event properties')
        self.crs = stream.read_object('crs')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'name': self.name,
            'feature_dataset_name': self.feature_dataset_name.to_dict() if self.feature_dataset_name else None,
            'event_properties': self.event_properties.to_dict() if self.event_properties else None,
            'crs': self.crs.to_dict() if self.crs else None
        }

    @classmethod
    def from_dict(cls, definition: dict) -> 'XYEventSourceName':
        res = XYEventSourceName()
        res.name = definition['name']
        res.feature_dataset_name = REGISTRY.create_object_from_dict(definition['feature_dataset_name'])
        res.event_properties = REGISTRY.create_object_from_dict(definition['event_properties'])
        res.crs = REGISTRY.create_object_from_dict(definition['crs'])
        return res
