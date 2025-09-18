#!/usr/bin/env python
"""
HotlinkVbscriptEngine
"""

from ..object import Object
from ..stream import Stream


class HotlinkVbscriptEngine(Object):
    """
    Relates to hyperlinks
    """

    @staticmethod
    def cls_id():
        return "55ef0065-fdff-469b-b693-8ebfc56b3b3b"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        assert stream.read(2) == b"\xff\xff"

    def to_dict(self):  # pylint: disable=method-hidden
        return {}
