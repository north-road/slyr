#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object, not_implemented
from ..stream import Stream


@not_implemented
class DimensionStyles(Object):
    """
    DimensionStyles
    """

    @staticmethod
    def cls_id():
        return '45b2fa28-fa01-11d3-80d3-00c04f601565'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    def read(self, stream: Stream, version):
        pass

    def to_dict(self):  # pylint: disable=method-hidden
        return {
        }
