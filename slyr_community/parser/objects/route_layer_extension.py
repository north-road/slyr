#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class RouteLayerExtension(Object):
    """
    RouteLayerExtension
    """

    @staticmethod
    def cls_id():
        return '7ae2ec78-3a86-4b7b-901b-a30d1d99f4ca'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.route_identifier = ''
        self.anomaly_properties = None

    @staticmethod
    def supports_references():
        return False

    def read(self, stream: Stream, version):
        self.route_identifier = stream.read_string('route identifier')
        self.anomaly_properties = stream.read_object('route anomaly properties')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
        }
