#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class IdentityXForm(Object):
    """
    IdentityXForm
    """

    @staticmethod
    def cls_id():
        return "c4709a2e-299e-4609-9904-6c595319b30f"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.crs = None

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        stream.read_ushort("unknown", expected=0)
        self.crs = stream.read_object("crs")

    def to_dict(self):  # pylint: disable=method-hidden
        return {"crs": self.crs.to_dict() if self.crs else None}
