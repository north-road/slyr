#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class AnnotationPythonEngine(Object):
    """
    AnnotationPythonEngine
    """

    @staticmethod
    def cls_id():
        return "bb6721a2-d81a-45e3-7fef-884db2b2a905"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.show_coded = False

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        self.show_coded = stream.read_ushort("show coded") != 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {"show_coded": self.show_coded}
