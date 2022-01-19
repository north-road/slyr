#!/usr/bin/env python
"""
Serializable object subclass

COMPLETE INTERPRETATION
"""

from ..object import Object
from ..stream import Stream


class Hyperlink(Object):
    """
    Hyperlink
    """

    @staticmethod
    def cls_id():
        return '3036d35e-ede5-11d0-87fe-080009ec732a'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.feature_id = 0
        self.url = ''
        self.link_type = 0

    def read(self, stream: Stream, version):
        self.feature_id = stream.read_int('feature id')
        self.url = stream.read_string('url')
        self.link_type = stream.read_int('link type')  # esriHyperlinkType

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'url': self.url,
            'feature_id': self.feature_id,
            'link_type': self.link_type
        }
