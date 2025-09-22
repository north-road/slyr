#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class StyleGallery(Object):
    """
    StyleGallery
    """

    @staticmethod
    def cls_id():
        return "ac0e9827-91cb-11d1-8813-080009ec732a"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.styles = []
        self.default_path = ""

    def read(self, stream: Stream, version):
        count = stream.read_int("count")
        for i in range(count):
            self.styles.append(stream.read_string("style path {}".format(i + 1)))
        self.default_path = stream.read_string("default path")

    def to_dict(self):  # pylint: disable=method-hidden
        return {"styles": self.styles, "default_path": self.default_path}
