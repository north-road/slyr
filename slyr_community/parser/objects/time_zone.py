#!/usr/bin/env python
"""
TimeExtent

PARTIAL INTERPRETATION:
"""

from ..object import Object
from ..stream import Stream


class TimeZone(Object):

    @staticmethod
    def cls_id():
        return '78fad5f1-60fa-458a-8d93-630da920448d'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.offset = 0
        self.display_name = ''
        self.standard_name = ''
        self.use_daylight_savings = False

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        self.display_name = stream.read_string('display name?')
        self.standard_name = stream.read_string('standard name?')

        stream.read_string('unknown', expected='')
        stream.read_int('unknown', expected=0)

        self.offset = -stream.read_ulong('utc diff') / 60

        stream.read(80)
        stream.read_int('unknown', expected=0)
        stream.read(80)

        stream.read_ushort('unknown', expected=65476)
        stream.read_ushort('unknown', expected=65535)
        rule_count = stream.read_ushort('rule count')
        for i in range(rule_count):
            stream.read_uint('year')
            stream.read(172)

        self.use_daylight_savings = stream.read_ushort('use daylight savings') != 0
        stream.read_ushort('unknown', expected=65535)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'display_name': self.display_name,
            'standard_name': self.standard_name,
            'offset': self.offset,
            'use_daylight_savings': self.use_daylight_savings
        }
