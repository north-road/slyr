#!/usr/bin/env python
"""
TimeExtent

COMPLETE INTERPRETATION:
"""

from ..object import Object
from ..stream import Stream


class TimeReference(Object):

    @staticmethod
    def cls_id():
        return 'efb2e7db-78f4-4e24-b01f-4f9c7ab800c5'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.time_zone = None

    def read(self, stream: Stream, version):
        self.time_zone = stream.read_object('time zone')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'time_zone': self.time_zone.to_dict() if self.time_zone else None
        }
