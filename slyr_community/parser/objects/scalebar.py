#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object, not_implemented
from ..stream import Stream


@not_implemented
class Scalebar(Object):
    """
    Scalebar
    """

    @staticmethod
    def cls_id():
        return "7a3f91db-b9e3-11d1-8756-0000f8751720"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    def read(self, stream: Stream, version):
        pass

    def to_dict(self):  # pylint: disable=method-hidden
        return {}
