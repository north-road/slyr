#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class AnnotationVBScriptEngine(Object):
    """
    AnnotationVBScriptEngine
    """

    @staticmethod
    def cls_id():
        return 'aa157207-e079-11d2-9f48-00c04f6bc6a5'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.show_coded = False

    @staticmethod
    def compatible_versions():
        return [1, 2]

    def read(self, stream: Stream, version):
        if version > 1:
            self.show_coded = stream.read_ushort('show coded') != 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'show_coded': self.show_coded
        }
