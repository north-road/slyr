#!/usr/bin/env python
"""
HotlinkVbscriptEngine
"""

from ..object import Object
from ..stream import Stream


class HotlinkPythonEngine(Object):
    """
    Relates to hyperlinks
    """

    @staticmethod
    def cls_id():
        return "ff7d30a3-38fa-67d1-780a-bebb61c0e599"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        assert stream.read(2) == b"\xff\xff"

    def to_dict(self):  # pylint: disable=method-hidden
        return {}
