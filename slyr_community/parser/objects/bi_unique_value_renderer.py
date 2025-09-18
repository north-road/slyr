#!/usr/bin/env python
"""
Serializable object subclass

PARTIAL INTERPRETATION - possibly some instability
"""

from ..object import Object
from ..stream import Stream


class BiUniqueValueRenderer(Object):
    """
    BiUniqueValueRenderer
    """

    @staticmethod
    def cls_id():
        return "b899ccd3-cd1c-11d2-9f25-00c04f6bc709"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.main_renderer = None
        self.variation_renderer = None

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        self.main_renderer = stream.read_object("unique value renderer")
        self.variation_renderer = stream.read_object("class breaks renderer")

        # possibly legend?
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "main_renderer": self.main_renderer.to_dict()
            if self.main_renderer
            else None,
            "variation_renderer": self.variation_renderer.to_dict()
            if self.variation_renderer
            else None,
        }
