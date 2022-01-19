#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object, not_implemented
from ..stream import Stream


@not_implemented
class DimensionShape(Object):
    """
    DimensionShape
    """

    @staticmethod
    def cls_id():
        return 'd27a074a-10ad-11d4-80d7-00c04f601565'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    def read(self, stream: Stream, version):
        pass

    def to_dict(self):  # pylint: disable=method-hidden
        return {
        }
