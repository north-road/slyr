#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class SimpleNetworkRenderer(Object):
    """
    SimpleNetworkRenderer
    """

    @staticmethod
    def cls_id():
        return '1c30bfd1-db91-48f1-b3c1-6a2feb0c7104'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ''
        self.renderer_type = 0
        self.arrow_type = 0
        self.arrow_attribute_name = ''
        self.arrow_symbol_one_way = None
        self.arrow_symbol_both_ways = None
        self.arrow_symbol_no_way = None
        self.show_arrow_one_way = False
        self.show_arrow_both_ways = False
        self.show_arrow_no_way = False
        self.legend_group = None

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        internal_version = stream.read_ushort('internal version', expected=(2, 3))

        self.name = stream.read_string('name')
        self.renderer_type = stream.read_int('renderer type')

        self.arrow_type = stream.read_int('arrow type')
        self.arrow_attribute_name = stream.read_string('arrow attribute name')
        self.arrow_symbol_one_way = stream.read_object('arrow symbol one way')
        self.arrow_symbol_both_ways = stream.read_object('arrow symbol both ways')
        self.arrow_symbol_no_way = stream.read_object('arrow symbol no way')

        self.show_arrow_one_way = stream.read_ushort('show arrow one way') != 0
        self.show_arrow_both_ways = stream.read_ushort('show arrow both ways') != 0
        self.show_arrow_no_way = stream.read_ushort('show arrow no way') != 0

        if internal_version > 2:
            stream.read_int('unknown', expected=0)

        stream.read_object('legend group')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
        }
