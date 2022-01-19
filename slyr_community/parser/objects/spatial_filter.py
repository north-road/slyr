#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..object_registry import REGISTRY
from ..stream import Stream


class SpatialFilter(Object):
    """
    SpatialFilter
    """

    @staticmethod
    def cls_id():
        return 'fdfebd96-ed75-11d0-9a95-080009ec734b'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.sub_fields = ''
        self.where_clause = ''
        self.output_spatial_reference_field_name = ''
        self.output_spatial_reference = None
        self.spatial_resolution = 0
        self.postfix_clause = ''
        self.prefix_clause = ''
        self.filter_defs = None
        self.row_offset = None
        self.row_count = None
        self.spatial_relation = 0
        self.spatial_relation_description = ''
        self.reference_geometry = None
        self.geometry_field_name = ''
        self.fid_set = None

    def read(self, stream: Stream, version):
        internal_version = stream.read_ushort('internal version', expected=(1, 3, 4, 5))

        self.sub_fields = stream.read_string('sub fields')
        self.where_clause = stream.read_string('where clause')
        self.output_spatial_reference_field_name = stream.read_string('output spatial reference field name')
        self.output_spatial_reference = stream.read_object('output spatial reference')
        self.spatial_resolution = stream.read_double('spatial resolution')
        self.fid_set = stream.read_object('fid set')
        if internal_version > 1:
            self.postfix_clause = stream.read_stringv2('postfix clause')
            self.filter_defs = stream.read_object('array of filter def')
            self.prefix_clause = stream.read_stringv2('prefix clause')

        if internal_version > 4:
            res = stream.read_int('row offset')
            self.row_offset = res if res != 0xffffffff else None
            res = stream.read_int('row count')
            self.row_count = res if res != 0xffffffff else None
            stream.read_int('unknown', expected=0)
        elif internal_version != 3:
            # hm, don't like this!
            stream.read_int('unknown', expected=0)

        self.spatial_relation = stream.read_int('spatial relation')
        self.spatial_relation_description = stream.read_string('spatial relation description')
        self.reference_geometry = stream.read_object('reference geometry')
        self.geometry_field_name = stream.read_string('geometry field name')

        stream.read_ushort('unknown', expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'sub_fields': self.sub_fields,
            'where_clause': self.where_clause,
            'output_spatial_reference_field_name': self.output_spatial_reference_field_name,
            'output_spatial_reference': self.output_spatial_reference.to_dict() if self.output_spatial_reference else None,
            'spatial_resolution': self.spatial_resolution,
            'postfix_clause': self.postfix_clause,
            'prefix_clause': self.prefix_clause,
            'filter_defs': self.filter_defs.to_dict() if self.filter_defs else None,
            'row_offset': self.row_offset,
            'row_count': self.row_count,
            'spatial_relation': self.spatial_relation,
            'spatial_relation_description': self.spatial_relation_description,
            'reference_geometry': self.reference_geometry.to_dict() if self.reference_geometry else None,
            'geometry_field_name': self.geometry_field_name,
            'fid_set': self.fid_set.to_dict() if self.fid_set else None,
        }

    @classmethod
    def from_dict(cls, definition: dict) -> 'SpatialFilter':
        res = SpatialFilter()
        res.sub_fields = definition['sub_fields']
        res.where_clause = definition['where_clause']
        res.output_spatial_reference_field_name = definition['output_spatial_reference_field_name']
        res.output_spatial_reference = REGISTRY.create_object_from_dict(definition['output_spatial_reference'])
        res.spatial_resolution = definition['spatial_resolution']
        res.postfix_clause = definition['postfix_clause']
        res.prefix_clause = definition['prefix_clause']
        res.filter_defs = REGISTRY.create_object_from_dict(definition['filter_defs'])
        res.row_offset = definition['row_offset']
        res.row_count = definition['row_count']
        res.spatial_relation = definition['spatial_relation']
        res.spatial_relation_description = definition['spatial_relation_description']
        res.reference_geometry = REGISTRY.create_object_from_dict(definition['reference_geometry'])
        res.geometry_field_name = definition['geometry_field_name']
        res.fid_set = REGISTRY.create_object_from_dict(definition['fid_set'])
        return res
