# pylint: disable=bad-continuation,too-many-lines

"""
Test Connection conversion
"""

import unittest

from .test_case import SlyrTestCase

from ..converters.context import Context
from ..converters.connection import FdlConnectionParser, ConnectionConverter


class TestConnectionConverter(SlyrTestCase):
    """
    Test Connection Conversion
    """

    def test_connection_string(self):
        """
        Test converting encoded connection string
        """
        context = Context()
        context.upgrade_http_to_https = True
        uri, provider = ConnectionConverter.convert_connection_string(
            "SERVER=gis-server;INSTANCE=sde:sqlserver:gis-server\\sqlexpress_ri;DBCLIENT=sqlserver;DB_CONNECTION_PROPERTIES=gis-server\\sqlexpress_ri;DATABASE=mydb;USER=myadmin;VERSION=dbo.DEFAULT;AUTHENTICATION_MODE=DBMS",
            context,
        )
        self.assertEqual(
            uri.uri(), "dbname='mydb' host=gis-server\\sqlexpress_ri user='myadmin'"
        )
        self.assertEqual(provider, "mssql")

    def test_fdl(self):
        """
        Test FDL properties extraction
        """
        res = FdlConnectionParser.parse_fdl(
            'FDLVERSION1,WFS,https://geo.limburg.be/arcgis/services/Mobiliteit/MapServer/WFSServer?,RUNTIME_MACROS,"PREFER_DATASET_URL,No,PREFERRED_VERSION,1.1.0,CONNECTION_PROPERTIES_GROUP,NO,PREFER_POST,No,HTTP_USER_AGENT,,CONNECTION_TIMEOUT,90,TRANSFER_TIMEOUT,90,TABLELIST,""""""Bedrijventerreinen_-_Bedrijventerrein  {Bedrijventerreinen_-_Bedrijventerrein}"""""",MAX_RESULT_FEATURES,30000,START_INDEX,<Unused>,COUNT,<Unused>,OUTPUT_FORMAT,,FILTER_EXPRESSION,,IGNORE_APPLICATON_SCHEMA,no,XSD_DOC,,FME_FEATURE_IDENTIFIER,,MAP_FEATURE_COLLECTION,,GML_FEATURE_ELEMENTS,<Unused>,GMLSRS_GEOMETRY_PARAMETERS,,SRS_AXIS_ORDER,,SRS_ANGLE_DIRECTION,,ENFORCE_PATH_CONTINUITY_BY,SNAPPING_END_POINTS,GML_READER_GROUP,,USE_OLD_READER,NO,DISABLE_AUTOMATIC_READER_TYPE_SELECTION,NO,DISABLE_XML_NAMESPACE_PROCESSING,NO,GML_FEATURE_PROPERTIES,,MAP_EMBEDDED_OBJECTS_AS,ATTRIBUTES,MAP_PREDEFINED_GML_PROPERTIES,NO,MAP_GEOMETRY_COLUMNS,YES,ADD_NAMESPACE_PREFIX_TO_NAMES,,QNAMES_FOR_PROPERTIES_TO_IGNORE,,GML_FEATURE_PROPERTIES_ATTRIBUTE_HANDLING_GROUP,,MAP_COMPLEX_PROPERTIES_AS,""Nested Attributes"",MAX_MULTI_LIST_LEVEL,,XML_FRAGMENTS_AS_DOCUMENTS,YES,FLATTEN_XML_FRAGMENTS,NO,FLATTEN_XML_FRAGMENTS_OPEN_LIST_BRACE,,FLATTEN_XML_FRAGMENTS_CLOSE_LIST_BRACE,,FLATTEN_XML_FRAGMENTS_SEPARATOR,,ARCGIS_CACHE_GROUP,,LOCAL_CACHE_EXPIRY,60,EXPOSE_ATTRS_GROUP,,WFS_EXPOSE_FORMAT_ATTRS,,USE_SEARCH_ENVELOPE,NO,SEARCH_ENVELOPE_MINX,0,SEARCH_ENVELOPE_MINY,0,SEARCH_ENVELOPE_MAXX,0,SEARCH_ENVELOPE_MAXY,0,CLIP_TO_ENVELOPE,NO,BBOX_COORDINATE_SYSTEM,,NETWORK_AUTHENTICATION,,WFS_SERVICE_TITLE,WFS,_MERGE_SCHEMAS,YES",META_MACROS,"SourcePREFER_DATASET_URL,No,SourcePREFERRED_VERSION,1.1.0,SourceCONNECTION_PROPERTIES_GROUP,NO,SourcePREFER_POST,No,SourceHTTP_USER_AGENT,,SourceCONNECTION_TIMEOUT,90,SourceTRANSFER_TIMEOUT,90,SourceMAX_RESULT_FEATURES,30000,SourceSTART_INDEX,<Unused>,SourceCOUNT,<Unused>,SourceOUTPUT_FORMAT,,SourceFILTER_EXPRESSION,,SourceIGNORE_APPLICATON_SCHEMA,no,SourceXSD_DOC,,SourceFME_FEATURE_IDENTIFIER,,SourceMAP_FEATURE_COLLECTION,,SourceGML_FEATURE_ELEMENTS,<Unused>,SourceGMLSRS_GEOMETRY_PARAMETERS,,SourceSRS_AXIS_ORDER,,SourceSRS_ANGLE_DIRECTION,,SourceENFORCE_PATH_CONTINUITY_BY,SNAPPING_END_POINTS,SourceGML_READER_GROUP,,SourceUSE_OLD_READER,NO,SourceDISABLE_AUTOMATIC_READER_TYPE_SELECTION,NO,SourceDISABLE_XML_NAMESPACE_PROCESSING,NO,SourceGML_FEATURE_PROPERTIES,,SourceMAP_EMBEDDED_OBJECTS_AS,ATTRIBUTES,SourceMAP_PREDEFINED_GML_PROPERTIES,NO,SourceMAP_GEOMETRY_COLUMNS,YES,SourceADD_NAMESPACE_PREFIX_TO_NAMES,,SourceQNAMES_FOR_PROPERTIES_TO_IGNORE,,SourceGML_FEATURE_PROPERTIES_ATTRIBUTE_HANDLING_GROUP,,SourceMAP_COMPLEX_PROPERTIES_AS,""Nested Attributes"",SourceMAX_MULTI_LIST_LEVEL,,SourceXML_FRAGMENTS_AS_DOCUMENTS,YES,SourceFLATTEN_XML_FRAGMENTS,NO,SourceFLATTEN_XML_FRAGMENTS_OPEN_LIST_BRACE,,SourceFLATTEN_XML_FRAGMENTS_CLOSE_LIST_BRACE,,SourceFLATTEN_XML_FRAGMENTS_SEPARATOR,,SourceARCGIS_CACHE_GROUP,,SourceLOCAL_CACHE_EXPIRY,60,SourceEXPOSE_ATTRS_GROUP,,SourceWFS_EXPOSE_FORMAT_ATTRS,,SourceUSE_SEARCH_ENVELOPE,NO,SourceSEARCH_ENVELOPE_MINX,0,SourceSEARCH_ENVELOPE_MINY,0,SourceSEARCH_ENVELOPE_MAXX,0,SourceSEARCH_ENVELOPE_MAXY,0,SourceCLIP_TO_ENVELOPE,NO,SourceBBOX_COORDINATE_SYSTEM,,SourceNETWORK_AUTHENTICATION,,SourceWFS_SERVICE_TITLE,WFS",METAFILE,WFS,COORDSYS,"""ESRIWKT|Belge_Lambert_1972|PROJCS[""Belge_Lambert_1972"",GEOGCS[""GCS_Belge_1972"",DATUM[""D_Belge_1972"",SPHEROID[""International_1924"",6378388.0,297.0]],PRIMEM[""Greenwich"",0.0],UNIT[""Degree"",0.0174532925199433]],PROJECTION[""Lambert_Conformal_Conic""],PARAMETER[""False_Easting"",150000.01256],PARAMETER[""False_Northing"",5400088.4378],PARAMETER[""Central_Meridian"",4.367486666666666],PARAMETER[""Standard_Parallel_1"",49.8333339],PARAMETER[""Standard_Parallel_2"",51.16666723333333],PARAMETER[""Latitude_Of_Origin"",90.0],UNIT[""Meter"",1.0]]""",IDLIST,"""Bedrijventerreinen_-_Bedrijventerrein  {Bedrijventerreinen_-_Bedrijventerrein}"""'
        )
        self.assertEqual(
            res,
            {
                "COORDSYS": {
                    "name": "Belge_Lambert_1972",
                    "wkt": 'PROJCS["Belge_Lambert_1972",GEOGCS["GCS_Belge_1972",DATUM["D_Belge_1972",SPHEROID["International_1924",6378388.0,297.0]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",150000.01256],PARAMETER["False_Northing",5400088.4378],PARAMETER["Central_Meridian",4.367486666666666],PARAMETER["Standard_Parallel_1",49.8333339],PARAMETER["Standard_Parallel_2",51.16666723333333],PARAMETER["Latitude_Of_Origin",90.0],UNIT["Meter",1.0]]',
                },
                "IDLIST": "Bedrijventerreinen_-_Bedrijventerrein  "
                "{Bedrijventerreinen_-_Bedrijventerrein}",
                "METAFILE": "WFS",
                "META_MACROS": {
                    "SourceADD_NAMESPACE_PREFIX_TO_NAMES": None,
                    "SourceARCGIS_CACHE_GROUP": None,
                    "SourceBBOX_COORDINATE_SYSTEM": None,
                    "SourceCLIP_TO_ENVELOPE": False,
                    "SourceCONNECTION_PROPERTIES_GROUP": False,
                    "SourceCONNECTION_TIMEOUT": 90,
                    "SourceCOUNT": "<Unused>",
                    "SourceDISABLE_AUTOMATIC_READER_TYPE_SELECTION": False,
                    "SourceDISABLE_XML_NAMESPACE_PROCESSING": False,
                    "SourceENFORCE_PATH_CONTINUITY_BY": "SNAPPING_END_POINTS",
                    "SourceEXPOSE_ATTRS_GROUP": None,
                    "SourceFILTER_EXPRESSION": None,
                    "SourceFLATTEN_XML_FRAGMENTS": False,
                    "SourceFLATTEN_XML_FRAGMENTS_CLOSE_LIST_BRACE": None,
                    "SourceFLATTEN_XML_FRAGMENTS_OPEN_LIST_BRACE": None,
                    "SourceFLATTEN_XML_FRAGMENTS_SEPARATOR": None,
                    "SourceFME_FEATURE_IDENTIFIER": None,
                    "SourceGMLSRS_GEOMETRY_PARAMETERS": None,
                    "SourceGML_FEATURE_ELEMENTS": "<Unused>",
                    "SourceGML_FEATURE_PROPERTIES": None,
                    "SourceGML_FEATURE_PROPERTIES_ATTRIBUTE_HANDLING_GROUP": None,
                    "SourceGML_READER_GROUP": None,
                    "SourceHTTP_USER_AGENT": None,
                    "SourceIGNORE_APPLICATON_SCHEMA": False,
                    "SourceLOCAL_CACHE_EXPIRY": 60,
                    "SourceMAP_COMPLEX_PROPERTIES_AS": "Nested Attributes",
                    "SourceMAP_EMBEDDED_OBJECTS_AS": "ATTRIBUTES",
                    "SourceMAP_FEATURE_COLLECTION": None,
                    "SourceMAP_GEOMETRY_COLUMNS": True,
                    "SourceMAP_PREDEFINED_GML_PROPERTIES": False,
                    "SourceMAX_MULTI_LIST_LEVEL": None,
                    "SourceMAX_RESULT_FEATURES": 30000,
                    "SourceNETWORK_AUTHENTICATION": None,
                    "SourceOUTPUT_FORMAT": None,
                    "SourcePREFERRED_VERSION": "1.1.0",
                    "SourcePREFER_DATASET_URL": False,
                    "SourcePREFER_POST": False,
                    "SourceQNAMES_FOR_PROPERTIES_TO_IGNORE": None,
                    "SourceSEARCH_ENVELOPE_MAXX": 0,
                    "SourceSEARCH_ENVELOPE_MAXY": 0,
                    "SourceSEARCH_ENVELOPE_MINX": 0,
                    "SourceSEARCH_ENVELOPE_MINY": 0,
                    "SourceSRS_ANGLE_DIRECTION": None,
                    "SourceSRS_AXIS_ORDER": None,
                    "SourceSTART_INDEX": "<Unused>",
                    "SourceTRANSFER_TIMEOUT": 90,
                    "SourceUSE_OLD_READER": False,
                    "SourceUSE_SEARCH_ENVELOPE": False,
                    "SourceWFS_EXPOSE_FORMAT_ATTRS": None,
                    "SourceWFS_SERVICE_TITLE": "WFS",
                    "SourceXML_FRAGMENTS_AS_DOCUMENTS": True,
                    "SourceXSD_DOC": None,
                },
                "RUNTIME_MACROS": {
                    "ADD_NAMESPACE_PREFIX_TO_NAMES": None,
                    "ARCGIS_CACHE_GROUP": None,
                    "BBOX_COORDINATE_SYSTEM": None,
                    "CLIP_TO_ENVELOPE": False,
                    "CONNECTION_PROPERTIES_GROUP": False,
                    "CONNECTION_TIMEOUT": 90,
                    "COUNT": "<Unused>",
                    "DISABLE_AUTOMATIC_READER_TYPE_SELECTION": False,
                    "DISABLE_XML_NAMESPACE_PROCESSING": False,
                    "ENFORCE_PATH_CONTINUITY_BY": "SNAPPING_END_POINTS",
                    "EXPOSE_ATTRS_GROUP": None,
                    "FILTER_EXPRESSION": None,
                    "FLATTEN_XML_FRAGMENTS": False,
                    "FLATTEN_XML_FRAGMENTS_CLOSE_LIST_BRACE": None,
                    "FLATTEN_XML_FRAGMENTS_OPEN_LIST_BRACE": None,
                    "FLATTEN_XML_FRAGMENTS_SEPARATOR": None,
                    "FME_FEATURE_IDENTIFIER": None,
                    "GMLSRS_GEOMETRY_PARAMETERS": None,
                    "GML_FEATURE_ELEMENTS": "<Unused>",
                    "GML_FEATURE_PROPERTIES": None,
                    "GML_FEATURE_PROPERTIES_ATTRIBUTE_HANDLING_GROUP": None,
                    "GML_READER_GROUP": None,
                    "HTTP_USER_AGENT": None,
                    "IGNORE_APPLICATON_SCHEMA": False,
                    "LOCAL_CACHE_EXPIRY": 60,
                    "MAP_COMPLEX_PROPERTIES_AS": "Nested Attributes",
                    "MAP_EMBEDDED_OBJECTS_AS": "ATTRIBUTES",
                    "MAP_FEATURE_COLLECTION": None,
                    "MAP_GEOMETRY_COLUMNS": True,
                    "MAP_PREDEFINED_GML_PROPERTIES": False,
                    "MAX_MULTI_LIST_LEVEL": None,
                    "MAX_RESULT_FEATURES": 30000,
                    "NETWORK_AUTHENTICATION": None,
                    "OUTPUT_FORMAT": None,
                    "PREFERRED_VERSION": "1.1.0",
                    "PREFER_DATASET_URL": False,
                    "PREFER_POST": False,
                    "QNAMES_FOR_PROPERTIES_TO_IGNORE": None,
                    "SEARCH_ENVELOPE_MAXX": 0,
                    "SEARCH_ENVELOPE_MAXY": 0,
                    "SEARCH_ENVELOPE_MINX": 0,
                    "SEARCH_ENVELOPE_MINY": 0,
                    "SRS_ANGLE_DIRECTION": None,
                    "SRS_AXIS_ORDER": None,
                    "START_INDEX": "<Unused>",
                    "TABLELIST": "Bedrijventerreinen_-_Bedrijventerrein  "
                    "{Bedrijventerreinen_-_Bedrijventerrein}",
                    "TRANSFER_TIMEOUT": 90,
                    "USE_OLD_READER": False,
                    "USE_SEARCH_ENVELOPE": False,
                    "WFS_EXPOSE_FORMAT_ATTRS": None,
                    "WFS_SERVICE_TITLE": "WFS",
                    "XML_FRAGMENTS_AS_DOCUMENTS": True,
                    "XSD_DOC": None,
                    "_MERGE_SCHEMAS": True,
                },
                "WFS": "https://geo.limburg.be/arcgis/services/Mobiliteit/MapServer/WFSServer?",
                "version": "FDLVERSION1",
            },
        )


if __name__ == "__main__":
    unittest.main()
