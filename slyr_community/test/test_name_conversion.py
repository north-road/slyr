# pylint: disable=bad-continuation,too-many-lines

"""
Test layer source conversion
"""

import unittest
from copy import deepcopy

from qgis.core import QgsCoordinateReferenceSystem

from ..converters.context import Context
from ..converters.dataset_name import DatasetNameConverter
from ..parser.initalize_registry import initialize_registry
from ..parser.object_registry import REGISTRY

expected = {
    'GDB Annotation': {
        'object': {
            'name': 'point_labelsAnno',
            'dataset_name': {
                'category': '',
                'name': '',
                'subset_names': None,
                'dataset_type': 'DATASET_TYPE_CONTAINER',
                'workspace_name': {'name': 'S:\\slyr_test_gdb.gdb',
                                   'browse_name': 'slyr_test_gdb',
                                   'connection_properties': None,
                                   'path_name': '',
                                   'workspace_type': 'ESRI_LOCALDATABASE_WORKSPACE',
                                   'workspace_factory': {
                                       'type': 'FileGDBWorkspaceFactory',
                                       'version': 1},
                                   'name_string': '',
                                   'type': 'WorkspaceName',
                                   'version': 1},
                'type': 'FeatureDatasetName',
                'version': 1},
            'datasource_type': 'File Geodatabase Feature Class',
            'feature_type': 'FT_ANNOTATION',
            'shape_field_name': 'SHAPE',
            'shape_type': 'polygon',
            'compressed': False,
            'name_string': '',
            'type': 'FgdbFeatureClassName',
            'version': 1
        },
        'base': '/home/me/test_slyr/Aaaaa',
        'crs': 'EPSG:4326',
        'subset': '',
        'expected': {
            'uri': 'S:/slyr_test_gdb.gdb|layername=point_labelsAnno',
            'provider': 'ogr',
            'wkb_type': 6,
            'file_name': 'S:/slyr_test_gdb.gdb',
            'factory': 'FileGDBWorkspaceFactory'
        }
    },
    'GDB Point': {
        'object': {
            'name': 'Point_test',
            'dataset_name': {
                'name': 'S:\\slyr_test_gdb.gdb',
                'browse_name': 'slyr_test_gdb',
                'connection_properties': None,
                'path_name': '',
                'workspace_type': 'ESRI_LOCALDATABASE_WORKSPACE',
                'workspace_factory': {
                    'type': 'FileGDBWorkspaceFactory',
                    'version': 1
                },
                'name_string': '',
                'type': 'WorkspaceName',
                'version': 1
            },
            'datasource_type': 'File Geodatabase Feature Class',
            'feature_type': 'FT_SIMPLE',
            'shape_field_name': 'Shape',
            'shape_type': 'point',
            'compressed': False,
            'name_string': '',
            'type': 'FgdbFeatureClassName',
            'version': 1
        },
        'base': '/home/me/test_slyr/Aaaaa',
        'crs': 'EPSG:4326',
        'subset': 'View = 1',
        'expected': {
            'uri': 'S:/slyr_test_gdb.gdb|layername=Point_test',
            'provider': 'ogr',
            'wkb_type': 1,
            'file_name': 'S:/slyr_test_gdb.gdb',
            'factory': 'FileGDBWorkspaceFactory'
        }
    },
    'coverage polygons': {
        'object': {
            'name': 'polygon',
            'dataset_name': {
                'name': 'jjjjjjjj',
                'dataset_name': {
                    'name': 'g:\\grgrgrgrgr\\knknknkn\\bgbgbgbgbg',
                    'browse_name': 'ARC/INFO Data',
                    'connection_properties': {
                        'DATABASE': 'G:\\grgrgrgrgr\\knknknkn\\bgbgbgbgbg',
                        'type': 'PropertySet',
                        'version': 1
                    },
                    'path_name': '',
                    'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                    'workspace_factory': {
                        'type': 'ArcInfoWorkspaceFactory',
                        'version': 1
                    },
                    'name_string': 'ARCINFO: Workspace = \\\\nir\\Gaaagggg\\grgrgrgrgr\\knknknkn\\bgbgbgbgbg;',
                    'type': 'WorkspaceName',
                    'version': 1
                },
                'type': 'CoverageName',
                'version': 1
            },
            'datasource_type': 'Polygon Feature Class',
            'feature_type': 'FT_SIMPLE',
            'shape_field_name': 'Shape',
            'shape_type': 'polygon',
            'class_type': 'CFCT_POLYGON',
            'topology': 'FCT_EXISTS',
            'dataset_name_string': 'ARCINFO: Workspace = \\\\nir\\Gaaagggg\\grgrgrgrgr\\knknknkn\\bgbgbgbgbg\\; Coverage = jjjjjjjj; FeatureClass = polygon;',
            'type': 'CoverageFeatureClassName',
            'version': 1
        },
        'base': '/home/me/test_slyr/Aaaaa Aaa/LYRs',
        'crs': '',
        'subset': '',
        'skip_old': True,
        'expected': {
            'uri': 'g:/grgrgrgrgr/knknknkn/bgbgbgbgbg/jjjjjjjj|layername=PAL',
            'provider': 'ogr',
            'wkb_type': 6,
            'file_name': 'g:/grgrgrgrgr/knknknkn/bgbgbgbgbg/jjjjjjjj',
            'factory': 'ArcInfoWorkspaceFactory'
        }
    },
    'dbase table': {
        'object': {
            'name': 'Sum_Output',
            'category': '',
            'datasource_type': 'dBASE Table',
            'workspace_name': {
                'name': 'L:\\Jajaja\\Vlssss_151515',
                'browse_name': 'Shapefile Data',
                'connection_properties': {
                    'DATABASE': 'L:\\Jajaja\\Vlssss_151515',
                    'type': 'PropertySet',
                    'version': 1
                },
                'path_name': '',
                'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                'workspace_factory': {
                    'type': 'ShapefileWorkspaceFactory',
                    'version': 1
                },
                'name_string': 'ARCINFO: Workspace = \\\\alta0\\gis\\Jajaja\\Vlssss_151515;',
                'type': 'WorkspaceName',
                'version': 1
            },
            'type': 'TableName',
            'version': 1
        },
        'base': '/home/me/test_slyr/Aaaaa Aaa/MXDs',
        'crs': '',
        'subset': '',
        'skip_old': True,
        'expected': {
            'uri': 'L:/Jajaja/Vlssss_151515/Sum_Output.dbf',
            'provider': 'ogr',
            'wkb_type': 100,
            'file_name': 'L:/Jajaja/Vlssss_151515/Sum_Output.dbf',
            'factory': 'ShapefileWorkspaceFactory'
        }
    },
    'compressed gdb': {
        'object': {
            'name': 'issss_issss_100th',
            'dataset_name': {
                'category': '',
                'name': '',
                'subset_names': None,
                'dataset_type': 'DATASET_TYPE_CONTAINER',
                'workspace_name': {
                    'name': 'L:\\Inland\\KS50V1.1\\KS_50V_1.1_III99\\KS_50V_1.1.gdb',
                    'browse_name': 'KS_50V_1.1',
                    'connection_properties': {
                        'DATABASE': 'L:\\Inland\\KS50V1.1\\KS_50V_1.1_III99\\KS_50V_1.1.gdb',
                        'type': 'PropertySet',
                        'version': 1
                    },
                    'path_name': '',
                    'workspace_type': 'ESRI_LOCALDATABASE_WORKSPACE',
                    'workspace_factory': {
                        'type': 'FileGDBWorkspaceFactory',
                        'version': 1
                    },
                    'name_string': '',
                    'type': 'WorkspaceName',
                    'version': 1
                },
                'type': 'FeatureDatasetName',
                'version': 1
            },
            'datasource_type': 'File Geodatabase Feature Class (compressed)',
            'feature_type': 'FT_ANNOTATION',
            'shape_field_name': 'SHAPE',
            'shape_type': 'polygon',
            'compressed': True,
            'name_string': '',
            'type': 'FgdbFeatureClassName',
            'version': 1
        },
        'base': '/home/me/test_slyr/Aaaaa Aaa/MXDs',
        'crs': 'EPSG:3057',
        'subset': '',
        'expected': {
            'uri': 'L:/Inland/KS50V1.1/KS_50V_1.1_III99/KS_50V_1.1.gdb|layername=issss_issss_100th',
            'provider': 'ogr',
            'wkb_type': 6,
            'file_name': 'L:/Inland/KS50V1.1/KS_50V_1.1_III99/KS_50V_1.1.gdb',
            'factory': 'FileGDBWorkspaceFactory'
        }
    },
    'Personal geodatabase table': {
        'object': {
            'name': 'Faaaaaa_ghhh_RTR',
            'category': '',
            'datasource_type': 'Personal Geodatabase Table',
            'workspace_name': {
                'name': 'L:\\1248\\North.mdb',
                'browse_name': 'North',
                'connection_properties': {
                    'DATABASE': 'L:\\1248\\North.mdb',
                    'type': 'PropertySet',
                    'version': 1
                },
                'path_name': '',
                'workspace_type': 'ESRI_LOCALDATABASE_WORKSPACE',
                'workspace_factory': {
                    'type': 'AccessWorkspaceFactory',
                    'version': 1
                },
                'name_string': '',
                'type': 'WorkspaceName',
                'version': 1
            },
            'type': 'TableName',
            'version': 1
        },
        'base': '/home/me/test_slyr/Aaaaa Aaa/MXDs',
        'crs': '',
        'subset': '',
        'expected': {
            'uri': 'L:/1248/North.mdb|layername=Faaaaaa_ghhh_RTR',
            'provider': 'ogr',
            'wkb_type': 100,
            'file_name': 'L:/1248/North.mdb',
            'factory': 'AccessWorkspaceFactory'
        }
    },
    'XLSX': {
        'object': {
            'name': "'Rrrrr-Llllllll$'",
            'category': '',
            'datasource_type': 'Excel Table',
            'workspace_name': {
                'name': 'L:\\1148\\vnnnnnoooonn\\xls\\eeraaarerrrrr yuuuyuuu 2123.xlsx',
                'browse_name': 'eeraaarerrrrr yuuuyuuu 2123',
                'connection_properties': {
                    'DATABASE': 'L:\\1148\\vnnnnnoooonn\\xls\\eeraaarerrrrr yuuuyuuu 2123.xlsx',
                    'CONNECTSTRING': 'Provider=Microsoft.ACE.OLEDB.12.0;Data Source=L:\\1148\\vnnnnnoooonn\\xls\\eeraaarerrrrr yuuuyuuu 2123.xlsx;Extended Properties="Excel 12.0;HDR=Yes;IMEX=1;"',
                    'type': 'PropertySet',
                    'version': 1
                },
                'path_name': '',
                'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                'workspace_factory': {
                    'type': 'ExcelOrMdbWorkspaceFactory',
                    'version': 1
                },
                'name_string': '',
                'type': 'WorkspaceName',
                'version': 1
            },
            'type': 'TableName',
            'version': 1
        },
        'base': '/home/me/test_slyr/Aaaaa Aaa/MXDs',
        'crs': '',
        'subset': '',
        'expected': {
            'uri': 'L:/1148/vnnnnnoooonn/xls/eeraaarerrrrr yuuuyuuu 2123.xlsx|layername=Rrrrr-Llllllll',
            'provider': 'ogr',
            'wkb_type': 100,
            'file_name': 'L:/1148/vnnnnnoooonn/xls/eeraaarerrrrr yuuuyuuu 2123.xlsx',
            'factory': 'ExcelOrMdbWorkspaceFactory'
        }
    },
    'Coverage annotation': {
        'object': {
            'name': 'annotation.vatn',
            'dataset_name': {
                'name': 'noffffhg',
                'dataset_name': {
                    'name': 'l:\\v-kkoo\\rert\\cov',
                    'browse_name': 'ARC/INFO Data',
                    'connection_properties': None,
                    'path_name': '',
                    'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                    'workspace_factory': {
                        'type': 'ArcInfoWorkspaceFactory',
                        'version': 1},
                    'name_string': 'ARCINFO: Workspace = \\\\vvv-fdf\\data\\v-kkoo\\rert\\cov;',
                    'type': 'WorkspaceName',
                    'version': 1
                },
                'type': 'CoverageName',
                'version': 1
            },
            'datasource_type': 'Annotation Feature Class',
            'feature_type': 'FT_COVERAGE_ANNOTATION',
            'shape_field_name': 'Shape',
            'shape_type': 'polyline',
            'class_type': 'CFCT_ANNOTATION',
            'topology': 'FCT_NA',
            'dataset_name_string': 'ARCINFO: Workspace = \\\\vvv-fdf\\data\\v-kkoo\\rert\\cov\\; Coverage = noffffhg; FeatureClass = annotation.vatn;',
            'type': 'CoverageFeatureClassName',
            'version': 1
        },
        'base': '/home/me/test_slyr/Aaaaa Aaa/MXDs',
        'crs': '',
        'subset': '',
        'skip_old': True,
        'expected': {
            'uri': 'l:/v-kkoo/rert/cov/noffffhg|layername=vatn',
            'provider': 'ogr',
            'wkb_type': 5,
            'file_name': 'l:/v-kkoo/rert/cov/noffffhg',
            'factory': 'ArcInfoWorkspaceFactory'
        }
    },
    'xy event source': {
        'object': {
            'name': 'ssssssaaaa_123123_Features',
            'feature_dataset_name': {
                'name': 'sssaaaa_123123',
                'category': '',
                'datasource_type': 'Personal Geodatabase Table',
                'workspace_name': {
                    'name': 'L:\\Inland\\TTT\\saaaattt_trtr20010101.mdb',
                    'browse_name': 'saaaattt_trtr20010101',
                    'connection_properties': {
                        'DATABASE': 'L:\\Inland\\TTT\\saaaattt_trtr20010101.mdb',
                        'type': 'PropertySet',
                        'version': 1
                    },
                    'path_name': '',
                    'workspace_type': 'ESRI_LOCALDATABASE_WORKSPACE',
                    'workspace_factory': {
                        'type': 'AccessWorkspaceFactory',
                        'version': 1
                    },
                    'name_string': '',
                    'type': 'WorkspaceName',
                    'version': 1
                },
                'type': 'TableName',
                'version': 1
            },
            'event_properties': {
                'x_field': 'X',
                'y_field': 'Y',
                'z_field': '',
                'type': 'XYEvent2FieldsProperties',
                'version': 1
            },
            'crs': {
                'wkt': 'PROJCS["WGS_1984_Lambert_Conformal_Conic",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["false_easting",500000.0],PARAMETER["false_northing",500000.0],PARAMETER["central_meridian",-19.0],PARAMETER["standard_parallel_1",64.25],PARAMETER["standard_parallel_2",65.75],PARAMETER["latitude_of_origin",65.0],UNIT["Meter",1.0]]',
                'x_origin': -34541500.0,
                'y_origin': -31559400.0,
                'm_origin': -100000.0,
                'z_origin': -100000.0,
                'xy_scale': 10000.0,
                'm_scale': 10000.0,
                'z_scale': 10000.0,
                'xy_tolerance': 0.001,
                'z_tolerance': 0.001,
                'm_tolerance': 0.001,
                'is_high_precision': True,
                'type': 'ProjectedCoordinateSystem',
                'version': 6
            },
            'type': 'XYEventSourceName',
            'version': 1
        },
        'base': '/home/me/test_slyr/Aaaaa Aaa/MXDs',
        'crs': '',
        'subset': '',
        'skip_old': True,
        'expected': {
            'uri': 'L:/Inland/TTT/saaaattt_trtr20010101.mdb|layername=sssaaaa_123123',
            'provider': 'ogr',
            'wkb_type': 100,
            'file_name': 'L:/Inland/TTT/saaaattt_trtr20010101.mdb',
            'factory': 'AccessWorkspaceFactory'
        }
    },
    'Coverage point': {
        'object': {
            'name': 'point',
            'dataset_name': {
                'name': 'mnnnooop',
                'dataset_name': {
                    'name': 'l:\\v-kkoo\\rert\\mmm66',
                    'browse_name': 'ARC/INFO Data',
                    'connection_properties': None,
                    'path_name': '',
                    'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                    'workspace_factory': {
                        'type': 'ArcInfoWorkspaceFactory',
                        'version': 1
                    },
                    'name_string': 'ARCINFO: Workspace = \\\\vvv-fdf\\data\\v-kkoo\\rert\\mmm66;',
                    'type': 'WorkspaceName',
                    'version': 1
                },
                'type': 'CoverageName',
                'version': 1
            },
            'datasource_type': 'Point Feature Class',
            'feature_type': 'FT_SIMPLE',
            'shape_field_name': 'Shape',
            'shape_type': 'point',
            'class_type': 'CFCT_POINT',
            'topology': 'FCT_NA',
            'dataset_name_string': 'ARCINFO: Workspace = \\\\vvv-fdf\\data\\v-kkoo\\rert\\mmm66\\; Coverage = mnnnooop; FeatureClass = point;',
            'type': 'CoverageFeatureClassName',
            'version': 1
        },
        'base': '/home/me/test_slyr/Aaaaa Aaa/MXDs',
        'crs': '',
        'subset': '',
        'skip_old': True,
        'expected': {
            'uri': 'l:/v-kkoo/rert/mmm66/mnnnooop|layername=LAB',
            'provider': 'ogr',
            'wkb_type': 1,
            'file_name': 'l:/v-kkoo/rert/mmm66/mnnnooop',
            'factory': 'ArcInfoWorkspaceFactory'
        }
    },
    'Coverage relative path': {
        'object': {
            'name': 'polygon',
            'dataset_name': {
                'name': 'provinces',
                'dataset_name': {
                    'name': '.',
                    'browse_name': 'ARC/INFO Data',
                    'connection_properties': None,
                    'path_name': '',
                    'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                    'workspace_factory': {
                        'type': 'ArcInfoWorkspaceFactory',
                        'version': 1
                    },
                    'name_string': 'ARCINFO: Workspace = \\\\WWWWEEEE-PC\\T$\\brrrraaaa\\workspace\\eeeee.ws\\aa_illlll.ws;',
                    'type': 'WorkspaceName',
                    'version': 1
                },
                'type': 'CoverageName',
                'version': 1
            },
            'datasource_type': 'Clase de entidad poligonal',
            'feature_type': 'FT_SIMPLE',
            'shape_field_name': 'Shape',
            'shape_type': 'polygon',
            'class_type': 'CFCT_POLYGON',
            'topology': 'FCT_EXISTS',
            'dataset_name_string': 'ARCINFO: Workspace = \\\\WWWWEEEE-PC\\T$\\brrrraaaa\\workspace\\eeeee.ws\\aa_illlll.ws\\; Coverage = provinces; FeatureClass = polygon;',
            'type': 'CoverageFeatureClassName',
            'version': 1
        },
        'base': '/home/me/test_slyr/Anaaaaaa/project',
        'crs': 'EPSG:25830',
        'subset': '',
        'skip_old': True,
        'expected': {
            'uri': '/home/me/test_slyr/Anaaaaaa/project/provinces|layername=PAL',
            'provider': 'ogr',
            'wkb_type': 6,
            'file_name': '/home/me/test_slyr/Anaaaaaa/project/provinces',
            'factory': 'ArcInfoWorkspaceFactory'
        }
    },
    'Ole DB factory': {
        'object': {
            'name': 'aaa2333tttt',
            'category': '',
            'datasource_type': 'EXCEL Table',
            'workspace_name': {
                'name': 'K:\\2021.03\\13\\rree\\awww\\mxd\\uytre\\2021-01-01-ttrr',
                'browse_name': 'OLE DB Connection',
                'connection_properties': None,
                'path_name': '',
                'workspace_type': 'ESRI_REMOTEDATABASE_WORKSPACE',
                'workspace_factory': {
                    'type': 'OLEDBWorkspaceFactory',
                    'version': 1
                },
                'name_string': '',
                'type': 'WorkspaceName',
                'version': 1
            },
            'type': 'TableName',
            'version': 1
        },
        'base': '/home/me/test_slyr/Aaaaa Aaa/MXDs',
        'crs': '',
        'subset': '',
        'skip_old': True,
        'expected': {
            'uri': 'K:/2021.03/13/rree/awww/mxd/uytre/2021-01-01-ttrr.xlsx|layername=aaa2333tttt',
            'provider': 'ogr',
            'wkb_type': 100,
            'file_name': 'K:/2021.03/13/rree/awww/mxd/uytre/2021-01-01-ttrr.xlsx',
            'factory': 'OLEDBWorkspaceFactory'
        }
    },
    'text file': {
        'object': {
            'name': 'f .txt',
            'category': '',
            'datasource_type': 'Text File',
            'workspace_name': {
                'name': 'L:\\123333\\awww\\frrrrre_trrrrrrr',
                'browse_name': 'frrrrre_trrrrrrr',
                'connection_properties': {
                    'DATABASE': 'L:\\123333\\awww\\frrrrre_trrrrrrr',
                    'type': 'PropertySet',
                    'version': 1
                },
                'path_name': '',
                'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                'workspace_factory': {
                    'type': 'TextFileWorkspaceFactory',
                    'version': 1
                },
                'name_string': '',
                'type': 'WorkspaceName',
                'version': 1
            },
            'type': 'TableName',
            'version': 1
        },
        'base': '/home/me/test_slyr/Aaaaa Aaa/MXDs', 'crs': '',
        'subset': '',
        'skip_old': True,
        'expected': {
            'uri': 'L:/123333/awww/frrrrre_trrrrrrr/f .txt',
            'provider': 'ogr',
            'wkb_type': 100,
            'file_name': 'L:/123333/awww/frrrrre_trrrrrrr/f .txt',
            'factory': 'TextFileWorkspaceFactory'
        }
    },
    'fgdb table name': {
        'object': {
            'name': 'Vrrrvvvrr_hhh',
            'category': '',
            'datasource_type': 'File Geodatabase Table',
            'workspace_name': {
                'name': '..\\Raarrrraaa.gdb',
                'browse_name': 'Raarrrraaa',
                'connection_properties': None,
                'path_name': '',
                'workspace_type': 'ESRI_LOCALDATABASE_WORKSPACE',
                'workspace_factory': {
                    'type': 'FileGDBWorkspaceFactory',
                    'version': 1
                },
                'name_string': '',
                'type': 'WorkspaceName',
                'version': 1
            },
            'type': 'FgdbTableName',
            'version': 1
        },
        'base': '/home/me/test_slyr/Aaaaa Aaa/MXDs',
        'crs': '',
        'subset': '',
        'expected': {
            'uri': '/home/me/test_slyr/Aaaaa Aaa/MXDs/../Raarrrraaa.gdb|layername=Vrrrvvvrr_hhh',
            'provider': 'ogr',
            'wkb_type': 100,
            'file_name': '/home/me/test_slyr/Aaaaa Aaa/MXDs/../Raarrrraaa.gdb',
            'factory': 'FileGDBWorkspaceFactory'
        }
    },
    'shapefile': {
        'object': {
            'name': 'H_2021_FNNA-Contours',
            'dataset_name': {
                'name': '..\\Shp\\Treeeee\\Georref',
                'browse_name': 'Shapefile Data',
                'connection_properties': None,
                'path_name': '',
                'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                'workspace_factory': {
                    'type': 'ShapefileWorkspaceFactory',
                    'version': 1
                },
                'name_string': '',
                'type': 'WorkspaceName',
                'version': 1
            },
            'datasource_type': 'Shapefile Feature Class',
            'feature_type': 'FT_SIMPLE',
            'shape_field_name': 'Shape',
            'shape_type': 'polygon',
            'type': 'FeatureClassName',
            'version': 2
        },
        'base': '/home/me/test_slyr/Aaaaa Ccaaa Trtrrr',
        'crs': 'EPSG:32630',
        'subset': '"NAME" = \'LD_55\' OR "NAME" = \'LD_60\' OR "NAME" = \'LD_65\' OR "NAME" = \'LD_68\' OR "NAME" = \'LD_70\'',
        'expected': {
            'uri': '/home/me/test_slyr/Aaaaa Ccaaa Trtrrr/../Shp/Treeeee/Georref/H_2021_FNNA-Contours.shp',
            'provider': 'ogr',
            'wkb_type': 6,
            'file_name': '/home/me/test_slyr/Aaaaa Ccaaa Trtrrr/../Shp/Treeeee/Georref/H_2021_FNNA-Contours.shp',
            'factory': 'ShapefileWorkspaceFactory'
        }
    },
    'fgdb table name 2': {
        'object': {
            'name': 'Vrrrvvvrr_hhh',
            'category': '',
            'datasource_type': 'File Geodatabase Table',
            'workspace_name': {
                'name': '..\\Raarrrraaa.gdb',
                'browse_name': 'Raarrrraaa',
                'connection_properties': None,
                'path_name': '',
                'workspace_type': 'ESRI_LOCALDATABASE_WORKSPACE',
                'workspace_factory': {
                    'type': 'FileGDBWorkspaceFactory',
                    'version': 1
                },
                'name_string': '',
                'type': 'WorkspaceName',
                'version': 1
            },
            'type': 'FgdbTableName',
            'version': 1
        },
        'base': '/home/me/test_slyr/Aaaaa Aaa/MXDs',
        'crs': '',
        'subset': '',
        'expected': {
            'uri': '/home/me/test_slyr/Aaaaa Aaa/MXDs/../Raarrrraaa.gdb|layername=Vrrrvvvrr_hhh',
            'provider': 'ogr',
            'wkb_type': 100,
            'file_name': '/home/me/test_slyr/Aaaaa Aaa/MXDs/../Raarrrraaa.gdb',
            'factory': 'FileGDBWorkspaceFactory'
        }
    },
    'polygon coverage': {
        'object': {
            'name': 'polygon',
            'dataset_name': {
                'name': 'hyhyhyh00',
                'dataset_name': {
                    'name': 'l:\\v-kkoo\\rert\\mmm66',
                    'browse_name': 'ARC/INFO Data',
                    'connection_properties': None,
                    'path_name': '',
                    'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                    'workspace_factory': {
                        'type': 'ArcInfoWorkspaceFactory',
                        'version': 1
                    },
                    'name_string': 'ARCINFO: Workspace = \\\\vvv-fdf\\data\\v-kkoo\\rert\\mmm66;',
                    'type': 'WorkspaceName',
                    'version': 1
                },
                'type': 'CoverageName',
                'version': 1
            },
            'datasource_type': 'Polygon Feature Class',
            'feature_type': 'FT_SIMPLE',
            'shape_field_name': 'Shape',
            'shape_type': 'polygon',
            'class_type': 'CFCT_POLYGON',
            'topology': 'FCT_EXISTS',
            'dataset_name_string': 'ARCINFO: Workspace = \\\\vvv-fdf\\data\\v-kkoo\\rert\\mmm66\\; Coverage = hyhyhyh00; FeatureClass = polygon;',
            'type': 'CoverageFeatureClassName',
            'version': 1
        },
        'base': '/home/me/test_slyr/Aaaaa Aaa/MXDs',
        'crs': '',
        'subset': '',
        'skip_old': True,
        'expected': {
            'uri': 'l:/v-kkoo/rert/mmm66/hyhyhyh00|layername=PAL',
            'provider': 'ogr',
            'wkb_type': 6,
            'file_name': 'l:/v-kkoo/rert/mmm66/hyhyhyh00',
            'factory': 'ArcInfoWorkspaceFactory'
        }
    },
    'feature service': {
        'object': {
            'name': '0',
            'dataset_name': {
                'name': 'http://rrrr-01.rrrrrrr.ca/arcgis/rest/services/Umffff/Hhhh_Vvvvv/FeatureServer',
                'browse_name': 'FeatureServer',
                'connection_properties': {
                    'DATABASE': 'http://rrrr-01.rrrrrrr.ca/arcgis/rest/services/Umffff/Hhhh_Vvvvv/FeatureServer',
                    'type': 'PropertySet',
                    'version': 1
                },
                'path_name': '',
                'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                'workspace_factory': {
                    'type': 'FeatureServiceWorkspaceFactory',
                    'version': 1
                },
                'name_string': '',
                'type': 'WorkspaceName',
                'version': 1
            },
            'datasource_type': 'Feature Service Feature Class',
            'feature_type': 'FT_SIMPLE',
            'shape_field_name': 'Shape',
            'shape_type': 'point',
            'type': 'FeatureClassName',
            'version': 2
        },
        'base': '/home/me/test_slyr/Aaaaa Aaa/MXDs',
        'crs': 'EPSG:3057',
        'subset': '',
        'expected': {
            'provider': 'arcgisfeatureserver',
            'uri': "crs='EPSG:3057' "
                   "url='http://rrrr-01.rrrrrrr.ca/arcgis/rest/services/Umffff/Hhhh_Vvvvv/FeatureServer/0'",
            'wkb_type': 1,
            'factory': 'FeatureServiceWorkspaceFactory'
        }
    },
    'sde': {
        'object': {
            'name': 'LLL_PPPPPP.Gkljrtett',
            'dataset_name': {
                'category': '',
                'name': '',
                'subset_names': None,
                'dataset_type': 'DATASET_TYPE_CONTAINER',
                'workspace_name': {
                    'name': 'C:\\Documents and Settings\\ghhh42\\Application Data\\ESRI\\ArcCatalog\\Connection to llalasd.rett.ca (5).sde',
                    'browse_name': 'ArcSDE Data',
                    'connection_properties': {
                        'SERVER': 'llalasd.rett.ca',
                        'INSTANCE': 'esri_sde',
                        'USER': 'ghhh42',
                        'PASSWORD': '******************************',
                        'VERSION': 'SDE.DEFAULT',
                        'type': 'PropertySet',
                        'version': 1
                    },
                    'path_name': '',
                    'workspace_type': 'ESRI_REMOTEDATABASE_WORKSPACE',
                    'workspace_factory': {
                        'type': 'SdeWorkspaceFactory',
                        'version': 1
                    },
                    'name_string': '',
                    'type': 'WorkspaceName',
                    'version': 1
                },
                'type': 'FeatureDatasetName',
                'version': 1
            },
            'datasource_type': 'SDE Feature Class',
            'feature_type': 'FT_SIMPLE',
            'shape_field_name': 'SHAPE',
            'shape_type': 'null',
            'type': 'FeatureClassName',
            'version': 2
        },
        'base': '/home/me/test_slyr/Aaaaa Aaa/MXDs',
        'crs': '',
        'subset': '',
        'skip_old': True,
        'expected': {
            'uri': 'C:/Documents and Settings/ghhh42/Application Data/ESRI/ArcCatalog/Connection to llalasd.rett.ca (5).sde|layername=LLL_PPPPPP.Gkljrtett',
            'provider': 'ogr',
            'wkb_type': 100,
            'file_name': 'C:/Documents and Settings/ghhh42/Application Data/ESRI/ArcCatalog/Connection to llalasd.rett.ca (5).sde',
            'factory': 'SdeWorkspaceFactory'
        }
    },
    'GPKG with table name': {
        'object': {
            'name': 'main.network_intersected',
            'dataset_name': {
                'name': 'c:\\users\\me\\my_gpkg.gpkg',
                'browse_name': 'hydro',
                'connection_properties': {
                    'DATABASE': 'c:\\users\\me\\my_gpkg.gpkg',
                    'type': 'PropertySet',
                    'version': 1
                },
                'path_name': '',
                'workspace_type': 'ESRI_LOCALDATABASE_WORKSPACE',
                'workspace_factory': {
                    'type': 'GpkgWorkspaceFactory',
                    'version': 1
                },
                'name_string': '',
                'type': 'WorkspaceName',
                'version': 1
            },
            'datasource_type': 'Feature Class',
            'shape_field_name': 'geom',
            'geometry_type': 7,
            'type': 'DBTableName',
        },
        'base': '/home/me/test_slyr/Aaaaa Aaa/MXDs',
        'crs': 'EPSG:3857',
        'subset': '',
        'expected': {
            'uri': 'c:/users/me/my_gpkg.gpkg|layername=network_intersected',
            'provider': 'ogr',
            'wkb_type': 7,
            'file_name': 'c:/users/me/my_gpkg.gpkg',
            'factory': 'GpkgWorkspaceFactory'
        }
    },
    'GPKG': {
        'object': {
            'name': 'main.%jjhjassddd',
            'dataset_name': {
                'name': '..\\gretyyasd_asdrerr\\jjhjassddd.gpkg',
                'browse_name': 'main',
                'connection_properties': {
                    'DATABASE': '..\\gretyyasd_asdrerr\\jjhjassddd.gpkg',
                    'type': 'PropertySet',
                    'version': 1
                },
                'path_name': '',
                'workspace_type': 'ESRI_LOCALDATABASE_WORKSPACE',
                'workspace_factory': {
                    'type': 'GpkgWorkspaceFactory',
                    'version': 1
                },
                'name_string': '',
                'type': 'WorkspaceName',
                'version': 1
            },
            'datasource_type': 'Query Feature Class', 'feature_type': 'FT_SIMPLE', 'shape_field_name': '',
            'shape_type': 'any', 'topologies': [],
            'query': {'query': 'select fid, geom from main.jjhjassddd', 'fid': 'fid',
                      'geometry_field': 'geom', 'esri_oid': 'ESRI_OID', 'fields': {'fields': [
                    {'name': 'fid', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 6,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 4, 'precision': 0,
                     'scale': 0, 'editable': False, 'is_nullable': False, 'required': True,
                     'domain_fixed': False, 'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'geom', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 7,
                     'value_domain': None,
                     'geometry_definition': {'average_number_of_points': 0, 'geometry_type': 'polygon',
                                             'crs': {
                                                 'wkt': 'PROJCS["WGS 84 / Pseudo-Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["degree",0.0174532925199433]],PROJECTION["Mercator_1SP"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",0.0],PARAMETER["scale_factor",1.0],UNIT["Metre",1.0]]',
                                                 'x_origin': -20037700.0, 'y_origin': -30198300.0,
                                                 'm_origin': -100000.0, 'z_origin': -100000.0,
                                                 'xy_scale': 10000.0, 'm_scale': 10000.0,
                                                 'z_scale': 10000.0,
                                                 'xy_tolerance': 0.001, 'z_tolerance': 0.001,
                                                 'm_tolerance': 0.001, 'is_high_precision': True,
                                                 'type': 'ProjectedCoordinateSystem', 'version': 6},
                                             'has_m': False, 'has_z': False, 'type': 'GeometryDef',
                                             'version': 1}, 'field_length': 4, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2}], 'type': 'Fields', 'version': 2},
                      'crs': {
                          'wkt': 'PROJCS["WGS 84 / Pseudo-Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["degree",0.0174532925199433]],PROJECTION["Mercator_1SP"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",0.0],PARAMETER["scale_factor",1.0],UNIT["Metre",1.0]]',
                          'x_origin': -20037700.0, 'y_origin': -30198300.0, 'm_origin': -100000.0,
                          'z_origin': -100000.0, 'xy_scale': 10000.0, 'm_scale': 10000.0,
                          'z_scale': 10000.0,
                          'xy_tolerance': 0.001, 'z_tolerance': 0.001, 'm_tolerance': 0.001,
                          'is_high_precision': True, 'type': 'ProjectedCoordinateSystem', 'version': 6},
                      'type': 'GpkgFeatureClassQuery', 'version': 3}, 'type': 'GpkgFeatureClassName',
            'version': 2}, 'base': '/home/me/test_slyr/Aaaaa Aaa/MXDs',
        'crs': 'EPSG:3857',
        'subset': '',
        'expected': {
            'uri': '/home/me/test_slyr/Aaaaa Aaa/MXDs/../gretyyasd_asdrerr/jjhjassddd.gpkg|layername=jjhjassddd',
            'provider': 'ogr',
            'wkb_type': 3,
            'file_name': '/home/me/test_slyr/Aaaaa Aaa/MXDs/../gretyyasd_asdrerr/jjhjassddd.gpkg',
            'factory': 'GpkgWorkspaceFactory'
        }
    },
    'sdc': {
        'object': {
            'name': 'continent',
            'dataset_name': {
                'category': '',
                'name': '',
                'subset_names': None,
                'dataset_type': 'DATASET_TYPE_CONTAINER',
                'workspace_name': {
                    'name': 'data\\continent',
                    'browse_name': 'continent',
                    'connection_properties': None,
                    'path_name': '',
                    'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                    'workspace_factory': {
                        'type': 'SdcWorkspaceFactory',
                        'version': 1
                    },
                    'name_string': '',
                    'type': 'WorkspaceName',
                    'version': 1
                },
                'type': 'FeatureDatasetName',
                'version': 1
            },
            'datasource_type': 'SDC Feature Class',
            'feature_type': 'FT_SIMPLE',
            'shape_field_name': 'Shape',
            'shape_type': 'polygon',
            'type': 'FeatureClassName',
            'version': 2
        },
        'base': '/home/me/test_slyr/Archive/LYRs',
        'crs': 'EPSG:4326',
        'subset': '',
        'skip_old': True,
        'expected': {
            'uri': '/home/me/test_slyr/Archive/LYRs/data/continent/continent',
            'provider': 'ogr',
            'wkb_type': 6,
            'file_name': '/home/me/test_slyr/Archive/LYRs/data/continent/continent',
            'factory': 'SdcWorkspaceFactory'
        }
    },
    'sde2': {'object': {'name': 'AA_SSSSSSSS.sCCCccccVaaaa_asd',
                        'dataset_name': {'category': '', 'name': '', 'subset_names': None,
                                         'dataset_type': 'DATASET_TYPE_CONTAINER', 'workspace_name': {
                                'name': 'C:\\Users\\RR112333\\AppData\\Roaming\\ESRI\\Desktop10.2\\ArcCatalog\\ASDD to ASDDD_ASDD.sde',
                                'browse_name': 'ArcSDE Data',
                                'connection_properties': {'SERVER': 'sde', 'INSTANCE': 'sde:oracle$sde:oracle11g:ssss',
                                                          'IS_GEODATABASE': 'true', 'AUTHENTICATION_MODE': 'DBMS',
                                                          'CONNPROP-REV': 'Rev1.0', 'type': 'PropertySet',
                                                          'version': 1}, 'path_name': '',
                                'workspace_type': 'ESRI_REMOTEDATABASE_WORKSPACE',
                                'workspace_factory': {'type': 'SdeWorkspaceFactory', 'version': 1}, 'name_string': '',
                                'type': 'WorkspaceName', 'version': 1}, 'type': 'FeatureDatasetName', 'version': 1},
                        'datasource_type': 'SDE Feature Class', 'feature_type': 'FT_SIMPLE',
                        'shape_field_name': 'SHAPE', 'shape_type': 'point', 'type': 'FeatureClassName', 'version': 2},
             'base': '/home/me/test_slyr/Archive/LYRs', 'crs': 'EPSG:28356',
             'subset': "STATUS <> 'ERR'", 'expected': {
            'uri': 'C:/Users/RR112333/AppData/Roaming/ESRI/Desktop10.2/ArcCatalog/ASDD to ASDDD_ASDD.sde|layername=AA_SSSSSSSS.sCCCccccVaaaa_asd',
            'provider': 'ogr', 'wkb_type': 1,
            'file_name': 'C:/Users/RR112333/AppData/Roaming/ESRI/Desktop10.2/ArcCatalog/ASDD to ASDDD_ASDD.sde',
            'factory': 'SdeWorkspaceFactory'
        }
             },
    'sql server': {'object': {'name': 'sde.START.AAA_Overlay_NNNnnnnnnRRRRrrrrrCCCccc',
                              'dataset_name': {'category': '', 'name': '', 'subset_names': None,
                                               'dataset_type': 'DATASET_TYPE_CONTAINER', 'workspace_name': {
                                      'name': 'C:\\Users\\dangermouse\\AppData\\Roaming\\ESRI\\Desktop10.5\\ArcCatalog\\Guest.sde',
                                      'browse_name': 'ArcSDE Data',
                                      'connection_properties': {'SERVER': 'sde', 'INSTANCE': 'sde:sqlserver:sde',
                                                                'DBCLIENT': 'sqlserver',
                                                                'DB_CONNECTION_PROPERTIES': 'sde',
                                                                'DATABASE': 'sde', 'IS_GEODATABASE': 'true',
                                                                'AUTHENTICATION_MODE': 'DBMS', 'USER': 'asdddd',
                                                                'PASSWORD': '********************************************************',
                                                                'CONNPROP-REV': 'Rev1.0', 'VERSION': 'sde.DEFAULT',
                                                                'type': 'PropertySet', 'version': 1}, 'path_name': '',
                                      'workspace_type': 'ESRI_REMOTEDATABASE_WORKSPACE',
                                      'workspace_factory': {'type': 'SdeWorkspaceFactory', 'version': 1},
                                      'name_string': '',
                                      'type': 'WorkspaceName', 'version': 1}, 'type': 'FeatureDatasetName',
                                               'version': 1},
                              'datasource_type': 'SDE Feature Class', 'feature_type': 'FT_SIMPLE',
                              'shape_field_name': 'Shape',
                              'shape_type': 'polygon', 'type': 'FeatureClassName', 'version': 2},
                   'base': '/home/me/test_slyr/Archive/LYRs', 'crs': 'EPSG:28356',
                   'subset': '"Changes_20111025" is null or "Changes_20111025" = \'Add\'', 'expected': {
            'uri': 'dbname=\'sde\' host=sde key=\'OBJECTID\' srid=28356 type=Polygon disableInvalidGeometryHandling=\'0\' table="START"."AAA_Overlay_NNNnnnnnnRRRRrrrrrCCCccc" (Shape) sql="Changes_20111025" is null or "Changes_20111025" = \'Add\'',
            'provider': 'mssql', 'wkb_type': 3,
            'factory': 'SdeWorkspaceFactory'}},
    'sdc with workspace': {'object': {'name': 'continent',
                                      'dataset_name': {'category': '', 'name': '', 'subset_names': None,
                                                       'dataset_type': 'DATASET_TYPE_CONTAINER',
                                                       'workspace_name': {'name': 'data\\continent',
                                                                          'browse_name': 'continent',
                                                                          'connection_properties': None,
                                                                          'path_name': '',
                                                                          'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                                                                          'workspace_factory': {
                                                                              'type': 'SdcWorkspaceFactory',
                                                                              'version': 1}, 'name_string': '',
                                                                          'type': 'WorkspaceName', 'version': 1},
                                                       'type': 'FeatureDatasetName', 'version': 1},
                                      'datasource_type': 'SDC Feature Class', 'feature_type': 'FT_SIMPLE',
                                      'shape_field_name': 'Shape', 'shape_type': 'polygon', 'type': 'FeatureClassName',
                                      'version': 2}, 'base': '/home/me/test_slyr/Archive/LYRs',
                           'crs': 'EPSG:4326', 'subset': '', 'expected': {
            'uri': '/home/me/test_slyr/Archive/LYRs/data/continent/continent', 'provider': 'ogr',
            'wkb_type': 6, 'file_name': '/home/me/test_slyr/Archive/LYRs/data/continent/continent',
            'factory': 'SdcWorkspaceFactory'}},
    'sde oracle': {
        'object': {
            'name': 'SD_MMMMMM.SSSS_AAAA_BBBB',
            'dataset_name': {
                'name': 'C:\\Users\\RR112333\\AppData\\Roaming\\ESRI\\Desktop10.2\\ArcCatalog\\ASDD to ASDDD_ASDD.sde',
                'browse_name': 'ArcSDE Data',
                'connection_properties': {
                    'SERVER': 'sde', 'INSTANCE': 'sde:oracle$sde:oracle11g:ssss',
                    'IS_GEODATABASE': 'true', 'AUTHENTICATION_MODE': 'DBMS',
                    'CONNPROP-REV': 'Rev1.0',
                    'type': 'PropertySet', 'version': 1}, 'path_name': '',
                'workspace_type': 'ESRI_REMOTEDATABASE_WORKSPACE',
                'workspace_factory': {'type': 'SdeWorkspaceFactory', 'version': 1}, 'name_string': '',
                'type': 'WorkspaceName',
                'version': 1
            },
            'datasource_type': 'SDE Feature Class',
            'feature_type': 'FT_SIMPLE',
            'shape_field_name': 'SHAPE',
            'shape_type': 'polyline',
            'type': 'FeatureClassName',
            'version': 2
        },
        'base': '/home/me/test_slyr/Archive/LYRs',
        'crs': 'EPSG:28356',
        'subset': '',
        'expected': {
            'uri': 'C:/Users/RR112333/AppData/Roaming/ESRI/Desktop10.2/ArcCatalog/ASDD to ASDDD_ASDD.sde|layername=SD_MMMMMM.SSSS_AAAA_BBBB',
            'provider': 'ogr',
            'wkb_type': 5,
            'file_name': 'C:/Users/RR112333/AppData/Roaming/ESRI/Desktop10.2/ArcCatalog/ASDD to ASDDD_ASDD.sde',
            'factory': 'SdeWorkspaceFactory'
        }
    },
    'sde no dbclient': {'object': {'name': 'SD_MMMMMM.SSSS_AAAA_BBBB', 'dataset_name': {
        'name': 'C:\\Users\\RR112333\\AppData\\Roaming\\ESRI\\Desktop10.2\\ArcCatalog\\ASDD to ASDDD_ASDD.sde',
        'browse_name': 'ArcSDE Data',
        'connection_properties': {'SERVER': 'sde', 'INSTANCE': 'sde:oracle$sde:oracle11g:ssss',
                                  'IS_GEODATABASE': 'true', 'AUTHENTICATION_MODE': 'DBMS', 'CONNPROP-REV': 'Rev1.0',
                                  'type': 'PropertySet', 'version': 1}, 'path_name': '',
        'workspace_type': 'ESRI_REMOTEDATABASE_WORKSPACE',
        'workspace_factory': {'type': 'SdeWorkspaceFactory', 'version': 1}, 'name_string': '', 'type': 'WorkspaceName',
        'version': 1}, 'datasource_type': 'SDE Feature Class', 'feature_type': 'FT_SIMPLE', 'shape_field_name': 'SHAPE',
                                   'shape_type': 'polyline', 'type': 'FeatureClassName', 'version': 2},
                        'base': '/home/me/test_slyr/Archive/LYRs', 'crs': 'EPSG:28356', 'subset': '',
                        'expected': {
                            'uri': 'C:/Users/RR112333/AppData/Roaming/ESRI/Desktop10.2/ArcCatalog/ASDD to ASDDD_ASDD.sde|layername=SD_MMMMMM.SSSS_AAAA_BBBB',
                            'provider': 'ogr', 'wkb_type': 5,
                            'file_name': 'C:/Users/RR112333/AppData/Roaming/ESRI/Desktop10.2/ArcCatalog/ASDD to ASDDD_ASDD.sde',
                            'factory': 'SdeWorkspaceFactory'}},
    'sdc no connection': {
        'object': {'name': 'ccccmmmm', 'dataset_name': {'category': '', 'name': '', 'subset_names': None,
                                                        'dataset_type': 'DATASET_TYPE_CONTAINER',
                                                        'workspace_name': {'name': 'Data', 'browse_name': 'Data',
                                                                           'connection_properties': None,
                                                                           'path_name': '',
                                                                           'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                                                                           'workspace_factory': {
                                                                               'type': 'SdcWorkspaceFactory',
                                                                               'version': 1}, 'name_string': '',
                                                                           'type': 'WorkspaceName', 'version': 1},
                                                        'type': 'FeatureDatasetName', 'version': 1},
                   'datasource_type': 'SDC Feature Class', 'feature_type': 'FT_SIMPLE', 'shape_field_name': 'Shape',
                   'shape_type': 'point', 'type': 'FeatureClassName', 'version': 2},
        'base': '/home/me/test_slyr/Archive/LYRs', 'crs': 'EPSG:4326',
        'subset': '"CAPTYPE" = \'1\'',
        'expected': {'uri': '/home/me/test_slyr/Archive/LYRs/Data/ccccmmmm', 'provider': 'ogr',
                     'wkb_type': 1,
                     'file_name': '/home/me/test_slyr/Archive/LYRs/Data/ccccmmmm',
                     'factory': 'SdcWorkspaceFactory'
                     }
    },
    'Shapefile table': {
        'object': {
            'name': 'pop_areas_codes',
            'category': '',
            'datasource_type': 'Shapefile Table',
            'workspace_name': {
                'name': 'D:\\SPS_AAAA\\JIIIIIIIIII',
                'browse_name': 'Shapefile Data',
                'connection_properties': {
                    'DATABASE': 'd:\\SPS_AAAA\\JIIIIIIIIII',
                    'type': 'PropertySet',
                    'version': 1
                },
                'path_name': '',
                'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                'workspace_factory': {
                    'type': 'ShapefileWorkspaceFactory',
                    'version': 1
                },
                'name_string': '',
                'type': 'WorkspaceName',
                'version': 1
            },
            'type': 'TableName',
            'version': 1
        },
        'base': '/home/me/test_slyr/Archive/MXDs',
        'crs': '',
        'subset': '',
        'skip_old': True,
        'expected': {
            'uri': 'D:/SPS_AAAA/JIIIIIIIIII/pop_areas_codes.dbf',
            'provider': 'ogr',
            'wkb_type': 100,
            'file_name': 'D:/SPS_AAAA/JIIIIIIIIII/pop_areas_codes.dbf',
            'factory': 'ShapefileWorkspaceFactory'
        }
    },
    'TEXT Table': {
        'object': {
            'name': 'aaaaaaa bbbb_ (TRACK).txt',
            'category': '',
            'datasource_type': 'TEXT Table',
            'workspace_name': {
                'name': 'D:\\srrreaaaaaa\\MAP\\Kaaaa Bbbbb.co\\IuuugfL\\P.Lllllll',
                'browse_name': 'Text File Data',
                'connection_properties': None,
                'path_name': '',
                'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                'workspace_factory': {
                    'type': 'TextFileWorkspaceFactory',
                    'version': 1
                },
                'name_string': '',
                'type': 'WorkspaceName',
                'version': 1
            },
            'type': 'TableName',
            'version': 1
        },
        'base': '/home/me/test_slyr/Archive/MXDs',
        'crs': '',
        'subset': '',
        'skip_old': True,
        'expected': {
            'uri': 'D:/srrreaaaaaa/MAP/Kaaaa Bbbbb.co/IuuugfL/P.Lllllll/aaaaaaa bbbb_ (TRACK).txt',
            'provider': 'ogr',
            'wkb_type': 100,
            'file_name': 'D:/srrreaaaaaa/MAP/Kaaaa Bbbbb.co/IuuugfL/P.Lllllll/aaaaaaa bbbb_ (TRACK).txt',
            'factory': 'TextFileWorkspaceFactory'
        }
    },
    'sde dataset connection no dbclient subset': {'object': {'name': 'eeeaaaaw.DBO.TTTTTT_AAAAAA_line',
                                                             'dataset_name': {
                                                                 'name': 'N:\\SPS_AAAA\\SDE_Connects\\Direct Connections\\JJJJJ (ggggggg).sde',
                                                                 'browse_name': 'ArcSDE Data',
                                                                 'connection_properties': {'SERVER': 'spatialdata',
                                                                                           'INSTANCE': 'sde:sqlserver:spatialdata',
                                                                                           'DATABASE': 'eeeaaaaw',
                                                                                           'AUTHENTICATION_MODE': 'OSA',
                                                                                           'VERSION': 'dbo.DEFAULT',
                                                                                           'type': 'PropertySet',
                                                                                           'version': 1},
                                                                 'path_name': '',
                                                                 'workspace_type': 'ESRI_REMOTEDATABASE_WORKSPACE',
                                                                 'workspace_factory': {'type': 'SdeWorkspaceFactory',
                                                                                       'version': 1},
                                                                 'name_string': '', 'type': 'WorkspaceName',
                                                                 'version': 1},
                                                             'datasource_type': 'SDE Feature Class',
                                                             'feature_type': 'FT_SIMPLE', 'shape_field_name': 'SHAPE',
                                                             'shape_type': 'polyline', 'type': 'FeatureClassName',
                                                             'version': 2},
                                                  'base': '/home/me/test_slyr/Bbbbbbbb Aaaa/LYRs',
                                                  'crs': 'EPSG:26910',
                                                  'subset': "( Drivable LIKE '%Yes%' AND ( left(CLASS_RNP, 1) = 5 OR left(CLASS_RNP, 1) = 6  OR left(CLASS_RNP, 1) = 8  OR left(CLASS_RNP, 1) = 9 )  AND CLASS_RNP LIKE '%TRAIL_%' ) AND MapDisplay >= 36",
                                                  'expected': {
                                                      'uri': 'N:/SPS_AAAA/SDE_Connects/Direct Connections/JJJJJ (ggggggg).sde|layername=eeeaaaaw.DBO.TTTTTT_AAAAAA_line',
                                                      'provider': 'ogr',
                                                      'wkb_type': 5,
                                                      'file_name': 'N:/SPS_AAAA/SDE_Connects/Direct Connections/JJJJJ (ggggggg).sde',
                                                      'factory': 'SdeWorkspaceFactory'
                                                  }
                                                  },
    'sde sql server': {'object': {'name': 'iiiiiiddddddd.IIIIIIIIAAAAAA.KK_aaaa_CCCC_dissolve', 'dataset_name': {
        'name': 'C:\\Users\\pccccc\\AppData\\Roaming\\ESRI\\Desktop10.1\\ArcCatalog\\CAA_EEEE.sde',
        'browse_name': 'ArcSDE Data',
        'connection_properties': {'SERVER': 'keeeeaa3aa33', 'INSTANCE': 'sde:sqlserver:keeeeaa3aa33\\sdesqlco',
                                  'DBCLIENT': 'sqlserver', 'DB_CONNECTION_PROPERTIES': 'keeeeaa3aa33\\sdesqlco',
                                  'DATABASE': 'iiiiiiddddddd', 'IS_GEODATABASE': 'true', 'AUTHENTICATION_MODE': 'OSA',
                                  'CONNPROP-REV': 'Rev1.0', 'VERSION': 'sde.DEFAULT', 'type': 'PropertySet',
                                  'version': 1}, 'path_name': '', 'workspace_type': 'ESRI_REMOTEDATABASE_WORKSPACE',
        'workspace_factory': {'type': 'SdeWorkspaceFactory', 'version': 1}, 'name_string': '', 'type': 'WorkspaceName',
        'version': 1}, 'datasource_type': 'SDE Feature Class', 'feature_type': 'FT_SIMPLE', 'shape_field_name': 'SHAPE',
                                  'shape_type': 'polygon', 'type': 'FeatureClassName', 'version': 2},
                       'base': '/home/me/test_slyr/Bbbbbbbb Aaaa/LYRs', 'crs': 'EPSG:26913',
                       'subset': '',
                       'expected': {
                           'uri': 'dbname=\'iiiiiiddddddd\' host=keeeeaa3aa33 key=\'OBJECTID\' srid=26913 type=Polygon disableInvalidGeometryHandling=\'0\' table="IIIIIIIIAAAAAA"."KK_aaaa_CCCC_dissolve" (SHAPE)',
                           'provider': 'mssql',
                           'wkb_type': 3,
                           'factory': 'SdeWorkspaceFactory'
                       }
                       },
    'coverage region nested dataset name': {
        'object': {
            'name': 'region.aaa',
            'dataset_name': {
                'name': 'krrraaa',
                'dataset_name': {
                    'name': '..\\spatial_data\\month_jun_01\\month_jun_01',
                    'browse_name': 'ARC/INFO Data',
                    'connection_properties': None,
                    'path_name': '',
                    'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                    'workspace_factory': {
                        'type': 'ArcInfoWorkspaceFactory',
                        'version': 1
                    },
                    'name_string': 'ARCINFO: Workspace = \\\\CCCCCC\\D$\\spatial_data\\month_jun_01\\month_jun_01;',
                    'type': 'WorkspaceName',
                    'version': 1
                },
                'type': 'CoverageName',
                'version': 1
            },
            'datasource_type': 'Region Feature Class',
            'feature_type': 'FT_SIMPLE',
            'shape_field_name': 'Shape',
            'shape_type': 'polygon',
            'class_type': 'CFCT_REGION',
            'topology': 'FCT_EXISTS',
            'dataset_name_string': 'ARCINFO: Workspace = \\\\CCCCCC\\D$\\spatial_data\\month_jun_01\\month_jun_01\\; Coverage = krrraaa; FeatureClass = region.rch;',
            'type': 'CoverageFeatureClassName',
            'version': 1
        },
        'base': '/home/me/test_slyr/Bbbbbbbb Aaaa/MXDs',
        'crs': 'EPSG:4269',
        'subset': '',
        'skip_old': True,
        'expected': {
            'uri': '/home/me/test_slyr/Bbbbbbbb Aaaa/MXDs/../spatial_data/month_jun_01/month_jun_01/krrraaa|layername=aaa',
            'provider': 'ogr', 'wkb_type': 6,
            'file_name': '/home/me/test_slyr/Bbbbbbbb Aaaa/MXDs/../spatial_data/month_jun_01/month_jun_01/krrraaa',
            'factory': 'ArcInfoWorkspaceFactory'
        }
    },
    'Info table': {
        'object': {
            'name': 'bbbbb_aaaa_final',
            'category': 'ARCINFO: Workspace = \\\\CCCCCC\\D$\\reeeeeee\\samples; InfoTable = bbbbb_aaaa_final;',
            'datasource_type': 'Info Table',
            'workspace_name': {
                'name': '..\\reeeeeee\\samples',
                'browse_name': 'ARC/INFO Data',
                'connection_properties': None,
                'path_name': '',
                'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                'workspace_factory': {
                    'type': 'ArcInfoWorkspaceFactory',
                    'version': 1
                },
                'name_string': 'ARCINFO: Workspace = \\\\CCCCCC\\D$\\reeeeeee\\samples;',
                'type': 'WorkspaceName',
                'version': 1
            },
            'type': 'TableName',
            'version': 1
        },
        'base': '/home/me/test_slyr/Bbbbbbbb Aaaa/MXDs',
        'crs': '',
        'subset': '',
        'skip_old': True,
        'expected': {
            'uri': '/home/me/test_slyr/Bbbbbbbb Aaaa/MXDs/../reeeeeee/samples|layername=bbbbb_aaaa_final',
            'provider': 'ogr',
            'wkb_type': 100,
            'file_name': '/home/me/test_slyr/Bbbbbbbb Aaaa/MXDs/../reeeeeee/samples',
            'factory': 'ArcInfoWorkspaceFactory'
        }
    },
    'info table 2': {'object': {'name': 'ttttttsum',
                                'category': 'ARCINFO: Workspace = \\\\CCCCCC\\D$\\ww_ppppppp_sssss\\rasters; InfoTable = ttttttsum;',
                                'datasource_type': 'Info Table',
                                'workspace_name': {'name': '..\\ww_ppppppp_sssss\\rasters',
                                                   'browse_name': 'ARC/INFO Data',
                                                   'connection_properties': None, 'path_name': '',
                                                   'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                                                   'workspace_factory': {'type': 'ArcInfoWorkspaceFactory',
                                                                         'version': 1},
                                                   'name_string': 'ARCINFO: Workspace = \\\\CCCCCC\\D$\\ww_ppppppp_sssss\\rasters;',
                                                   'type': 'WorkspaceName', 'version': 1}, 'type': 'TableName',
                                'version': 1},
                     'base': '/home/me/test_slyr/Bbbbbbbb Aaaa/MXDs', 'crs': '', 'subset': '',
                     'expected': {
                         'uri': '/home/me/test_slyr/Bbbbbbbb Aaaa/MXDs/../ww_ppppppp_sssss/rasters|layername=ttttttsum',
                         'provider': 'ogr', 'wkb_type': 100,
                         'file_name': '/home/me/test_slyr/Bbbbbbbb Aaaa/MXDs/../ww_ppppppp_sssss/rasters',
                         'factory': 'ArcInfoWorkspaceFactory'
                     }
                     },
    'Table with ArcInfoWorkspaceFactory': {'object': {'name': 'rrrrr_aaaaaa',
                                                      'category': 'ARCINFO: Workspace = \\\\SSSAAASSSS\\c\\outgoing\\dnr\\ssssaaaa_dir\\outoing_output; InfoTable = rrrrr_aaaaaa;',
                                                      'datasource_type': 'Info Table',
                                                      'workspace_name': {
                                                          'name': 'c:\\outgoing\\dnr\\ssssaaaa_dir\\outoing_output',
                                                          'browse_name': 'ARC/INFO Data', 'connection_properties': {
                                                              'DATABASE': 'C:\\outgoing\\DNR\\ssssaaaa_dir\\outoing_output',
                                                              'type': 'PropertySet', 'version': 1}, 'path_name': '',
                                                          'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                                                          'workspace_factory': {'type': 'ArcInfoWorkspaceFactory',
                                                                                'version': 1},
                                                          'name_string': 'ARCINFO: Workspace = \\\\SSSAAASSSS\\c\\outgoing\\dnr\\ssssaaaa_dir\\outoing_output;',
                                                          'type': 'WorkspaceName', 'version': 1}, 'type': 'TableName',
                                                      'version': 1},
                                           'base': '/home/me/test_slyr/Bbbbbbbb Aaaa/MXDs', 'crs': '',
                                           'subset': '',
                                           'expected': {
                                               'uri': 'c:/outgoing/dnr/ssssaaaa_dir/outoing_output|layername=rrrrr_aaaaaa',
                                               'provider': 'ogr', 'wkb_type': 100,
                                               'file_name': 'c:/outgoing/dnr/ssssaaaa_dir/outoing_output',
                                               'factory': 'ArcInfoWorkspaceFactory'}},
    'RelQueryTableName': {
        'object': {
            'name': 'sssss_aaaaaa_Ccccccc_Aaaaa',
            'workspace_name': {
                'name': 'JoinUIRelationship',
                'destination_name': {
                    'name': 'Ccccccc_Aaaaa',
                    'category': '',
                    'datasource_type': 'dBASE Table',
                    'workspace_name': {
                        'name': 'C:\\GIS\\analysis',
                        'browse_name': 'Shapefile Data',
                        'connection_properties': {
                            'DATABASE': 'C:\\GIS\\analysis',
                            'type': 'PropertySet',
                            'version': 1
                        },
                        'path_name': '',
                        'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                        'workspace_factory': {
                            'type': 'ShapefileWorkspaceFactory',
                            'version': 1
                        },
                        'name_string': '',
                        'type': 'WorkspaceName',
                        'version': 1
                    },
                    'type': 'TableName',
                    'version': 1
                },
                'origin_name': {
                    'name': 'sssss_aaaaaa',
                    'dataset_name': {
                        'name': 'C:\\GIS\\spatial_data\\Asda_mxds_etc\\Kjjjjj_asdasd_eeee\\NM',
                        'browse_name': 'Shapefile Data',
                        'connection_properties': {
                            'DATABASE': 'C:\\GIS\\spatial_data\\Asda_mxds_etc\\Kjjjjj_asdasd_eeee\\NM',
                            'type': 'PropertySet',
                            'version': 1
                        },
                        'path_name': '',
                        'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                        'workspace_factory': {
                            'type': 'ShapefileWorkspaceFactory',
                            'version': 1
                        },
                        'name_string': '',
                        'type': 'WorkspaceName',
                        'version': 1
                    },
                    'datasource_type': 'Shapefile Feature Class',
                    'feature_type': 'FT_SIMPLE',
                    'shape_field_name': 'Shape',
                    'shape_type': 'polygon',
                    'type': 'FeatureClassName',
                    'version': 2
                },
                'origin_primary_key': 'S_T_R',
                'origin_foreign_key': 'S_T_R',
                'forward_path_label': 'Forwards',
                'backward_path_label': 'Backwards',
                'type': 'MemoryRelationshipClassName',
                'version': 1
            },
            'filter': {'sub_fields': '*', 'where_clause': '', 'output_spatial_reference_field_name': '',
                       'output_spatial_reference': None, 'spatial_resolution': 0.0, 'postfix_clause': '',
                       'prefix_clause': '', 'filter_defs': {'type': 'ArrayOfFilterDef', 'version': 1},
                       'row_offset': None, 'row_count': None, 'spatial_relation': 0,
                       'spatial_relation_description': '', 'reference_geometry': None,
                       'geometry_field_name': 'Shape', 'fid_set': None, 'type': 'SpatialFilter', 'version': 1},
            'type': 'RelQueryTableName', 'version': 3},
        'base': '/home/me/test_slyr/Bbbbbbbb Aaaa/MXDs', 'crs': '', 'subset': '',
        'expected': {
            'provider': 'ogr',
            'uri': 'temp',
            'wkb_type': 0,
            'factory': 'ArcInfoWorkspaceFactory'
        }
    },
    'sde workspace oracle': {
        'object': {
            'name': 'TTTTA_PPPPP_RRRR.aAAAAAAsssspppttTTT',
            'dataset_name': {
                'category': '',
                'name': '',
                'subset_names': None,
                'dataset_type': 'DATASET_TYPE_CONTAINER',
                'workspace_name': {
                    'name': 'T:\\FS\\AdasdASd\\FaasdTTTT\\rr01_aaaa\\DatabaseConnection\\gaaa09b_rr01_aaaa_default_as_myself.sde',
                    'browse_name': 'ArcSDE Data',
                    'connection_properties': {
                        'SERVER': 'gaaa09b',
                        'INSTANCE': 'sde:oracle11g:gaaa09b:TTTTA_PPPPP_RRRR',
                        'DBCLIENT': 'oracle',
                        'DB_CONNECTION_PROPERTIES': 'gaaa09b',
                        'PROJECT_INSTANCE': 'TTTTA_PPPPP_RRRR',
                        'IS_GEODATABASE': 'true',
                        'AUTHENTICATION_MODE': 'DBMS',
                        'USER': '/',
                        'PASSWORD': '********************************************************',
                        'CONNPROP-REV': 'Rev1.0',
                        'VERSION': 'TTTTA_PPPPP_RRRR.DEFAULT',
                        'type': 'PropertySet',
                        'version': 1
                    },
                    'path_name': '',
                    'workspace_type': 'ESRI_REMOTEDATABASE_WORKSPACE',
                    'workspace_factory': {
                        'type': 'SdeWorkspaceFactory',
                        'version': 1
                    },
                    'name_string': '',
                    'type': 'WorkspaceName',
                    'version': 1
                },
                'type': 'FeatureDatasetName',
                'version': 1
            },
            'datasource_type': 'SDE Feature Class',
            'feature_type': 'FT_SIMPLE',
            'shape_field_name': 'SHAPE',
            'shape_type': 'polygon',
            'type': 'FeatureClassName',
            'version': 2
        },
        'base': '/home/me/test_slyr/Bbbbbbbb Aaaa/MXDs',
        'crs': 'EPSG:26911',
        'subset': '',
        'skip_old': True,
        'expected': {
            'uri': "dbname='TTTTA_PPPPP_RRRR' port=1521 key='OBJECTID' estimatedmetadata=true srid=26911 type=Polygon table=\"TTTTA_PPPPP_RRRR\".\"aAAAAAAsssspppttTTT\" (SHAPE)",
            'provider': 'oracle',
            'wkb_type': 3,
            'factory': 'SdeWorkspaceFactory'
        }
    },
    'sde oracle workspace with subset': {'object': {'name': 'S_TTT.aAAAAAAsssspppttTTT',
                                                    'dataset_name': {'category': '', 'name': '', 'subset_names': None,
                                                                     'dataset_type': 'DATASET_TYPE_CONTAINER',
                                                                     'workspace_name': {'name': '',
                                                                                        'browse_name': 'ArcSDE Data',
                                                                                        'connection_properties': {
                                                                                            'SERVER': 'dasdd.ghg.err.aa',
                                                                                            'INSTANCE': 'sde:oracle11g:dasdd.ghg.err.aa',
                                                                                            'DBCLIENT': 'oracle',
                                                                                            'DB_CONNECTION_PROPERTIES': 'dasdd.ghg.err.aa',
                                                                                            'PROJECT_INSTANCE': 'sde',
                                                                                            'IS_GEODATABASE': 'true',
                                                                                            'AUTHENTICATION_MODE': 'DBMS',
                                                                                            'USER': '/',
                                                                                            'PASSWORD': '********************************************************',
                                                                                            'CONNPROP-REV': 'Rev1.0',
                                                                                            'VERSION': 'SDE.DEFAULT',
                                                                                            'type': 'PropertySet',
                                                                                            'version': 1},
                                                                                        'path_name': '',
                                                                                        'workspace_type': 'ESRI_REMOTEDATABASE_WORKSPACE',
                                                                                        'workspace_factory': {
                                                                                            'type': 'SdeWorkspaceFactory',
                                                                                            'version': 1},
                                                                                        'name_string': '',
                                                                                        'type': 'WorkspaceName',
                                                                                        'version': 1},
                                                                     'type': 'FeatureDatasetName', 'version': 1},
                                                    'datasource_type': 'SDE Feature Class', 'feature_type': 'FT_SIMPLE',
                                                    'shape_field_name': 'SHAPE',
                                                    'shape_type': 'polygon', 'type': 'FeatureClassName', 'version': 2},
                                         'base': '/home/me/test_slyr/Bbbbbbbb Aaaa/MXDs',
                                         'crs': 'EPSG:4269',
                                         'subset': "FORESTNAME = 'Gifford Pinchot National Forest'", 'expected': {
            'uri': '/home/me/test_slyr/Bbbbbbbb Aaaa/MXDs/|layername=S_TTT.aAAAAAAsssspppttTTT',
            'provider': 'ogr', 'wkb_type': 6, 'file_name': '/home/me/test_slyr/Bbbbbbbb Aaaa/MXDs/',
            'factory': 'SdeWorkspaceFactory'
        }
                                         },
    'dBASE-Tabelle': {
        'object': {
            'name': 'Rrrrrr_Aaa',
            'category': '',
            'datasource_type': 'dBASE-Tabelle',
            'workspace_name': {
                'name': 'G:\\Bbaaaa\\Pppaaaa\\LLL_AAAAAaaaa\\Project 14-01_Vvaavav_ssaaa_ammmm_aaaaa\\Daaadaddda_aaa\\Lgennn',
                'browse_name': 'Shapefile Data',
                'connection_properties': {
                    'DATABASE': 'G:\\Bbaaaa\\Pppaaaa\\LLL_AAAAAaaaa\\Project 14-01_Vvaavav_ssaaa_ammmm_aaaaa\\Daaadaddda_aaa\\Lgennn',
                    'type': 'PropertySet',
                    'version': 1
                },
                'path_name': '',
                'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                'workspace_factory': {
                    'type': 'ShapefileWorkspaceFactory',
                    'version': 1
                },
                'name_string': '',
                'type': 'WorkspaceName',
                'version': 1
            },
            'type': 'TableName',
            'version': 1
        },
        'base': '/home/me/test_slyr/AAe',
        'crs': '',
        'subset': '',
        'skip_old': True,
        'expected': {
            'uri': 'G:/Bbaaaa/Pppaaaa/LLL_AAAAAaaaa/Project 14-01_Vvaavav_ssaaa_ammmm_aaaaa/Daaadaddda_aaa/Lgennn/Rrrrrr_Aaa.dbf',
            'provider': 'ogr',
            'wkb_type': 100,
            'file_name': 'G:/Bbaaaa/Pppaaaa/LLL_AAAAAaaaa/Project 14-01_Vvaavav_ssaaa_ammmm_aaaaa/Daaadaddda_aaa/Lgennn/Rrrrrr_Aaa.dbf',
            'factory': 'ShapefileWorkspaceFactory'
        }
    },
    'Excel-Tabelle': {
        'object': {
            'name': 'gaaaa233_TtTrrAasddd',
            'category': '',
            'datasource_type': 'Excel-Tabelle',
            'workspace_name': {
                'name': '.\\gaaaa233_TtTrrAasddd.xlsx',
                'browse_name': 'gaaaa233_TtTrrAasddd',
                'connection_properties': None,
                'path_name': '',
                'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                'workspace_factory': {
                    'type': 'ExcelOrMdbWorkspaceFactory',
                    'version': 1
                },
                'name_string': '',
                'type': 'WorkspaceName',
                'version': 1
            },
            'type': 'TableName',
            'version': 1
        },
        'base': '/home/me/test_slyr/Gad Rererr asd Rwewaaa qww Arreee Qqqqq',
        'crs': '',
        'subset': '', 'expected': {
            'uri': '/home/me/test_slyr/Gad Rererr asd Rwewaaa qww Arreee Qqqqq/gaaaa233_TtTrrAasddd.xlsx|layername=gaaaa233_TtTrrAasddd',
            'provider': 'ogr',
            'wkb_type': 100,
            'file_name': '/home/me/test_slyr/Gad Rererr asd Rwewaaa qww Arreee Qqqqq/gaaaa233_TtTrrAasddd.xlsx',
            'factory': 'ExcelOrMdbWorkspaceFactory'
        }
    },
    'Tableau Excel': {
        'object': {
            'name': 'ARRR$',
            'category': '',
            'datasource_type': 'Tableau Excel',
            'workspace_name': {
                'name': 'M:\\332 - Poor asdd aasss\\AAAA_BBBB\\Inaasaddd\\Aaa-bbbbbb.xls',
                'browse_name': 'Aaa-bbbbbb',
                'connection_properties': {
                    'DATABASE': 'M:\\332 - Poor asdd aasss\\AAAA_BBBB\\Inaasaddd\\Aaa-bbbbbb.xls',
                    'CONNECTSTRING': 'Provider=Microsoft.Jet.OLEDB.4.0;Data Source=M:\\332 - Poor asdd aasss\\AAAA_BBBB\\Inaasaddd\\Aaa-bbbbbb.xls;Extended Properties="Excel 8.0;HDR=Yes;IMEX=1;"',
                    'type': 'PropertySet',
                    'version': 1
                },
                'path_name': '',
                'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                'workspace_factory': {
                    'type': 'ExcelOrMdbWorkspaceFactory',
                    'version': 1
                },
                'name_string': '',
                'type': 'WorkspaceName',
                'version': 1
            },
            'type': 'TableName',
            'version': 1
        },
        'base': '/home/me/test_slyr/ARTTER',
        'crs': '',
        'subset': '',
        'expected': {
            'uri': 'M:/332 - Poor asdd aasss/AAAA_BBBB/Inaasaddd/Aaa-bbbbbb.xls|layername=ARRR',
            'provider': 'ogr', 'wkb_type': 100,
            'file_name': 'M:/332 - Poor asdd aasss/AAAA_BBBB/Inaasaddd/Aaa-bbbbbb.xls',
            'factory': 'ExcelOrMdbWorkspaceFactory'
        }
    },
    'DBTableName': {
        'object': {
            'name': 'main.layer_styles',
            'dataset_name': {
                'name': '.\\fr099_asddddaa_bbbbbfdd_asdddvccc.gpkg',
                'browse_name': 'fr099_asddddaa_bbbbbfdd_asdddvccc',
                'connection_properties': None,
                'path_name': '',
                'workspace_type': 'ESRI_LOCALDATABASE_WORKSPACE',
                'workspace_factory': {
                    'type': 'GpkgWorkspaceFactory',
                    'version': 1
                },
                'name_string': '',
                'type': 'WorkspaceName',
                'version': 1
            },
            'datasource_type': 'Table',
            'type': 'DBTableName',
            'version': 1
        },
        'base': '/home/me/test_slyr/AaaBbbbbbbb',
        'crs': '',
        'subset': '',
        'skip_old': True,
        'expected': {
            'file_name': '/home/me/test_slyr/AaaBbbbbbbb/fr099_asddddaa_bbbbbfdd_asdddvccc.gpkg',
            'uri': '/home/me/test_slyr/AaaBbbbbbbb/fr099_asddddaa_bbbbbfdd_asdddvccc.gpkg|layername=layer_styles',
            'provider': 'ogr',
            'wkb_type': 100,
            'factory': 'GpkgWorkspaceFactory'
        }
    },
    'Access workspace factory': {
        'object': {
            'name': 'raaaaaa',
            'dataset_name': {
                'category': '',
                'name': '',
                'subset_names': None,
                'dataset_type': 'DATASET_TYPE_CONTAINER',
                'workspace_name': {
                    'name': 'D:\\Faaa_Rrrr\\Aaaa_bbb_444 000\\BBB.mdb',
                    'browse_name': 'BBB',
                    'connection_properties': {
                        'DATABASE': 'D:\\Faaa_Rrrr\\Aaaa_bbb_444 000\\BBB.mdb',
                        'type': 'PropertySet',
                        'version': 1}, 'path_name': '',
                    'workspace_type': 'ESRI_LOCALDATABASE_WORKSPACE',
                    'workspace_factory': {
                        'type': 'AccessWorkspaceFactory',
                        'version': 1
                    },
                    'name_string': '',
                    'type': 'WorkspaceName',
                    'version': 1
                },
                'type': 'FeatureDatasetName',
                'version': 1
            },
            'datasource_type': 'Персональная база геоданных Класс пространственных объектов',
            'feature_type': 'FT_SIMPLE',
            'shape_field_name': 'Shape',
            'shape_type': 'polyline',
            'type': 'FeatureClassName',
            'version': 2
        },
        'base': '/home/me/test_slyr/Adddsaaa',
        'crs': 'EPSG:28471',
        'subset': '',
        'expected': {
            'uri': 'D:/Faaa_Rrrr/Aaaa_bbb_444 000/BBB.mdb|layername=raaaaaa',
            'provider': 'ogr',
            'wkb_type': 5,
            'file_name': 'D:/Faaa_Rrrr/Aaaa_bbb_444 000/BBB.mdb',
            'factory': 'AccessWorkspaceFactory'
        }
    },
    'sde oracle no workspace with subset': {
        'object': {
            'name': 'ASASD_BBBAAAAAA.CCA_RDDD_9G_GGGGG_AAAA_BBBBB',
            'dataset_name': {
                'name': '//aaaa.bbbbbb/aaaabbbbb_cccccc/bbbb.aaaaaa.sde',
                'browse_name': 'ArcSDE Data',
                'connection_properties': {'SERVER': 'bbbb.aaaaaa',
                                          'INSTANCE': 'sde:oracle$bbbb.aaaaaa/aavbvvv_tttrrr1.bcgov',
                                          'DBCLIENT': 'oracle',
                                          'DB_CONNECTION_PROPERTIES': 'bbbb.aaaaaa/aavbvvv_tttrrr1.bcgov',
                                          'IS_GEODATABASE': 'true',
                                          'AUTHENTICATION_MODE': 'DBMS',
                                          'CONNPROP-REV': 'Rev2.0',
                                          'type': 'PropertySet',
                                          'version': 1},
                'path_name': '',
                'workspace_type': 'ESRI_REMOTEDATABASE_WORKSPACE',
                'workspace_factory': {'type': 'SdeWorkspaceFactory',
                                      'version': 1},
                'name_string': '', 'type': 'WorkspaceName', 'version': 1},
            'datasource_type': 'SDE Feature Class',
            'feature_type': 'FT_SIMPLE', 'shape_field_name': 'GEOMETRY',
            'shape_type': 'point', 'type': 'FeatureClassName', 'version': 2},
        'base': '/home/me/test_slyr/Aaaaaaa bb CCCcccc',
        'crs': 'EPSG:3005',
        'subset': "NAME IN ( 'Victoria', 'Vancouver', 'Nanaimo', 'Campbell River', 'Kamloops', 'Kelowna', 'Prince Rupert', 'Prince George', 'Smithers', 'Atlin', 'Fort Nelson', 'Fort St. John', 'Williams Lake', 'Revelstoke', 'Nelson', 'Cranbrook', 'Masset' )  or ( REGION_CODE = 48 AND POPULATION_RANGE > 3) or ( REGION_CODE > 59 AND POPULATION_RANGE > 2)",
        'expected': {
            'uri': 'dbname=\'aavbvvv_tttrrr1.bcgov\' port=1521 key=\'OBJECTID\' estimatedmetadata=true srid=3005 type=Point table="ASASD_BBBAAAAAA"."CCA_RDDD_9G_GGGGG_AAAA_BBBBB" (GEOMETRY) sql=NAME IN ( \'Victoria\', \'Vancouver\', \'Nanaimo\', \'Campbell River\', \'Kamloops\', \'Kelowna\', \'Prince Rupert\', \'Prince George\', \'Smithers\', \'Atlin\', \'Fort Nelson\', \'Fort St. John\', \'Williams Lake\', \'Revelstoke\', \'Nelson\', \'Cranbrook\', \'Masset\' )  or ( REGION_CODE = 48 AND POPULATION_RANGE > 3) or ( REGION_CODE > 59 AND POPULATION_RANGE > 2)',
            'provider': 'oracle', 'wkb_type': 1,
            'factory': 'SdeWorkspaceFactory'
        }
    },
    'DBTablename sde': {
        'object': {
            'name': 'AA_BBBBBBBB.AAA_BBBBBBB_CCCC_DDDDD',
            'dataset_name': {
                'name': '',
                'browse_name': '',
                'connection_properties': None,
                'path_name': '',
                'workspace_type': 'ESRI_REMOTEDATABASE_WORKSPACE',
                'workspace_factory': {
                    'type': 'SdeWorkspaceFactory',
                    'version': 1
                },
                'name_string': '',
                'type': 'WorkspaceName',
                'version': 1
            },
            'datasource_type': 'Table',
            'type': 'DBTableName',
            'version': 1
        },
        'base': '/home/me/test_slyr/ABBBB/r2/MXDs',
        'crs': '',
        'subset': '',
        'skip_old': True,
        'expected': {
            'uri': '/home/me/test_slyr/ABBBB/r2/MXDs/|layername=AA_BBBBBBBB.AAA_BBBBBBB_CCCC_DDDDD',
            'file_name': '/home/me/test_slyr/ABBBB/r2/MXDs/',
            'provider': 'ogr',
            'wkb_type': 100,
            'factory': 'SdeWorkspaceFactory'
        }
    },
    'SDE Table': {
        'object': {
            'name': 'AA_SSSSSSSS.SSSRRR',
            'category': '',
            'datasource_type': 'SDE Table',
            'workspace_name': {
                'name': 'C:\\Users\\A333333\\AppData\\Roaming\\ESRI\\Desktop10.2\\ArcCatalog\\ssss.sde',
                'browse_name': 'ArcSDE Data',
                'connection_properties': {
                    'SERVER': 'ssss',
                    'INSTANCE': 'sde:oracle11g:ssss',
                    'DBCLIENT': 'oracle',
                    'DB_CONNECTION_PROPERTIES': 'ssss',
                    'PROJECT_INSTANCE': 'sde',
                    'IS_GEODATABASE': 'true',
                    'AUTHENTICATION_MODE': 'DBMS',
                    'VERSION': 'SDE.DEFAULT',
                    'CONNPROP-REV': 'Rev1.0',
                    'type': 'PropertySet',
                    'version': 1
                },
                'path_name': '',
                'workspace_type': 'ESRI_REMOTEDATABASE_WORKSPACE',
                'workspace_factory': {
                    'type': 'SdeWorkspaceFactory',
                    'version': 1
                },
                'name_string': '',
                'type': 'WorkspaceName',
                'version': 1
            },
            'type': 'TableName',
            'version': 1
        },
        'base': '/home/me/test_slyr/ABBBB/r2/MXDs',
        'crs': '',
        'subset': '',
        'expected': {
            'uri': 'C:/Users/A333333/AppData/Roaming/ESRI/Desktop10.2/ArcCatalog/ssss.sde|layername=AA_SSSSSSSS.SSSRRR',
            'provider': 'ogr',
            'wkb_type': 100,
            'file_name': 'C:/Users/A333333/AppData/Roaming/ESRI/Desktop10.2/ArcCatalog/ssss.sde',
            'factory': 'SdeWorkspaceFactory'
        }
    },
    'RouteEventSourceName': {
        'object': {
            'name': 'A_Bbbbbbb_Cc_dddddd_Eeee',
            'name_string': '',
            'workspace_name': {
                'name': 'AAA_Bbbbbb Feature-Class-Locator',
                'description': 'Aaa',
                'datasource_type': 'Bbbb',
                'name_string': '',
                'feature_class_name': {
                    'name': 'AAA_Bbbbbb',
                    'dataset_name': {
                        'name': 'I:\\gis\\AAAAAA\\SHP-DATA\\Aaaaalllll\\AAA_Bbbbbb.gdb',
                        'browse_name': 'AAA_Bbbbbb',
                        'connection_properties': {
                            'DATABASE': 'I:\\gis\\AAAAAA\\SHP-DATA\\Aaaaalllll\\AAA_Bbbbbb.gdb',
                            'type': 'PropertySet',
                            'version': 1
                        },
                        'path_name': '',
                        'workspace_type': 'ESRI_LOCALDATABASE_WORKSPACE',
                        'workspace_factory': {
                            'type': 'FileGDBWorkspaceFactory',
                            'version': 1
                        },
                        'name_string': '',
                        'type': 'WorkspaceName',
                        'version': 1
                    },
                    'datasource_type': 'Feature-Class in File-Geodatabase',
                    'feature_type': 'FT_SIMPLE',
                    'shape_field_name': 'Shape',
                    'shape_type': 'polyline',
                    'compressed': False,
                    'name_string': '',
                    'type': 'FgdbFeatureClassName',
                    'version': 1
                },
                'route_id_field_name': 'GDE_KEY',
                'route_measure_unit': 'unknown',
                'type': 'RouteMeasureLocatorName',
                'version': 1
            },
            'event_table_name': {
                'name': 'A_Bbbbb_cc_ddddereee',
                'category': '',
                'datasource_type': 'ACCESS Tabelle',
                'workspace_name': {
                    'name': 'C:\\Users\\AAARRRRRA\\AppData\\Roaming\\ESRI\\Desktop10.4\\ArcCatalog\\Zvvccccccc.odc',
                    'browse_name': 'Zvvccccccc',
                    'connection_properties': {
                        'CONNECTSTRING': 'Provider=MSDASQL.1;Persist Security Info=False;Data Source=Zcccxxzzz',
                        'type': 'PropertySet',
                        'version': 1
                    },
                    'path_name': '',
                    'workspace_type': 'ESRI_REMOTEDATABASE_WORKSPACE',
                    'workspace_factory': {
                        'type': 'OLEDBWorkspaceFactory',
                        'version': 1
                    },
                    'name_string': '',
                    'type': 'WorkspaceName',
                    'version': 1
                },
                'type': 'TableName',
                'version': 1
            },
            'route_measure_line_properties': {
                'event_route_id_field': 'StrKey',
                'from_measure_field_name': 'von_km',
                'to_measure_field_name': 'bis_km',
                'lateral_offset_field_name': '',
                'event_measure_unit': 'unknown',
                'add_error_field': False,
                'error_field_name': 'LOC_ERROR',
                'm_direction_offsetting': True,
                'type': 'RouteMeasureLineProperties',
                'version': 5
            },
            'type': 'RouteEventSourceName',
            'version': 1
        },
        'base': '/home/me/test_slyr/Vbaaaaaa',
        'crs': 'EPSG:31254',
        'subset': '',
        'expected': {
            'uri': 'I:/gis/AAAAAA/SHP-DATA/Aaaaalllll/AAA_Bbbbbb.gdb|layername=AAA_Bbbbbb',
            'provider': 'ogr',
            'wkb_type': 5,
            'file_name': 'I:/gis/AAAAAA/SHP-DATA/Aaaaalllll/AAA_Bbbbbb.gdb',
            'factory': 'FileGDBWorkspaceFactory'
        }
    },
    'access mdb relative path': {
        'object': {
            'name': 'XCAAAAA333A',
            'dataset_name': {
                'category': '',
                'name': '',
                'subset_names': None,
                'dataset_type': 'DATASET_TYPE_CONTAINER',
                'workspace_name': {
                    'name': '.\\ooppppo.mdb',
                    'browse_name': 'ooppppo',
                    'connection_properties': None,
                    'path_name': '',
                    'workspace_type': 'ESRI_LOCALDATABASE_WORKSPACE',
                    'workspace_factory': {
                        'type': 'AccessWorkspaceFactory',
                        'version': 1
                    },
                    'name_string': '',
                    'type': 'WorkspaceName',
                    'version': 1
                },
                'type': 'FeatureDatasetName',
                'version': 1
            },
            'datasource_type': 'Geodatabase personal Clase de entidad',
            'feature_type': 'FT_SIMPLE',
            'shape_field_name': 'Shape',
            'shape_type': 'polyline',
            'type': 'FeatureClassName',
            'version': 2
        },
        'base': '/home/me/test_slyr/Anaaaaaa/kkhhhhh44',
        'crs': 'EPSG:3042',
        'subset': '',
        'expected': {
            'uri': '/home/me/test_slyr/Anaaaaaa/kkhhhhh44/ooppppo.mdb|layername=XCAAAAA333A',
            'provider': 'ogr',
            'wkb_type': 5,
            'file_name': '/home/me/test_slyr/Anaaaaaa/kkhhhhh44/ooppppo.mdb',
            'factory': 'AccessWorkspaceFactory'
        }
    },
    'sde sql server any geometry type': {
        'object': {'name': 'GIS."PROD\\BCVBBBBB".%vw_TTRA_AAA_ttttaaaammmaaasdtt',
                   'dataset_name': {'name': 'P:\\GISData\\ArcGIS\\GIS.sde', 'browse_name': 'ArcSDE Data',
                                    'connection_properties': {'SERVER': 'bnnnccc66aa1.prod.local',
                                                              'INSTANCE': 'sde:sqlserver:bnnnccc66aa1.prod.local',
                                                              'DBCLIENT': 'sqlserver',
                                                              'DB_CONNECTION_PROPERTIES': 'bnnnccc66aa1.prod.local',
                                                              'DATABASE': 'GIS', 'IS_GEODATABASE': 'true',
                                                              'AUTHENTICATION_MODE': 'OSA', 'CONNPROP-REV': 'Rev1.0',
                                                              'VERSION': 'sde.DEFAULT', 'type': 'PropertySet',
                                                              'version': 1}, 'path_name': '',
                                    'workspace_type': 'ESRI_REMOTEDATABASE_WORKSPACE',
                                    'workspace_factory': {'type': 'SdeWorkspaceFactory', 'version': 1},
                                    'name_string': '', 'type': 'WorkspaceName', 'version': 1},
                   'datasource_type': 'Query Feature Class', 'feature_type': 'FT_SIMPLE', 'shape_field_name': '',
                   'shape_type': 'any', 'topologies': [], 'query': {
                'query': 'select OBJECTID, TENEMENT, FMT_TENID, TENID, NAME, JV, REGION, PROJECT, TYPE, SURVSTATUS, TENSTATUS, HOLDERCNT, HOLDER1, ADDR1, HOLDER2, ADDR2, STARTDATE, STARTTIME, ENDDATE, ENDTIME, GRANTDATE, GRANTTIME, LEGAL_AREA, UNIT_OF_MEASURE, SPECIAL_IND, EXTRACT_DATE, COMBINED_REPORTING_NO, ALL_HOLDERS, AREA_KM2, COMBINED_REPORTING_NAME, Shape from GIS.GISDO.vw_TTRA_AAA_ttttaaaammmaaasdtt',
                'fid': 'OBJECTID', 'geometry_field': 'Shape', 'esri_oid': 'ESRI_OID', 'fields': {'fields': [
                    {'name': 'OBJECTID', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 1,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 4, 'precision': 10, 'scale': 0,
                     'editable': True, 'is_nullable': False, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'TENEMENT', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 10, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'FMT_TENID', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 16, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'TENID', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 12, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'NAME', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 30, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'JV', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 10, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'REGION', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 5, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'PROJECT', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 11, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'TYPE', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 50, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'SURVSTATUS', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 15, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'TENSTATUS', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 10, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'HOLDERCNT', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 1,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 4, 'precision': 10, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'HOLDER1', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 80, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'ADDR1', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 150, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'HOLDER2', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 80, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'ADDR2', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 150, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'STARTDATE', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 5,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 36, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'STARTTIME', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 8, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'ENDDATE', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 5,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 36, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'ENDTIME', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 8, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'GRANTDATE', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 5,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 36, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'GRANTTIME', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 8, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'LEGAL_AREA', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 3,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 8, 'precision': 38, 'scale': 8,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'UNIT_OF_MEASURE', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 4, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'SPECIAL_IND', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 1, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'EXTRACT_DATE', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 5,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 36, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'COMBINED_REPORTING_NO', 'alias': '', 'model_name': '', 'default_value': None,
                     'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 10, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'ALL_HOLDERS', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 200, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'AREA_KM2', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 3,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 8, 'precision': 38, 'scale': 8,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None,
                     'type': 'Field', 'version': 2},
                    {'name': 'COMBINED_REPORTING_NAME', 'alias': '', 'model_name': '', 'default_value': None,
                     'field_type': 4, 'value_domain': None, 'geometry_definition': None, 'field_length': 40,
                     'precision': 0,
                     'scale': 0, 'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'Shape', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 7,
                     'value_domain': None,
                     'geometry_definition': {'average_number_of_points': 0, 'geometry_type': 'polygon', 'crs': {
                         'wkt': 'GEOGCS["GCS_GDA_1994",DATUM["D_GDA_1994",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433],AUTHORITY["EPSG",12483]]',
                         'x_origin': -400.0, 'y_origin': -400.0, 'xy_scale': 999999999.9999999, 'z_origin': -100000.0,
                         'z_scale': 10000.0, 'm_origin': -100000.0, 'm_scale': 10000.0,
                         'xy_tolerance': 8.983152841195213e-09, 'z_tolerance': 0.001, 'm_tolerance': 0.001,
                         'is_high_precision': True, 'type': 'GeographicCoordinateSystem', 'version': 7}, 'has_m': False,
                                             'has_z': False, 'type': 'GeometryDef', 'version': 1}, 'field_length': 4,
                     'precision': 0, 'scale': 0, 'editable': True, 'is_nullable': True, 'required': False,
                     'domain_fixed': False, 'raster_def': None, 'type': 'Field', 'version': 2}], 'type': 'Fields',
                    'version': 2}, 'crs': {
                    'wkt': 'GEOGCS["GCS_GDA_1994",DATUM["D_GDA_1994",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433],AUTHORITY["EPSG",12483]]',
                    'x_origin': -400.0, 'y_origin': -400.0, 'xy_scale': 999999999.9999999, 'z_origin': -100000.0,
                    'z_scale': 10000.0, 'm_origin': -100000.0, 'm_scale': 10000.0,
                    'xy_tolerance': 8.983152841195213e-09,
                    'z_tolerance': 0.001, 'm_tolerance': 0.001, 'is_high_precision': True,
                    'type': 'GeographicCoordinateSystem', 'version': 7}, 'type': 'GpkgFeatureClassQuery', 'version': 2},
                   'type': 'GpkgFeatureClassName', 'version': 2}, 'base': '/home/me/test_slyr/Misc',
        'crs': 'EPSG:3111',
        'subset': '',
        'skip_old': True,
        'expected': {
            'factory': 'SdeWorkspaceFactory',
            'provider': 'mssql',
            'uri': "dbname='GIS' host=bnnnccc66aa1.prod.local key='OBJECTID' srid=3111 "
                   "type=GeometryCollection disableInvalidGeometryHandling='0' "
                   'table="PROD\\\\BCVBBBBB"."%vw_TTRA_AAA_ttttaaaammmaaasdtt"',
            'wkb_type': 7
        }
    },
    'feature server 2': {
        'object': {
            'name': '0',
            'dataset_name': {
                'name': 'https://services3.arcgis.com/Bxcxcvvx4554321/arcgis/rest/services/C3333_pOoooAAAA/FeatureServer',
                'browse_name': 'FeatureServer',
                'connection_properties': {
                    'URL': 'https://services3.arcgis.com/Bxcxcvvx4554321/arcgis/rest/services',
                    'RESTURL': 'https://services3.arcgis.com/Bxcxcvvx4554321/arcgis/rest/services',
                    'CONNECTIONTYPE': 2,
                    'HIDEUSERPROPERTY': False,
                    'UseSSOIdentityIfPortalOwned': True,
                    'checkForAuthentication': True,
                    'HTTPTIMEOUT': 60,
                    'MESSAGEFORMAT': 2,
                    'ServerType': 3,
                    'TOKENPROVIDERTYPE': 'AGOL',
                    'DATABASE': 'https://services3.arcgis.com/Bxcxcvvx4554321/arcgis/rest/services/C3333_pOoooAAAA/FeatureServer',
                    'type': 'PropertySet',
                    'version': 1
                },
                'path_name': '',
                'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                'workspace_factory': {
                    'type': 'FeatureServiceWorkspaceFactory',
                    'version': 1
                },
                'name_string': '',
                'type': 'WorkspaceName',
                'version': 1
            },
            'datasource_type': 'Feature Service Feature Class',
            'feature_type': 'FT_SIMPLE',
            'shape_field_name': 'Shape',
            'shape_type': 'polyline',
            'type': 'FeatureClassName',
            'version': 2
        },
        'base': '/home/me/test_slyr/Misc/lyr',
        'crs': 'EPSG:28356',
        'subset': '',
        'expected': {
            'factory': 'FeatureServiceWorkspaceFactory',
            'provider': 'arcgisfeatureserver',
            'uri': "crs='EPSG:28356' "
                   "url='https://services3.arcgis.com/Bxcxcvvx4554321/arcgis/rest/services/C3333_pOoooAAAA/FeatureServer/0'",
            'wkb_type': 5}
    },
    'CadWorkspaceFactory': {
        'object': {
            'name': 'Annotation',
            'dataset_name': {
                'category': '',
                'name': '',
                'subset_names': None,
                'dataset_type': 'DATASET_TYPE_CONTAINER',
                'workspace_name': {
                    'name': 'P:\\Saaasdas Baaaaa\\Jhggff Trrrrr\\AAAA_BBBBB\\CAD\\DWG\\999_AAB',
                    'browse_name': 'CAD Data',
                    'connection_properties': {
                        'DATABASE': 'P:\\Saaasdas Baaaaa\\Jhggff Trrrrr\\AAAA_BBBBB\\CAD\\DWG\\999_AAB',
                        'type': 'PropertySet',
                        'version': 1
                    },
                    'path_name': '',
                    'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                    'workspace_factory': {
                        'type': 'CadWorkspaceFactory',
                        'version': 1
                    },
                    'name_string': '',
                    'type': 'WorkspaceName',
                    'version': 1
                },
                'type': 'FeatureDatasetName',
                'version': 1
            },
            'datasource_type': 'CAD Annotation Feature Class',
            'feature_type': 'FT_COVERAGE_ANNOTATION',
            'shape_field_name': 'Shape',
            'shape_type': 'point',
            'type': 'FeatureClassName',
            'version': 2
        },
        'base': '/home/me/test_slyr/Misc/lyr',
        'crs': 'EPSG:4326',
        'subset': '',
        'skip_old': True,
        'expected': {
            'factory': 'CadWorkspaceFactory',
            'file_name': 'P:/Saaasdas Baaaaa/Jhggff Trrrrr/AAAA_BBBBB/CAD/DWG/999_AAB.dwg',
            'provider': 'ogr',
            'uri': 'P:/Saaasdas Baaaaa/Jhggff Trrrrr/AAAA_BBBBB/CAD/DWG/999_AAB.dwg|layername=Annotation',
            'wkb_type': 1
        }
    },
    'XY Event fields with text': {
        'object': {
            'name': 'BBBASAA.csv_Features',
            'feature_dataset_name': {
                'name': 'BBBASAA.csv',
                'category': '',
                'datasource_type': 'Text File',
                'workspace_name': {
                    'name': 'C:\\Projects\\Ghhhh_Aaaaaa_ZBbbb\\2021 Aaa Bbbbbbbb\\Pictures',
                    'browse_name': 'Pictures',
                    'connection_properties': {
                        'DATABASE': 'C:\\Projects\\Ghhhh_Aaaaaa_ZBbbb\\2021 Aaa Bbbbbbbb\\Pictures',
                        'type': 'PropertySet',
                        'version': 1
                    },
                    'path_name': '',
                    'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                    'workspace_factory': {
                        'type': 'TextFileWorkspaceFactory',
                        'version': 1
                    },
                    'name_string': '',
                    'type': 'WorkspaceName',
                    'version': 1
                },
                'type': 'TableName',
                'version': 1
            },
            'event_properties': {
                'x_field': 'X_Coord',
                'y_field': 'Y_Coord',
                'z_field': 'SOMA',
                'type': 'XYEvent2FieldsProperties',
                'version': 1
            },
            'crs': {
                'wkt': 'PROJCS["WGS_1984_UTM_Zone_23S",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",10000000.0],PARAMETER["Central_Meridian",-45.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]',
                'x_origin': -5120900.0,
                'y_origin': 1900.0,
                'm_origin': -100000.0,
                'z_origin': -100000.0,
                'xy_scale': 10000.0,
                'm_scale': 10000.0,
                'z_scale': 10000.0,
                'xy_tolerance': 0.001,
                'z_tolerance': 0.001,
                'm_tolerance': 0.001,
                'is_high_precision': True,
                'type': 'ProjectedCoordinateSystem',
                'version': 6
            },
            'type': 'XYEventSourceName',
            'version': 1
        },
        'base': '/home/me/test_slyr/Aaaaaa Bbbbbb',
        'crs': 'EPSG:32723',
        'subset': '',
        'skip_old': True,
        'expected': {
            'factory': 'TextFileWorkspaceFactory',
            'file_name': 'C:/Projects/Ghhhh_Aaaaaa_ZBbbb/2021 Aaa Bbbbbbbb/Pictures/BBBASAA.csv',
            'provider': 'ogr',
            'uri': 'C:/Projects/Ghhhh_Aaaaaa_ZBbbb/2021 Aaa Bbbbbbbb/Pictures/BBBASAA.csv',
            'wkb_type': 100
        }},
    'SQL server with escaped table name': {
        'object': {
            'name': 'ccaaaaaccc."AD\\CCCCDA.SMITH".%SV_CAADA_TABLE_NAME',
            'dataset_name': {
                'name': 'C:\\Users\\CCCCDA.SMITH\\AppData\\Roaming\\ESRI\\Desktop10.2\\ArcCatalog\\daaaaa@ccaaaaaccc.sde',
                'browse_name': 'ArcSDE Data',
                'connection_properties': {
                    'SERVER': 'sde_prod',
                    'INSTANCE': 'sde:sqlserver:sde_prod',
                    'DBCLIENT': 'sqlserver',
                    'DB_CONNECTION_PROPERTIES': 'sde_prod',
                    'DATABASE': 'ccaaaaaccc',
                    'IS_GEODATABASE': 'true',
                    'AUTHENTICATION_MODE': 'OSA',
                    'CONNPROP-REV': 'Rev1.0',
                    'VERSION': 'sde.DEFAULT',
                    'type': 'PropertySet',
                    'version': 1
                },
                'path_name': '',
                'workspace_type': 'ESRI_REMOTEDATABASE_WORKSPACE',
                'workspace_factory': {
                    'type': 'SdeWorkspaceFactory',
                    'version': 1
                },
                'name_string': '',
                'type': 'WorkspaceName',
                'version': 1
            },
            'datasource_type': 'Query Feature Class',
            'feature_type': 'FT_SIMPLE',
            'shape_field_name': '',
            'shape_type': 'any',
            'topologies': [],
            'query': {
                'query': 'select OBJECTID, Shape, PLAN_LOT, parcel_num, gis_ref, parish, county, assessment_num, old_ass_num, house_number, street_name, street_type, suburb, joined_property_address, area, area_measure, name1, name2, joined_owner_name, address1, address2, address3, joined_poastal_address, rates_zone, rates_class, rates_flag, parcel_flag, LOT, PLAN_ from ccaaaaaccc.gis.SV_CAADA_TABLE_NAME',
                'fid': 'PLAN_LOT', 'geometry_field': 'Shape', 'esri_oid': 'ESRI_OID', 'fields': {'fields': [
                    {'name': 'OBJECTID', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 1,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 4, 'precision': 10, 'scale': 0,
                     'editable': True, 'is_nullable': False, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'Shape', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 7,
                     'value_domain': None,
                     'geometry_definition': {'average_number_of_points': 0, 'geometry_type': 'polygon', 'crs': {
                         'wkt': 'PROJCS["GDA_1994_MGA_Zone_56",GEOGCS["GCS_GDA_1994",DATUM["D_GDA_1994",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",10000000.0],PARAMETER["Central_Meridian",153.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0],AUTHORITY["EPSG",28356]]',
                         'x_origin': -5120900.0, 'y_origin': 1900.0, 'm_origin': -100000.0, 'z_origin': -100000.0,
                         'xy_scale': 10000.0, 'm_scale': 10000.0, 'z_scale': 10000.0, 'xy_tolerance': 0.001,
                         'z_tolerance': 0.001, 'm_tolerance': 0.001, 'is_high_precision': True,
                         'type': 'ProjectedCoordinateSystem', 'version': 6}, 'has_m': False, 'has_z': False,
                                             'type': 'GeometryDef', 'version': 1}, 'field_length': 4, 'precision': 0,
                     'scale': 0, 'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'PLAN_LOT', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 25, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'parcel_num', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 1,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 4, 'precision': 10, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'gis_ref', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 20, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'parish', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 40, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'county', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 40, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'assessment_num', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 1,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 4, 'precision': 10, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'old_ass_num', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 15, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'house_number', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 133, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'street_name', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 40, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'street_type', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 4, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'suburb', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 35, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'joined_property_address', 'alias': '', 'model_name': '', 'default_value': None,
                     'field_type': 4, 'value_domain': None, 'geometry_definition': None, 'field_length': 215,
                     'precision': 0, 'scale': 0, 'editable': True, 'is_nullable': True, 'required': False,
                     'domain_fixed': False, 'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'area', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 3,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 8, 'precision': 14, 'scale': 4,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'area_measure', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 1, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'name1', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 50, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'name2', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 50, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'joined_owner_name', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 101, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'address1', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 50, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'address2', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 50, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'address3', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 50, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'joined_poastal_address', 'alias': '', 'model_name': '', 'default_value': None,
                     'field_type': 4, 'value_domain': None, 'geometry_definition': None, 'field_length': 152,
                     'precision': 0, 'scale': 0, 'editable': True, 'is_nullable': True, 'required': False,
                     'domain_fixed': False, 'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'rates_zone', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 4, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'rates_class', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 4, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'rates_flag', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 1, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'parcel_flag', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 1, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'LOT', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 10, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2},
                    {'name': 'PLAN_', 'alias': '', 'model_name': '', 'default_value': None, 'field_type': 4,
                     'value_domain': None, 'geometry_definition': None, 'field_length': 15, 'precision': 0, 'scale': 0,
                     'editable': True, 'is_nullable': True, 'required': False, 'domain_fixed': False,
                     'raster_def': None, 'type': 'Field', 'version': 2}], 'type': 'Fields', 'version': 2}, 'crs': {
                    'wkt': 'PROJCS["GDA_1994_MGA_Zone_56",GEOGCS["GCS_GDA_1994",DATUM["D_GDA_1994",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",10000000.0],PARAMETER["Central_Meridian",153.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0],AUTHORITY["EPSG",28356]]',
                    'x_origin': -5120900.0, 'y_origin': 1900.0, 'm_origin': -100000.0, 'z_origin': -100000.0,
                    'xy_scale': 10000.0, 'm_scale': 10000.0, 'z_scale': 10000.0, 'xy_tolerance': 0.001,
                    'z_tolerance': 0.001, 'm_tolerance': 0.001, 'is_high_precision': True,
                    'type': 'ProjectedCoordinateSystem', 'version': 6}, 'type': 'GpkgFeatureClassQuery', 'version': 3},
            'type': 'GpkgFeatureClassName', 'version': 2},
        'base': '/home/nyall/Documents/North Road/SLYR/ABBBB/r2/MXDs',
        'crs': '',
        'subset': '',
        'skip_old': True,
        'expected': {
            'factory': 'SdeWorkspaceFactory',
            'provider': 'mssql',
            'uri': "dbname='ccaaaaaccc' host=sde_prod key='OBJECTID' srid=0 type=GeometryCollection "
                   "disableInvalidGeometryHandling='0' "
                   'table="AD\\\\CCCCDA.SMITH"."%SV_CAADA_TABLE_NAME"',
            'wkb_type': 7}
    },
    'XY event source with join': {
        'object': {
            'name': 'Awwwww_Addbb_XY_RAAAA',
            'feature_dataset_name': {
                'name': 'Awwwww_Addbb_XY_RAAAA_Data',
                'workspace_name': {
                    'name': 'JoinUIRelationship',
                    'destination_name': {
                        'name': 'Awwwww_Addbb_Data',
                        'workspace_name': {
                            'name': 'JoinUIRelationship',
                            'destination_name': {
                                'name': 'Wwwww_AAaaaa',
                                'category': '',
                                'datasource_type': 'File Geodatabase Table',
                                'workspace_name': {
                                    'name': 'R:\\PROJECTS\\A399999\\Data\\Vector\\Working\\A399999_4888_AAAA_4444\\Data.gdb',
                                    'browse_name': 'Data',
                                    'connection_properties': {
                                        'DATABASE': 'R:\\PROJECTS\\A399999\\Data\\Vector\\Working\\A399999_4888_AAAA_4444\\Data.gdb',
                                        'type': 'PropertySet',
                                        'version': 1},
                                    'path_name': '',
                                    'workspace_type': 'ESRI_LOCALDATABASE_WORKSPACE',
                                    'workspace_factory': {
                                        'type': 'FileGDBWorkspaceFactory',
                                        'version': 1},
                                    'name_string': '',
                                    'type': 'WorkspaceName',
                                    'version': 1},
                                'type': 'FgdbTableName',
                                'version': 1},
                            'origin_name': {
                                'name': 'Roads_for_map6_ABBBB_Projects',
                                'dataset_name': {
                                    'name': 'R:\\PROJECTS\\A399999\\Data\\Vector\\Working\\A399999_4888_AAAA_4444\\Data.gdb',
                                    'browse_name': 'Data',
                                    'connection_properties': {
                                        'DATABASE': 'R:\\PROJECTS\\A399999\\Data\\Vector\\Working\\A399999_4888_AAAA_4444\\Data.gdb',
                                        'type': 'PropertySet',
                                        'version': 1},
                                    'path_name': '',
                                    'workspace_type': 'ESRI_LOCALDATABASE_WORKSPACE',
                                    'workspace_factory': {
                                        'type': 'FileGDBWorkspaceFactory',
                                        'version': 1},
                                    'name_string': '',
                                    'type': 'WorkspaceName',
                                    'version': 1},
                                'datasource_type': 'File Geodatabase Feature Class',
                                'feature_type': 'FT_SIMPLE',
                                'shape_field_name': 'SHAPE',
                                'shape_type': 'polyline',
                                'compressed': False,
                                'name_string': '',
                                'type': 'FgdbFeatureClassName',
                                'version': 1},
                            'origin_primary_key': 'Code',
                            'origin_foreign_key': 'Code',
                            'forward_path_label': 'Forwards',
                            'backward_path_label': 'Backwards',
                            'type': 'MemoryRelationshipClassName',
                            'version': 1},
                        'filter': {'sub_fields': '*', 'where_clause': '',
                                   'output_spatial_reference_field_name': '',
                                   'output_spatial_reference': None,
                                   'spatial_resolution': 0.0, 'postfix_clause': '',
                                   'prefix_clause': '',
                                   'filter_defs': {'type': 'ArrayOfFilterDef',
                                                   'version': 1},
                                   'row_offset': None, 'row_count': None,
                                   'spatial_relation': 0,
                                   'spatial_relation_description': '',
                                   'reference_geometry': None,
                                   'geometry_field_name': 'SHAPE', 'fid_set': None,
                                   'type': 'SpatialFilter', 'version': 1},
                        'type': 'RelQueryTableName', 'version': 3},
                    'origin_name': {'name': 'Wwwww_AAaaaa_XY',
                                    'category': '',
                                    'datasource_type': 'File Geodatabase Table',
                                    'workspace_name': {
                                        'name': 'R:\\PROJECTS\\A399999\\Data\\Vector\\Working\\A399999_4888_AAAA_4444\\Data.gdb',
                                        'browse_name': 'Data',
                                        'connection_properties': {
                                            'DATABASE': 'R:\\PROJECTS\\A399999\\Data\\Vector\\Working\\A399999_4888_AAAA_4444\\Data.gdb',
                                            'type': 'PropertySet',
                                            'version': 1},
                                        'path_name': '',
                                        'workspace_type': 'ESRI_LOCALDATABASE_WORKSPACE',
                                        'workspace_factory': {
                                            'type': 'FileGDBWorkspaceFactory',
                                            'version': 1},
                                        'name_string': '',
                                        'type': 'WorkspaceName',
                                        'version': 1},
                                    'type': 'FgdbTableName',
                                    'version': 1},
                    'origin_primary_key': 'Roads_for_map6_ABBBB_Projects.OBJECTID',
                    'origin_foreign_key': 'FeatureID',
                    'forward_path_label': 'Forwards',
                    'backward_path_label': 'Backwards',
                    'type': 'MemoryRelationshipClassName', 'version': 1},
                'filter': {'type': 'QueryFilter', 'filter': '', 'version': 5},
                'type': 'RelQueryTableName', 'version': 3},
            'event_properties': {'x_field': 'Wwwww_AAaaaa_XY.INSIDE_X',
                                 'y_field': 'Wwwww_AAaaaa_XY.INSIDE_Y',
                                 'z_field': '', 'type': 'XYEvent2FieldsProperties',
                                 'version': 1}, 'crs': {
                'wkt': 'PROJCS["WGS_1984_Web_Mercator_Auxiliary_Sphere",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mercator_Auxiliary_Sphere"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",0.0],PARAMETER["Standard_Parallel_1",0.0],PARAMETER["Auxiliary_Sphere_Type",0.0],UNIT["Meter",1.0]]',
                'x_origin': -20037700.0, 'y_origin': -30241100.0, 'm_origin': -100000.0, 'z_origin': -100000.0,
                'xy_scale': 10000.0, 'm_scale': 10000.0, 'z_scale': 10000.0, 'xy_tolerance': 0.001,
                'z_tolerance': 0.001,
                'm_tolerance': 0.001, 'is_high_precision': True, 'type': 'ProjectedCoordinateSystem', 'version': 6},
            'type': 'XYEventSourceName', 'version': 1},
        'base': '/home/nyall/Documents/North Road/SLYR/ABBBB/r2/MXDs', 'crs': 'EPSG:3857',
        'subset': "Wwwww_AAaaaa.Code NOT LIKE 'ABBBB%'",
        'skip_old': True,
        'expected': {
            'factory': '',
            'provider': 'ogr', 'uri': 'temp', 'wkb_type': 0
        }},
    's57': {
        'object': {
            'name': 'BOOPOOOA_4',
            'dataset_name': {
                'category': '',
                'name': '',
                'subset_names': None,
                'dataset_type': 'DATASET_TYPE_CONTAINER',
                'workspace_name': {
                    'name': '\\\\bbaa6661\\kklllaaaaaa\\CCDA\\CCDA-Test\\GEODATA\\Projects\\Inland\\AAC_AAC\\99_BBB\\01.01_AAA\\AAA_Bbbbbbb_cccccc\\20210101_EAAA_ccccccccc',
                    'browse_name': '20210101_EAAA_ccccccccc',
                    'connection_properties': {
                        'DATABASE': '\\\\bbaa6661\\kklllaaaaaa\\CCDA\\CCDA-Test\\GEODATA\\Projects\\Inland\\AAC_AAC\\99_BBB\\01.01_AAA\\AAA_Bbbbbbb_cccccc\\20210101_EAAA_ccccccccc',
                        'type': 'PropertySet',
                        'version': 1
                    },
                    'path_name': '',
                    'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                    'workspace_factory': {
                        'type': 'S57WorkspaceFactory',
                        'version': 1
                    },
                    'name_string': '',
                    'type': 'WorkspaceName',
                    'version': 1
                }, 'type': 'FeatureDatasetName',
                'version': 1
            },
            'datasource_type': '',
            'feature_type': 'FT_SIMPLE',
            'shape_field_name': 'SHAPE',
            'shape_type': 'point',
            'type': 'FeatureClassName',
            'version': 2
        },
        'base': '/home/nyall/Documents/North Road/SLYR/Aaaaaa',
        'crs': 'EPSG:32632',
        'subset': '',
        'skip_old': True,
        'expected': {
            'factory': 'S57WorkspaceFactory',
            'file_name': '//bbaa6661/kklllaaaaaa/CCDA/CCDA-Test/GEODATA/Projects/Inland/AAC_AAC/99_BBB/01.01_AAA/AAA_Bbbbbbb_cccccc/20210101_EAAA_ccccccccc',
            'provider': 'ogr',
            'uri': '//bbaa6661/kklllaaaaaa/CCDA/CCDA-Test/GEODATA/Projects/Inland/AAC_AAC/99_BBB/01.01_AAA/AAA_Bbbbbbb_cccccc/20210101_EAAA_ccccccccc|layername=BOOPOOOA_4',
            'wkb_type': 1
        }
    },
    'FME Workspace': {
        'object': {
            'name': 'aaaaaa_bbbbbbb_ws',
            'dataset_name': {
                'category': '',
                'name': '',
                'subset_names': None,
                'dataset_type': 'DATASET_TYPE_CONTAINER',
                'workspace_name': {
                    'name': 'C:\\Users\\ccaaaaaa\\AppData\\Roaming\\Safe Software\\Interoperability',
                    'browse_name': 'Interoperability',
                    'connection_properties': None,
                    'path_name': '',
                    'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                    'workspace_factory': {
                        'type': 'FMEWorkspaceFactory',
                        'version': 1
                    }, 'name_string': '',
                    'type': 'WorkspaceName',
                    'version': 1},
                'type': 'FeatureDatasetName',
                'version': 1
            },
            'datasource_type': 'Interoperability Feature Class',
            'feature_type': 'FT_SIMPLE',
            'shape_field_name': 'SHAPE',
            'shape_type': 'multipoint',
            'type': 'FeatureClassName',
            'version': 2
        },
        'base': '/home/nyall/Documents/North Road/SLYR/Ddddddd',
        'crs': 'EPSG:25832',
        'subset': '',
        'skip_old': True,
        'expected': {
            'factory': 'FMEWorkspaceFactory',
            'file_name': 'C:/Users/ccaaaaaa/AppData/Roaming/Safe '
                         'Software/Interoperability/aaaaaa_bbbbbbb_ws',
            'provider': 'ogr',
            'uri': 'C:/Users/ccaaaaaa/AppData/Roaming/Safe Software/Interoperability/aaaaaa_bbbbbbb_ws'
        }
    },
    'street map': {
        'object': {
            'name': 'usa_mr.edg',
            'dataset_name': {
                'name': 'usa\\streets',
                'browse_name': 'StreetMap Data',
                'connection_properties': None,
                'path_name': '',
                'workspace_type': 'ESRI_FILESYSTEM_WORKSPACE',
                'workspace_factory': {
                    'type': 'StreetMapWorkspaceFactory',
                    'version': 1
                },
                'name_string': '',
                'type': 'WorkspaceName',
                'version': 1
            },
            'datasource_type': 'StreetMap Feature Class',
            'feature_type': 'FT_SIMPLE',
            'shape_field_name': 'Shape',
            'shape_type': 'polyline',
            'type': 'FeatureClassName',
            'version': 2
        },
        'base': '/home/me/data/Ddddddd',
        'crs': 'EPSG:25832',
        'subset': '',
        'skip_old': True,
        'expected': {
            'factory': 'StreetMapWorkspaceFactory',
            'file_name': '/home/me/data/Ddddddd/usa/streets/usa_mr.edg',
            'provider': 'ogr',
            'uri': '/home/me/data/Ddddddd/usa/streets/usa_mr.edg',
            'wkb_type': 5
        }
    },
    'ims': {
        'object': {
            'name': 'DD AAAaaaaaa - Bbbbbbb',
            'dataset_name': {
                'name': 'D:\\ZZ_bbbbbbbb',
                'browse_name': 'IMS Feature Service Data',
                'connection_properties': {
                    'URL': 'http://www.aaaaaaaaaaaaa.gov',
                    'SERVICENAME': 'AAA_MY_SERVICE',
                    'SERVICETYPE': 'FeatureMapService',
                    'type': 'PropertySet',
                    'version': 1
                },
                'path_name': '',
                'workspace_type': 'ESRI_REMOTEDATABASE_WORKSPACE',
                'workspace_factory': {
                    'type': 'IMSWorkspaceFactory',
                    'version': 1
                },
                'name_string': '',
                'type': 'WorkspaceName', 'version': 1
            },
            'datasource_type': 'ArcIMS Feature Class',
            'feature_type': 'FT_SIMPLE',
            'shape_field_name': '',
            'shape_type': 'polygon',
            'type': 'FeatureClassName',
            'version': 2
        },
        'base': '/home/me/data/Ddddddd',
        'crs': 'EPSG:25832',
        'subset': '',
        'skip_old': True,
        'expected': {
            'factory': 'IMSWorkspaceFactory',
            'file_name': 'D:/ZZ_bbbbbbbb/DD AAAaaaaaa - Bbbbbbb',
            'provider': 'ogr',
            'uri': 'D:/ZZ_bbbbbbbb/DD AAAaaaaaa - Bbbbbbb',
            'wkb_type': 6
        }

    }
}

initialize_registry()


class TestLayerSourceConversion(unittest.TestCase):
    """
    Test layer source conversion
    """

    maxDiff = None

    def test_sources(self):
        """
        Test source conversion
        """
        context = Context()

        def unsupported(string, level):
            pass

        context.unsupported_object_callback = unsupported

        for name, definition in expected.items():
            print(name)

            obj = REGISTRY.create_object_from_dict(definition['object'])

            expected_res = deepcopy(definition['expected'])
            factory = expected_res['factory']
            del expected_res['factory']

            res = DatasetNameConverter.convert(obj, base=definition.get('base', ''),
                                               crs=QgsCoordinateReferenceSystem(definition.get('crs', '')),
                                               subset=definition.get('subset'),
                                               context=context
                                               )

            self.assertEqual(expected_res, res.to_dict())
            if res.factory is not None:
                self.assertEqual(factory, res.factory.__class__.__name__)

    def test_split_to_tokens(self):
        """
        Test DatasetNameConverter.split_to_tokens
        """
        self.assertEqual(DatasetNameConverter.split_to_tokens(''), [])
        self.assertEqual(DatasetNameConverter.split_to_tokens('aaa'), ['aaa'])
        self.assertEqual(DatasetNameConverter.split_to_tokens('aaA.bb11'), ['aaA', 'bb11'])
        self.assertEqual(DatasetNameConverter.split_to_tokens('aaA.bb11.cc-111'), ['aaA', 'bb11', 'cc-111'])
        self.assertEqual(DatasetNameConverter.split_to_tokens('aaA.bb11.cc-111.5555'),
                         ['aaA', 'bb11', 'cc-111', '5555'])
        self.assertEqual(DatasetNameConverter.split_to_tokens('"aaA.bb11".cc-111.5555'),
                         ['aaA.bb11', 'cc-111', '5555'])
        self.assertEqual(DatasetNameConverter.split_to_tokens('aaA."bb11.cc-111".5555'), ['aaA', 'bb11.cc-111', '5555'])
        self.assertEqual(DatasetNameConverter.split_to_tokens('aaA.bb11."cc-111.5555"'), ['aaA', 'bb11', 'cc-111.5555'])


if __name__ == '__main__':
    unittest.main()
