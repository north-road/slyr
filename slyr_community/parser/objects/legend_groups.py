#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class LegendGroups(Object):
    """
    LegendGroups
    """

    @staticmethod
    def cls_id():
        return '93942eb3-2cd2-4bfe-9937-380ec7d06e1f'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.groups = []

    def read(self, stream: Stream, version):
        count = stream.read_int('count')
        for i in range(count):
            self.groups.append(stream.read_object('legend group {}'.format(i + 1)))

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'groups': [g.to_dict() for g in self.groups]
        }
