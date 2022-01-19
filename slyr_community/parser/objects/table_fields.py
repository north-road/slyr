#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class TableFields(Object):
    """
    TableFields
    """

    @staticmethod
    def cls_id():
        return 'c6b01007-533d-4625-81b7-2dff82f0424c'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.fields = []
        self.field_info = []
        self.field_widths = {}

    @staticmethod
    def compatible_versions():
        return [1, 2]

    def read(self, stream: Stream, version):
        stream.read_int('unknown', expected=39)
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=20)
        stream.read_int('unknown', expected=1600)
        stream.read_int('unknown', expected=172)
        if version == 1:
            stream.read_string('unknown', expected='')
            stream.read_int('unknown', expected=0)
            stream.read_uchar('unknown', expected=0)

        elif version > 1:
            stream.read_int('unknown', expected=0)

        stream.read_string('fields')

        stream.read_object('unknown color')

        count = stream.read_int('field count')
        for i in range(count):
            field_name = stream.read_string('field {}'.format(i + 1))
            field_width = stream.read_int('field width {}'.format(i + 1))
            self.field_widths[field_name] = field_width

        for i in range(count):
            self.fields.append(stream.read_object('field {}'.format(i + 1)))
            self.field_info.append(stream.read_object('field info {}'.format(i + 1)))

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'fields': [f.to_dict() for f in self.fields],
            'field_info': [f.to_dict() for f in self.field_info],
            'widths': self.field_widths
        }
