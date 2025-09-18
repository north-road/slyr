#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class CadDrawingObject(Object):
    """
    CadDrawingObject
    """

    @staticmethod
    def cls_id():
        return "e0f384b8-e0c1-11d2-9b30-00c04fa33299"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.path = ""
        self.world_file_path = ""

    def read(self, stream: Stream, version):
        self.path = stream.read_string("file path")
        self.world_file_path = stream.read_string("world file path")
        stream.read_int("unknown", expected=0)
        stream.read_ushort("unknown", expected=0)
        stream.read_double("unknown")
        stream.read_double("unknown")
        stream.read_double("unknown")
        stream.read_double("unknown")
        stream.read_double("unknown")
        stream.read_double("unknown")
        stream.read_double("unknown")
        stream.read_double("unknown")
        stream.read_double("unknown", expected=0)
        stream.read_double("unknown", expected=1)
        count = stream.read_int("unknown count")
        for i in range(count):
            stream.read_int("unknown {}".format(i + 1))

    def to_dict(self):  # pylint: disable=method-hidden
        return {"path": self.path, "world_file_path": self.world_file_path}
