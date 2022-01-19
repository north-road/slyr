#!/usr/bin/env python
"""
FeatureClassName -- reflects source data paths

NEAR COMPLETE INTERPRETATION:
Some components are of unknown use, but don't seem important and reading is robust
"""

from .geometry import Geometry
from ..object import Object
from ..object_registry import REGISTRY
from ..stream import Stream


class FeatureClassName(Object):
    """
    Feature class name
    """

    # feature types
    FEATURE_TYPES = {1: 'FT_SIMPLE',
                     7: 'FT_SIMPLE_JUNCTION',
                     8: 'FT_SIMPLE_EDGE',
                     9: 'FT_COMPLEX_JUNCTION',
                     10: 'FT_COMPLEX_EDGE',
                     11: 'FT_ANNOTATION',
                     12: 'FT_COVERAGE_ANNOTATION',
                     13: 'FT_DIMENSION',
                     14: 'FT_RASTER_CATALOG_ITEM'}

    @staticmethod
    def cls_id():
        return '198846d0-ca42-11d1-aa7c-00c04fa33a15'

    def __init__(self):
        super().__init__()
        self.name = ''
        self.dataset_name = None
        self.datasource_type = ''
        self.feature_type = 1
        self.model_name = ''
        self.shape_field_name = ''
        self.shape_type = Geometry.GEOMETRY_ANY

    @staticmethod
    def compatible_versions():
        return [1, 2]

    def read(self, stream: Stream, version):
        self.name = stream.read_string('layer name?')
        _ = stream.read_string('unknown')
        self.datasource_type = stream.read_string('datasource type')
        self.shape_field_name = stream.read_string('shape field name')
        self.shape_type = stream.read_uint('shape type')
        self.feature_type = stream.read_uint('feature type')
        _ = stream.read_ushort('unknown')
        self.dataset_name = stream.read_object('dataset name')
        if version == 2:
            extra = stream.read_ushort('topology count??')
            for i in range(extra):
                stream.read_object('topology {}??'.format(i + 1))

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'name': self.name,
            'dataset_name': self.dataset_name.to_dict() if self.dataset_name else None,
            'datasource_type': self.datasource_type,
            'feature_type': self.FEATURE_TYPES[self.feature_type],
            'shape_field_name': self.shape_field_name,
            'shape_type': Geometry.geometry_type_to_string(self.shape_type)
        }

    @classmethod
    def from_dict(cls, definition: dict) -> 'FeatureClassName':
        res = FeatureClassName()
        res.name = definition['name']
        res.dataset_name = REGISTRY.create_object_from_dict(definition['dataset_name'])
        res.datasource_type = definition['datasource_type']
        res.feature_type = [k for k, v in FeatureClassName.FEATURE_TYPES.items() if v == definition['feature_type']][0]
        res.shape_field_name = definition['shape_field_name']
        res.shape_type = Geometry.string_to_geometry_type(definition['shape_type'])
        return res


class FgdbFeatureClassName(FeatureClassName):
    """
    FgdbFeatureClassName
    """

    @staticmethod
    def cls_id():
        return '75e10086-4226-42ac-afec-cbb9b748f847'

    def __init__(self):
        super().__init__()
        self.compressed = False
        self.name_string = ''

    @staticmethod
    def compatible_versions():
        return [1]

    def read(self, stream: Stream, version):
        self.compressed = stream.read_ushort('compressed') != 0
        stream.read_ushort('unknown', expected=2)
        self.name = stream.read_string('layer name')
        self.name_string = stream.read_string('name string')
        self.datasource_type = stream.read_string('datasource type')
        self.shape_field_name = stream.read_string('shape_field_name')
        self.shape_type = stream.read_uint('shape_type')
        self.feature_type = stream.read_uint('feature_type')
        stream.read_ushort('unknown', expected=(0, 1))
        self.dataset_name = stream.read_object('dataset name')
        if version == 1:
            extra = stream.read_ushort('topology count??')
            for i in range(extra):
                stream.read_object('topology {}??'.format(i + 1))

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res['compressed'] = self.compressed
        res['name_string'] = self.name_string
        return res

    @classmethod
    def from_dict(cls, definition: dict) -> 'FgdbFeatureClassName':
        res = FgdbFeatureClassName()
        res.name = definition['name']
        res.compressed = definition['compressed']
        res.name_string = definition['name_string']
        res.dataset_name = REGISTRY.create_object_from_dict(definition['dataset_name'])
        res.datasource_type = definition['datasource_type']
        res.feature_type = [k for k, v in FeatureClassName.FEATURE_TYPES.items() if v == definition['feature_type']][0]
        res.shape_field_name = definition['shape_field_name']
        res.shape_type = Geometry.string_to_geometry_type(definition['shape_type'])
        return res


class RepresentationClassName(FeatureClassName):
    """
    RepresentationClassName
    """

    @staticmethod
    def cls_id():
        return '4e74aa22-a1b6-47d4-9914-20f8c6c2b699'

    def __init__(self):
        super().__init__()
        self.compressed = False
        self.name_string = ''

    @staticmethod
    def compatible_versions():
        return [1]

    def read(self, stream: Stream, version):
        self.name = stream.read_string('layer name')
        self.name_string = stream.read_string('name string')
        self.datasource_type = stream.read_string('datasource type')
        self.dataset_name = stream.read_object('dataset name')

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res['name_string'] = self.name_string
        return res

    @classmethod
    def from_dict(cls, definition: dict) -> 'RepresentationClassName':
        res = RepresentationClassName()
        res.name = definition['name']
        res.compressed = definition['compressed']
        res.name_string = definition['name_string']
        res.dataset_name = REGISTRY.create_object_from_dict(definition['dataset_name'])
        res.datasource_type = definition['datasource_type']
        res.feature_type = [k for k, v in FeatureClassName.FEATURE_TYPES.items() if v == definition['feature_type']][0]
        res.shape_field_name = definition['shape_field_name']
        res.shape_type = Geometry.string_to_geometry_type(definition['shape_type'])
        return res


class GpkgFeatureClassName(FeatureClassName):
    """
    GpkgFeatureClassName
    """

    @staticmethod
    def cls_id():
        return '793873de-c0bb-48f4-a6bf-f6f83fa3c1bc'

    def __init__(self):
        super().__init__()
        self.query = None
        self.topologies = []

    @staticmethod
    def compatible_versions():
        return [2]

    def read(self, stream: Stream, version):
        self.name = stream.read_string('layer name')
        stream.read_string('unknown', expected='')
        self.datasource_type = stream.read_string('datasource type')
        self.dataset_name = stream.read_object('dataset name')
        if version == 1:
            extra = stream.read_ushort('topology count??')
            for i in range(extra):
                self.topologies.append(stream.read_object('topology {}??'.format(i + 1)))
        self.query = stream.read_object('query')

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res['topologies'] = [t.to_dict() for t in self.topologies]
        res['query'] = self.query.to_dict() if self.query else None
        return res

    @classmethod
    def from_dict(cls, definition: dict) -> 'GpkgFeatureClassName':
        res = GpkgFeatureClassName()
        res.name = definition['name']
        res.query = REGISTRY.create_object_from_dict(definition['query'])
        # todo -- topologies?
        res.dataset_name = REGISTRY.create_object_from_dict(definition['dataset_name'])
        res.datasource_type = definition['datasource_type']
        res.feature_type = [k for k, v in FeatureClassName.FEATURE_TYPES.items() if v == definition['feature_type']][0]
        res.shape_field_name = definition['shape_field_name']
        res.shape_type = Geometry.string_to_geometry_type(definition['shape_type'])
        return res


class GpkgFeatureClassQuery(Object):
    """
    GpkgFeatureClassQuery - unknown component
    """

    @staticmethod
    def cls_id():
        return '712881f6-daf7-46f1-bc75-a47a15694a38'

    def __init__(self):
        super().__init__()
        self.query = ''
        self.fid = ''
        self.geometry_field = ''
        self.esri_oid = ''
        self.fields = None
        self.crs = None

    @staticmethod
    def compatible_versions():
        return [2, 3]

    def read(self, stream: Stream, version):
        stream.read_string('unknown, crs related?')
        self.query = stream.read_string('query')
        self.fid = stream.read_string('fid')
        self.geometry_field = stream.read_string('geom')
        self.esri_oid = stream.read_string('esri_oid', expected='ESRI_OID')
        stream.read_string('unknown')  # fid, objectid
        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=1)
        stream.read_int('unknown', expected=(3, 4))
        self.fields = stream.read_object('fields')

        self.crs = stream.read_object('crs')

        if version > 2:
            stream.read_int('unknown', expected=11)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'query': self.query,
            'fid': self.fid,
            'geometry_field': self.geometry_field,
            'esri_oid': self.esri_oid,
            'fields': self.fields.to_dict() if self.fields else None,
            'crs': self.crs.to_dict() if self.crs else None
        }

    @classmethod
    def from_dict(cls, definition: dict) -> 'GpkgFeatureClassQuery':
        res = GpkgFeatureClassQuery()
        res.query = definition['query']
        res.fid = definition['fid']
        res.geometry_field = definition['geometry_field']
        res.esri_oid = definition['esri_oid']
        res.fields = REGISTRY.create_object_from_dict(definition['fields'])
        res.crs = REGISTRY.create_object_from_dict(definition['crs'])
        return res


class TopologyName(Object):
    """
    TopologyName
    """

    @staticmethod
    def cls_id():
        return '9fca50ec-c413-440c-b453-49a591440096'

    def read(self, stream: Stream, version):
        stream.read_string('unknown')
        stream.read_string('unknown')
        stream.read_object('unknown')
        # assert stream.read_int('unknown') == 1


class CoverageFeatureClassName(FeatureClassName):
    """
    CoverageFeatureClassName
    """

    FEATURE_CLASS_TYPES = {1: 'CFCT_POINT',
                           2: 'CFCT_ARC',
                           3: 'CFCT_POLYGON',
                           4: 'CFCT_NODE',
                           5: 'CFCT_TIC',
                           6: 'CFCT_ANNOTATION',
                           7: 'CFCT_SECTION',
                           8: 'CFCT_ROUTE',
                           9: 'CFCT_LINK',
                           11: 'CFCT_REGION',
                           51: 'CFCT_LABEL',
                           666: 'CFCT_FILE'}

    FEATURE_CLASS_TOPOLOGY = {0: 'FCT_NA',
                              1: 'FCT_PRELIMINARY',
                              2: 'FCT_EXISTS',
                              3: 'FCT_UNKNOWN'}

    @staticmethod
    def cls_id():
        return '72f77de8-122a-11d3-9f31-00c04f79927c'

    def __init__(self):
        super().__init__()
        self.class_type = 1
        self.topology = 0
        self.dataset_name = None
        self.dataset_name_string = ''

    @staticmethod
    def compatible_versions():
        return [1]

    def read(self, stream: Stream, version):
        self.class_type = stream.read_uint('feature class type')
        self.topology = stream.read_uint('topology')
        stream.read_uchar('unknown', expected=1)
        internal_version = stream.read_uchar('internal version', expected=(1, 2))
        stream.read_uchar('unknown', expected=0)
        self.name = stream.read_string('layer name')
        self.dataset_name_string = stream.read_string('dataset_name_string')
        self.datasource_type = stream.read_string('datasource type')
        self.shape_field_name = stream.read_string('shape_field_name')
        self.shape_type = stream.read_uint('shape_type')
        self.feature_type = stream.read_uint('feature_type')
        stream.read_ushort('unknown', expected=(0, 1))
        self.dataset_name = stream.read_object('unknown name')
        if internal_version > 1:
            stream.read_ushort('unknown', expected=0)

    def to_dict(self):  # pylint: disable=method-hidden
        res = super().to_dict()
        res['class_type'] = CoverageFeatureClassName.FEATURE_CLASS_TYPES[self.class_type]
        res['topology'] = CoverageFeatureClassName.FEATURE_CLASS_TOPOLOGY[self.topology]
        res['dataset_name_string'] = self.dataset_name_string
        return res

    @classmethod
    def from_dict(cls, definition: dict) -> 'CoverageFeatureClassName':
        res = CoverageFeatureClassName()
        res.name = definition['name']
        res.dataset_name = REGISTRY.create_object_from_dict(definition['dataset_name'])
        res.datasource_type = definition['datasource_type']
        res.feature_type = [k for k, v in FeatureClassName.FEATURE_TYPES.items() if v == definition['feature_type']][0]
        res.shape_field_name = definition['shape_field_name']
        res.shape_type = Geometry.string_to_geometry_type(definition['shape_type'])

        res.class_type = \
        [k for k, v in CoverageFeatureClassName.FEATURE_CLASS_TYPES.items() if v == definition['class_type']][0]
        res.topology = \
        [k for k, v in CoverageFeatureClassName.FEATURE_CLASS_TOPOLOGY.items() if v == definition['topology']][0]
        res.dataset_name_string = definition['dataset_name_string']
        return res


class CoverageName(Object):
    """
    CoverageName
    """

    @staticmethod
    def cls_id():
        return '1e921c72-122f-11d3-9f31-00c04f79927c'

    def __init__(self):
        super().__init__()
        self.name = ''
        self.dataset_name = ''

    @staticmethod
    def compatible_versions():
        return [1]

    def read(self, stream: Stream, version):
        stream.read_uint('internal version', expected=(2, 3, 4))
        stream.read_ushort('unknown', expected=1)
        self.name = stream.read_string('layer name')
        stream.read_string('unknown')
        stream.read_string('unknown')
        stream.read_uint('unknown', expected=2)
        stream.read_ushort('unknown', expected=0)
        stream.read_uchar('unknown', expected=0)
        self.dataset_name = stream.read_object('dataset name')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'name': self.name,
            'dataset_name': self.dataset_name.to_dict() if self.dataset_name else None
        }

    @classmethod
    def from_dict(cls, definition: dict) -> 'CoverageName':
        res = CoverageName()
        res.name = definition['name']
        res.dataset_name = REGISTRY.create_object_from_dict(definition['dataset_name'])
        return res


class WmsConnectionName(Object):
    """
    WmsConnectionName
    """

    @staticmethod
    def cls_id():
        return '98b0e997-f21d-4195-8e06-f9cd2ad97165'

    def __init__(self):
        super().__init__()
        self.properties = None

    @staticmethod
    def compatible_versions():
        return [1, 2]

    def read(self, stream: Stream, version):
        self.properties = stream.read_object('properties')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'properties': self.properties.to_dict() if self.properties else None
        }
