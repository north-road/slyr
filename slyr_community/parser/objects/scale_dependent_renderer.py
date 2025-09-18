#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class ScaleDependentRenderer(Object):
    """
    ScaleDependentRenderer
    """

    @staticmethod
    def cls_id():
        return "207c19f5-ed81-11d0-8bba-080009ee4e41"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.breaks = []
        self.renderers = []

    @staticmethod
    def compatible_versions():
        return None

    def read(self, stream: Stream, version):
        count = stream.read_int("count")
        for i in range(count):
            self.breaks.append(stream.read_double("break {}".format(i + 1)))
            self.renderers.append(stream.read_object("renderer {}".format(i + 1)))

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "breaks": self.breaks,
            "renderers": [r.to_dict() for r in self.renderers],
        }
