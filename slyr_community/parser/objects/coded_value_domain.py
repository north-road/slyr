#!/usr/bin/env python
"""
Serializable object subclass

NEAR COMPLETE INTERPRETATION - all useful components

"""

from ..object import Object
from ..stream import Stream


class CodedValueDomain(Object):
    """
    CodedValueDomain
    """

    @staticmethod
    def cls_id():
        return 'f84c6c1b-47ff-11d2-9933-0000f80372b4'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ''
        self.values = {}
        self.domain_id = 0
        self.merge_policy = 0  # esriMergePolicyType
        self.split_policy = 0  # esriSplitPolicyType
        self.description = ''
        self.owner = ''
        self.field_type = 0  # esriFieldType

    def __repr__(self):
        if self.ref_id is not None:
            return '<CodedValueDomain: {} ({})>'.format(self.name, self.ref_id)
        else:
            return '<CodedValueDomain: {}>'.format(self.name)

    def read(self, stream: Stream, version):
        stream.read_ushort('unknown', expected=1)
        self.domain_id = stream.read_int('domain id')
        self.merge_policy = stream.read_int('merge policy')
        self.split_policy = stream.read_int('split policy')
        self.name = stream.read_string('name')
        self.description = stream.read_string('description')
        self.owner = stream.read_string('owner')
        self.field_type = stream.read_int('field type')

        count = stream.read_int('count')
        for i in range(count):
            description = stream.read_stringv2('description')
            variant_type = stream.read_int('variant type')
            stream.read_int('unknown', expected=0)
            stream.read_int('unknown', expected=0)
            stream.read_int('unknown', expected=0)
            value = stream.read_variant(variant_type, 'value')
            self.values[value] = description

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'name': self.name,
            'values': self.values,
            'domain_id': self.domain_id,
            'merge_policy': self.merge_policy,
            'split_policy': self.split_policy,
            'description': self.description,
            'owner': self.owner,
            'field_type': self.field_type,
        }
