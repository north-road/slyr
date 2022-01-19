#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object, not_implemented
from ..stream import Stream


class QueryFilter(Object):
    """
    QueryFilter
    """

    @staticmethod
    def cls_id():
        return 'fdfebd95-ed75-11d0-9a95-080009ec734b'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.filter = None
        self.filter_def = None

    @staticmethod
    def compatible_versions():
        return [1, 3, 4, 5]

    def read(self, stream: Stream, version):
        stream.read_string('fields', expected='*')
        self.filter = stream.read_string('filter')
        stream.read_string('unknown', expected='')

        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)

        if version > 1:
            # or possibly here for v1, and not in rel_query_table_name v2
            stream.read_int('unknown', expected=0)

            self.filter_def = stream.read_object('array of filter def')
        if version > 3:
            stream.read_int('unknown', expected=0)
        if version > 4:
            stream.read_ushort('unknown', expected=65535)
            stream.read_ushort('unknown', expected=65535)
            stream.read_ushort('unknown', expected=65535)
            stream.read_ushort('unknown', expected=65535)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'filter': self.filter,
            'filter_def': self.filter_def.to_dict() if self.filter_def else None
        }

    @classmethod
    def from_dict(cls, definition: dict) -> 'QueryFilter':
        res = QueryFilter()
        res.filter = definition['filter']
        return res