#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class CadDrawingName(Object):
    """
    CadDrawingName
    """

    @staticmethod
    def cls_id():
        return "d4224309-a5cb-11d2-9b10-00c04fa33299"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.dataset_name = None

    def read(self, stream: Stream, version):
        stream.read_string("unknown dgn path")
        stream.read_string("unknown", expected="")
        stream.read_string("unknown", expected="CAD Drawing")
        self.dataset_name = stream.read_object("workspace name")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "dataset_name": self.dataset_name.to_dict() if self.dataset_name else None
        }
