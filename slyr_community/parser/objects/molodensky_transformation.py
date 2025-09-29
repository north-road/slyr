#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object, not_implemented
from ..stream import Stream


@not_implemented
class MolodenskyTransformation(Object):
    """
    MolodenskyTransformation
    """

    @staticmethod
    def cls_id():
        return "0cdf92b0-c2a0-11d2-bd08-0000f875bcce"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    def read(self, stream: Stream, version):
        pass

    def to_dict(self):  # pylint: disable=method-hidden
        return {}
