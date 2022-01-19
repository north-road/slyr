#!/usr/bin/env python
"""
Unique value renderer

PARTIAL INTERPRETATION - Generally working, but large part of stream is
not understood and parsing is not robust
"""

from .vector_renderer import VectorRendererBase
from ..stream import Stream


class UniqueValueRenderer(VectorRendererBase):
    """
    UniqueValueRenderer
    """

    @staticmethod
    def cls_id():
        return 'c3346d29-b2bc-11d1-8817-080009ec732a'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.reverse_sorting = False
        self.fields = []
        self.symbol = None
        self.all_other_value = None
        self.include_all_other = True
        self.concatenator = None
        self.ramp = None
        self.ramp_name = ''
        self.groups = []
        self.values = []
        self.reversed = False
        self.style_path = None
        self.flip_symbols = False

    @staticmethod
    def compatible_versions():
        return [2, 3, 5]

    def read(self, stream: Stream, version):  # pylint: disable=too-many-statements
        field_count = stream.read_int('field count')
        for _ in range(field_count):
            self.fields.append(stream.read_string('field'))
            res = stream.read(3)  # pylint: disable=unused-variable
            # assert res == b'\x01\x00\x00', res

        self.concatenator = stream.read_string('concatenator')

        self.symbol = stream.read_object('all other symbol')

        group_count = stream.read_uint('group count')
        for i in range(group_count):
            self.groups.append(stream.read_object('legend group {}'.format(i + 1)))

        _ = stream.read_object('unknown')

        value_count = stream.read_uint('value count')
        temp_values = []
        for i in range(value_count):
            value = stream.read_string('value')
            grouping_flag = stream.read_int('grouping_flag')
            if grouping_flag == 0xffffffff:
                # grouped value
                assert stream.read_int('unknown') == 0xffffffff
                stream.read_int('unknown')
                value_to_join_to = stream.read_string('value to join to')
                temp_values = [t + [value] if t[0] == value_to_join_to else t for t in temp_values]
                i -= 1
            else:
                # normal value
                temp_values.append([value])
                stream.read_int('counter?')
                stream.read_int('unknown', expected=0)
        self.values = [v[0] if len(v) == 1 else v for v in temp_values]

        stream.read_ushort('unknown', expected=0)

        self.rotation_attribute = stream.read_string('rotation attribute')
        self.rotation_type = stream.read_int('rotation type ')
        self.transparency_attribute = stream.read_string('transparency attribute')

        self.ramp_name = stream.read_string('ramp name')
        self.style_path = stream.read_string('style path')  # for lookup symbols

        self.include_all_other = stream.read_ushort('include all other') != 0
        self.all_other_value = stream.read_string('all other value')
        if version > 2:
            self.read_irotation_renderer2_properties(stream)
            self.read_graduated_size_properties(stream)

        if version > 3:
            self.ramp = stream.read_object('ramp')
            self.flip_symbols = stream.read_ushort('flip symbols') == 1
            self.reversed = stream.read_ushort('reversed') == 1

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res['fields'] = self.fields
        res['concatenator'] = self.concatenator
        res['symbol'] = self.symbol.to_dict() if self.symbol else None
        res['groups'] = [g.to_dict() for g in self.groups]
        res['values'] = self.values
        res['include_all_other'] = self.include_all_other
        res['all_other_value'] = self.all_other_value
        res['reversed'] = self.reversed
        res['ramp'] = self.ramp.to_dict() if self.ramp else None
        res['ramp_name'] = self.ramp_name
        res['style_path'] = self.style_path
        res['flip_symbols'] = self.flip_symbols
        return res
