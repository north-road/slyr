#!/usr/bin/env python
"""
Serializable object subclass
"""

from ...parser.object import Object
from ...parser.stream import Stream


class LODInfos(Object):
    """
    LODInfos
    """

    @staticmethod
    def cls_id():
        return "8cd19a51-334b-4c0a-bc97-a3fdea0a1ce0"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.levels = []

    def read(self, stream: Stream, version):
        count = stream.read_int("count")
        for i in range(count):
            self.levels.append(stream.read_object("level {}".format(i + 1)))

    def to_dict(self):  # pylint: disable=method-hidden
        return {"levels": [l.to_dict() for l in self.levels]}
