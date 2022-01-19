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

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        internal_version = stream.read_ushort('internal version', expected=(2, 3))

        stream.read_string('name')
        stream.read_int('renderer type')

        stream.read_int('arrow type')
        stream.read_string('arrow attribute name')
        stream.read_object('arrow symbol one way')
        stream.read_object('arrow symbol both ways')
        stream.read_object('arrow symbol no way')
        stream.read_ushort('show arrow one way') != 0
        stream.read_ushort('show arrow both ways') != 0
        stream.read_ushort('show arrow no way') != 0

        if internal_version > 2:
            stream.read_int('unknown', expected=0)

        stream.read_object('legend group')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
        }
