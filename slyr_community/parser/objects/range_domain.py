#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class RangeDomain(Object):
    """
    RangeDomain
    """

    @staticmethod
    def cls_id():
        return "f84c6c1a-47ff-11d2-9933-0000f80372b4"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ""
        self.domain_id = 0
        self.merge_policy = 0  # esriMergePolicyType
        self.split_policy = 0  # esriSplitPolicyType
        self.description = ""
        self.owner = ""
        self.field_type = 0  # esriFieldType
        self.min = None
        self.max = None

    def __repr__(self):
        if self.ref_id is not None:
            return "<RangeDomain: {} ({})>".format(self.name, self.ref_id)
        else:
            return "<RangeDomain: {}>".format(self.name)

    def read(self, stream: Stream, version):
        stream.read_ushort("unknown", expected=1)
        self.domain_id = stream.read_int("domain id")
        self.merge_policy = stream.read_int("merge policy")
        self.split_policy = stream.read_int("split policy")
        self.name = stream.read_string("name")
        self.description = stream.read_string("description")
        self.owner = stream.read_string("owner")
        self.field_type = stream.read_int("field type")

        min_type = stream.read_int("min value type")
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        self.min = stream.read_variant(min_type, "min")

        max_type = stream.read_int("max value type")
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        stream.read_int("unknown", expected=0)
        self.max = stream.read_variant(max_type, "max")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "name": self.name,
            "domain_id": self.domain_id,
            "merge_policy": self.merge_policy,
            "split_policy": self.split_policy,
            "description": self.description,
            "owner": self.owner,
            "field_type": self.field_type,
            "min": self.min,
            "max": self.max,
        }
