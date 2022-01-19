#!/usr/bin/env python

# /***************************************************************************
# color_ramp.py
# ----------
# Date                 : October 2019
# copyright            : (C) 2019 by Nyall Dawson
# email                : nyall.dawson@gmail.com
#
#  ***************************************************************************/
#
# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

"""
Dataset name converter
"""

import os
import re
from pathlib import Path
from typing import Optional, List

from qgis.core import (Qgis,
                       QgsCoordinateReferenceSystem,
                       QgsWkbTypes)

from .connection import ConnectionConverter
from .context import Context
from .converter import NotImplementedException
from .utils import ConversionUtils
from ..parser.objects.table_name import TableName
from ..parser.objects.workspace_factory import WorkspaceFactory
from ..parser.objects.workspace_name import WorkspaceName


class DataSourceProperties:
    """
    Encapsulates properties of a data source required for QGIS layers
    """

    def __init__(self, uri: Optional[str] = None,
                 wkb_type: Optional[QgsWkbTypes.Type] = None,
                 provider: Optional[str] = None,
                 encoding: Optional[str] = None,
                 file_name: Optional[str] = None,
                 factory: Optional[WorkspaceFactory] = None):
        self.uri: Optional[str] = uri
        self.wkb_type: Optional[QgsWkbTypes.Type] = wkb_type
        self.provider: Optional[str] = provider
        self.encoding: Optional[str] = encoding
        self.file_name: Optional[str] = file_name
        self.factory = factory

    def to_dict(self) -> dict:
        """
        Converts the properties to a dict
        """
        res = {
            'uri': self.uri,
            'provider': self.provider,
        }
        if self.wkb_type is not None:
            res['wkb_type'] = self.wkb_type
        if self.encoding is not None:
            res['encoding'] = self.encoding
        if self.file_name is not None:
            res['file_name'] = self.file_name
        return res


class DatasetNameConverter:  # pylint: disable=too-many-public-methods
    """
    Dataset name converter
    """

    # pylint: disable=unused-argument

    @staticmethod
    def convert_file_gdb_workspace(name,
                                   workspace_name: WorkspaceName,
                                   base: str,
                                   crs: QgsCoordinateReferenceSystem,
                                   subset: str,
                                   context: Context) -> DataSourceProperties:
        """
        Convert FileGDBWorkspaceFactory
        """
        provider = 'ogr'
        file_name = ConversionUtils.get_absolute_path(workspace_name.name, base)
        layer_name = name.name
        uri = '{}|layername={}'.format(file_name, layer_name)

        wkb_type = None
        if name.__class__.__name__ == 'FgdbFeatureClassName':
            wkb_type = DatasetNameConverter.geometry_type_to_wkb(name.shape_type)
        elif name.__class__.__name__ == 'FgdbTableName':
            wkb_type = QgsWkbTypes.NoGeometry
        elif name.__class__.__name__ == 'RasterCatalogName':
            wkb_type = QgsWkbTypes.MultiPolygon

        if os.path.exists(file_name) and context.unsupported_object_callback:
            # try to open the gdb and see if it's compressed
            cdf_files = Path(file_name).glob('*.cdf')
            try:
                next(cdf_files)
                context.unsupported_object_callback(
                    'Compressed Geodatabase files are not supported in QGIS, the database {} will need to be decompressed before it can be used outside of ArcGIS'.format(
                        file_name), level=Context.CRITICAL)
            except StopIteration:
                pass
        elif context.unsupported_object_callback and name.datasource_type == 'File Geodatabase Feature Class (compressed)':
            context.unsupported_object_callback(
                'Compressed Geodatabase files are not supported in QGIS, the database {} will need to be decompressed before it can be used outside of ArcGIS'.format(
                    file_name), level=Context.CRITICAL)

        return DataSourceProperties(uri=uri,
                                    wkb_type=wkb_type,
                                    provider=provider,
                                    file_name=file_name)

    @staticmethod
    def convert_shapefile_workspace(name,  # pylint: disable=too-many-locals,too-many-branches
                                    workspace_name: WorkspaceName, base: str, crs: QgsCoordinateReferenceSystem,
                                    subset: str, context: Context) -> DataSourceProperties:
        """
        Convert ShapefileWorkspaceFactory
        """
        provider = 'ogr'
        folder = ConversionUtils.get_absolute_path(workspace_name.name, base)

        if name.__class__.__name__ == 'FeatureClassName':
            wkb_type = DatasetNameConverter.geometry_type_to_wkb(name.shape_type)
            extension = '.shp'
        elif name.__class__.__name__ == 'TableName':
            wkb_type = QgsWkbTypes.NoGeometry
            extension = '.dbf'
        else:
            assert False

        file_name = folder + '/' + name.name + extension
        uri = file_name

        encoding = None
        if Qgis.QGIS_VERSION_INT < 31600:
            cpg_path = uri[:-3] + 'cpg'
            if not os.path.exists(cpg_path):
                # No cpg file exists, assume ISO8859-1
                encoding = 'ISO-8859-1'
            else:
                # we ALWAYS use the cpg file - QGIS behavior of ignoring this by default is broken
                with open(cpg_path, 'rt', encoding='utf8') as f:
                    cpg = f.readline().strip()
                    # using gdal logic, see https://github.com/OSGeo/gdal/blob/a1220c07a5a81404a0036e0e9c010ea74863ca95/gdal/ogr/ogrsf_frmts/shape/ogrshapelayer.cpp#L433

                    try:
                        cpg_int = int(cpg)
                        if 437 <= cpg_int <= 950 or 1250 <= cpg_int <= 1258:
                            encoding = 'cp{}'.format(cpg_int)
                    except:  # nopep8, pylint: disable=bare-except
                        pass
                    if not encoding and cpg.lower().startswith('8859'):
                        if cpg[4] == '-':
                            encoding = 'ISO-8859-{}'.format(cpg[5:])
                        else:
                            encoding = 'ISO-8859-{}'.format(cpg[4:])
                    elif not encoding and (cpg.lower().startswith('utf-8') or cpg.lower().startswith('utf8')):
                        encoding = 'UTF-8'
                    elif not encoding and cpg.lower().startswith('ANSI 1251'):
                        encoding = 'cp1251'

        return DataSourceProperties(uri=uri,
                                    wkb_type=wkb_type,
                                    provider=provider,
                                    file_name=file_name,
                                    encoding=encoding)

    @staticmethod
    def convert_access_workspace(name, workspace_name: WorkspaceName, base: str, crs: QgsCoordinateReferenceSystem,
                                 subset: str, context: Context) -> DataSourceProperties:
        """
        Convert AccessWorkspaceFactory
        """
        provider = 'ogr'
        file_name = ConversionUtils.get_absolute_path(workspace_name.name, base)
        layer_name = name.name
        uri = '{}|layername={}'.format(file_name, layer_name)

        if name.__class__.__name__ == 'TableName':
            wkb_type = QgsWkbTypes.NoGeometry
        elif name.__class__.__name__ == 'FeatureClassName':
            wkb_type = DatasetNameConverter.geometry_type_to_wkb(name.shape_type)
        else:
            assert False

        return DataSourceProperties(uri=uri,
                                    wkb_type=wkb_type,
                                    provider=provider,
                                    file_name=file_name)

    @staticmethod
    def convert_cad_workspace(name, workspace_name: WorkspaceName, base: str, crs: QgsCoordinateReferenceSystem,
                              subset: str, context: Context) -> DataSourceProperties:
        """
        Convert CadWorkspaceFactory
        """
        provider = 'ogr'
        file_name = ConversionUtils.get_absolute_path(workspace_name.name, base) + '.dwg'
        layer_name = name.name
        uri = '{}|layername={}'.format(file_name, layer_name)

        wkb_type = DatasetNameConverter.geometry_type_to_wkb(name.shape_type)

        return DataSourceProperties(uri=uri,
                                    wkb_type=wkb_type,
                                    provider=provider,
                                    file_name=file_name)

    @staticmethod
    def convert_netcdf_workspace(name, workspace_name: WorkspaceName, base: str, crs: QgsCoordinateReferenceSystem,
                                 subset: str, context: Context) -> DataSourceProperties:
        """
        Convert NetCDFWorkspaceFactory

        untested!!... why is this a vector anyway?
        """
        provider = 'ogr'
        file_name = ConversionUtils.get_absolute_path(workspace_name.name, base)
        layer_name = name.name
        uri = '{}|layername={}'.format(file_name, layer_name)

        if name.__class__.__name__ == 'NetCDFTableName':
            wkb_type = QgsWkbTypes.NoGeometry
        else:
            assert False

        return DataSourceProperties(uri=uri,
                                    wkb_type=wkb_type,
                                    provider=provider,
                                    file_name=file_name)

    @staticmethod
    def convert_gpkg_workspace(name, workspace_name: WorkspaceName, base: str, crs: QgsCoordinateReferenceSystem,
                               subset: str, context: Context) -> DataSourceProperties:
        """
        Convert GpkgWorkspaceFactory
        """
        file_name = ConversionUtils.get_absolute_path(workspace_name.name, base)
        layer_name = re.sub(r'main\.%?', '', name.name)
        uri = '{}|layername={}'.format(file_name, layer_name)
        provider = 'ogr'

        if name.__class__.__name__ == 'DBTableName':
            if name.shape_field_name:
                wkb_type = DatasetNameConverter.GEOMETRY_TYPE_TO_WKB_TYPE[name.geometry_type]
                if wkb_type is None:
                    raise NotImplementedException('Cannot convert gpkg of geometry type: {}'.format(name.geometry_type))
            else:
                wkb_type = QgsWkbTypes.NoGeometry
        else:
            if name.query.geometry_field:
                geometry_type = [f for f in name.query.fields.fields if f.name == name.query.geometry_field][
                    0].geometry_def.geometry_type
                wkb_type = DatasetNameConverter.GEOMETRY_TYPE_TO_WKB_TYPE[geometry_type]
                if wkb_type is None:
                    raise NotImplementedException('Cannot convert gpkg of geometry type: {}'.format(geometry_type))
            else:
                wkb_type = QgsWkbTypes.NoGeometry

        return DataSourceProperties(uri=uri,
                                    wkb_type=wkb_type,
                                    provider=provider,
                                    file_name=file_name)

    @staticmethod
    def convert_arcinfo_workspace(name, workspace_name: WorkspaceName, base: str, crs: QgsCoordinateReferenceSystem,
                                  subset: str, context: Context) -> DataSourceProperties:
        """
        Convert ArcInfoWorkspaceFactory
        """
        provider = 'ogr'
        if name.__class__.__name__ == 'TableName':
            file_name = ConversionUtils.get_absolute_path(workspace_name.name, base)
            wkb_type = QgsWkbTypes.NoGeometry
            layer_name = name.name
            if layer_name.endswith('.dat'):
                layer_name = layer_name[:-4]
        else:
            assert name.dataset_name.__class__.__name__ == 'CoverageName'

            workspace_folder_name = ConversionUtils.get_absolute_path(workspace_name.name, base)
            file_name = ConversionUtils.get_absolute_path(name.dataset_name.name, workspace_folder_name)
            wkb_type = DatasetNameConverter.geometry_type_to_wkb(name.shape_type)
            if name.name == 'point':
                layer_name = 'LAB'
            elif name.name == 'line':
                layer_name = 'ARC'
            elif name.name == 'polygon':
                layer_name = 'PAL'
            elif name.name.startswith('region.'):
                layer_name = name.name[len('region.'):]
            elif name.name.startswith('annotation.'):
                layer_name = name.name[len('annotation.'):]
            else:
                layer_name = name.name

            if layer_name.endswith('.dat'):
                layer_name = layer_name[:-4]

        uri = '{}|layername={}'.format(file_name, layer_name)

        return DataSourceProperties(uri=uri,
                                    wkb_type=wkb_type,
                                    provider=provider,
                                    file_name=file_name)

    @staticmethod
    def convert_excel_or_mdb_workspace(name, workspace_name: WorkspaceName, base: str,
                                       crs: QgsCoordinateReferenceSystem,
                                       subset: str, context: Context) -> DataSourceProperties:
        """
        Convert ExcelOrMdbWorkspaceFactory
        """
        provider = 'ogr'
        file_name = ConversionUtils.get_absolute_path(workspace_name.name, base)

        sheet_name = name.name
        if sheet_name.endswith("'"):
            sheet_name = sheet_name[:-1]
        if sheet_name.startswith("'"):
            sheet_name = sheet_name[1:]
        if sheet_name.endswith('$'):
            sheet_name = sheet_name[:-1]
        uri = '{}|layername={}'.format(file_name,
                                       sheet_name)

        if name.__class__.__name__ == 'TableName':
            wkb_type = QgsWkbTypes.NoGeometry
        else:
            assert False

        return DataSourceProperties(uri=uri,
                                    wkb_type=wkb_type,
                                    provider=provider,
                                    file_name=file_name)

    @staticmethod
    def convert_oledb_workspace(name, workspace_name: WorkspaceName, base: str, crs: QgsCoordinateReferenceSystem,
                                subset: str, context: Context) -> DataSourceProperties:
        """
        Convert OLEDBWorkspaceFactory
        """
        provider = 'ogr'
        file_name = ConversionUtils.get_absolute_path(workspace_name.name, base)
        file_name += '.xlsx'  # this is a guess.. maybe .xls?

        sheet_name = name.name
        if sheet_name.endswith("'"):
            sheet_name = sheet_name[:-1]
        if sheet_name.startswith("'"):
            sheet_name = sheet_name[1:]
        if sheet_name.endswith('$'):
            sheet_name = sheet_name[:-1]
        uri = '{}|layername={}'.format(file_name,
                                       sheet_name)

        if name.__class__.__name__ == 'TableName':
            wkb_type = QgsWkbTypes.NoGeometry
        else:
            assert False

        return DataSourceProperties(uri=uri,
                                    wkb_type=wkb_type,
                                    provider=provider,
                                    file_name=file_name)

    @staticmethod
    def convert_text_file_workspace(name, workspace_name: WorkspaceName, base: str, crs: QgsCoordinateReferenceSystem,
                                    subset: str, context: Context) -> DataSourceProperties:
        """
        Convert TextFileWorkspaceFactory
        """
        provider = 'ogr'
        folder_name = ConversionUtils.get_absolute_path(workspace_name.name, base)
        file_name = ConversionUtils.get_absolute_path(name.name, folder_name)
        uri = file_name

        if name.__class__.__name__ == 'TableName':
            wkb_type = QgsWkbTypes.NoGeometry
        else:
            assert False

        return DataSourceProperties(uri=uri,
                                    wkb_type=wkb_type,
                                    provider=provider,
                                    file_name=file_name)

    @staticmethod
    def convert_feature_service_workspace(name, workspace_name: WorkspaceName, base: str,
                                          crs: QgsCoordinateReferenceSystem,
                                          subset: str, context: Context) -> DataSourceProperties:
        """
        Convert FeatureServiceWorkspaceFactory
        """
        # todo -- auto create auth service?
        crs_text = crs.authid()
        if not crs_text:
            crs_text = 'WKT:{}'.format(crs.toWkt())
        uri = "crs='{}' url='{}/{}'".format(crs_text, workspace_name.name, name.name)
        if context.ignore_online_sources:
            uri = ''
        provider = 'arcgisfeatureserver'
        wkb_type = DatasetNameConverter.geometry_type_to_wkb(name.shape_type)
        return DataSourceProperties(uri=uri,
                                    wkb_type=wkb_type,
                                    provider=provider)

    @staticmethod
    def convert_ims_workspace(name, workspace_name: WorkspaceName, base: str,
                              crs: QgsCoordinateReferenceSystem,
                              subset: str, context: Context) -> DataSourceProperties:
        """
        Convert IMSWorkspaceFactory
        """
        if context.unsupported_object_callback:
            context.unsupported_object_callback(
                '{}: IMS data sources are not supported in QGIS'.format(
                    context.layer_name), level=Context.WARNING)

        folder = ConversionUtils.get_absolute_path(workspace_name.name, base)
        file_name = ConversionUtils.get_absolute_path(name.name, folder)
        uri = file_name
        provider = 'ogr'
        wkb_type = DatasetNameConverter.geometry_type_to_wkb(name.shape_type)
        return DataSourceProperties(uri=uri,
                                    provider=provider,
                                    file_name=file_name,
                                    wkb_type=wkb_type)

    @staticmethod
    def convert_tin_workspace(name, workspace_name: WorkspaceName, base: str, crs: QgsCoordinateReferenceSystem,
                              subset: str, context: Context) -> DataSourceProperties:
        """
        Convert TinWorkspaceFactory
        """
        folder = ConversionUtils.get_absolute_path(workspace_name.name, base)
        file_name = ConversionUtils.get_absolute_path(name.name, folder) + '/tedg.adf'
        uri = file_name
        provider = 'mdal'
        return DataSourceProperties(uri=uri,
                                    provider=provider,
                                    file_name=file_name)

    @staticmethod
    def convert_las_dataset_workspace(name, workspace_name: WorkspaceName, base: str, crs: QgsCoordinateReferenceSystem,
                                      subset: str, context: Context) -> DataSourceProperties:
        """
        Convert LasDatasetWorkspaceFactory
        """
        folder = ConversionUtils.get_absolute_path(workspace_name.name, base)
        file_name = ConversionUtils.get_absolute_path(name.name, folder)

        uri = file_name
        provider = 'pdal'
        return DataSourceProperties(uri=uri,
                                    provider=provider,
                                    file_name=file_name)

    @staticmethod
    def convert_s57_workspace(name, workspace_name: WorkspaceName, base: str, crs: QgsCoordinateReferenceSystem,
                              subset: str, context: Context) -> DataSourceProperties:
        """
        Convert S57WorkspaceFactory
        """
        provider = 'ogr'
        file_name = ConversionUtils.get_absolute_path(workspace_name.name, base)
        layer_name = name.name
        uri = '{}|layername={}'.format(file_name, layer_name)

        if name.__class__.__name__ == 'TableName':
            wkb_type = QgsWkbTypes.NoGeometry
        elif name.__class__.__name__ == 'FeatureClassName':
            wkb_type = DatasetNameConverter.geometry_type_to_wkb(name.shape_type)
        else:
            assert False

        return DataSourceProperties(uri=uri,
                                    wkb_type=wkb_type,
                                    provider=provider,
                                    file_name=file_name)

    # pylint: enable=unused-argument

    @staticmethod
    def split_to_tokens(value: str) -> List[str]:
        """
        Splits a string by . separators, respecting " escaping
        """
        if not value:
            return []

        if value[0] == '"':
            parts_search = re.search(r'^"(.*?)"(.*)$', value, re.IGNORECASE)
            part1 = parts_search.group(1)
            part2 = parts_search.group(2)
            if part2.startswith('.'):
                part2 = part2[1:]

            return [part1] + DatasetNameConverter.split_to_tokens(part2)
        else:
            parts_search = re.search(r'^(.*?)\.(.*)$', value, re.IGNORECASE)
            if parts_search:
                part1 = parts_search.group(1)
                part2 = parts_search.group(2)
                return [part1] + DatasetNameConverter.split_to_tokens(part2)
        return [value]

    # pylint: disable=unused-argument

    @staticmethod
    def convert_sde_table_name(name: str, context: Context):
        """
        Converts an SDE table name
        """
        if context.sde_table_name_conversion == 'lower':
            return name.lower()
        elif context.sde_table_name_conversion == 'upper':
            return name.upper()

        return name

    @staticmethod
    def convert_sde_sdc_workspace(name,  # pylint: disable=too-many-branches,too-many-statements
                                  workspace_name: WorkspaceName, base: str, crs: QgsCoordinateReferenceSystem,
                                  subset: str, context: Context, is_sdc: bool) -> DataSourceProperties:
        """
        Convert SdeWorkspaceFactory/SdcWorkspaceFactory
        """
        file_name = ConversionUtils.get_absolute_path(workspace_name.name, base)
        uri = None
        wkb_type = None

        connection = None
        if not is_sdc:
            sde_path = Path(file_name)

            if workspace_name.connection_properties:
                connection = ConnectionConverter.convert_connection(workspace_name.connection_properties, context)
            elif sde_path.exists() and not sde_path.is_dir():
                connection = ConnectionConverter.convert_sde_connection(sde_path, context)

        if connection is not None:
            sde_uri, provider = connection
            # what happens if there's more than one . ???
            if provider == 'oracle':
                parts = DatasetNameConverter.split_to_tokens(name.name)
                if len(parts) == 2:
                    sde_uri.setSchema(parts[0])
                    sde_uri.setTable(DatasetNameConverter.convert_sde_table_name(parts[1], context))
                    if not isinstance(name, TableName):
                        sde_uri.setSrid(str(crs.postgisSrid()))
                        wkb_type = DatasetNameConverter.GEOMETRY_TYPE_TO_WKB_TYPE[name.shape_type]
                        sde_uri.setWkbType(wkb_type)
                        sde_uri.setGeometryColumn(name.shape_field_name)
                    else:
                        sde_uri.setWkbType(QgsWkbTypes.NoGeometry)

                    sde_uri.setSql(subset)
                    sde_uri.setKeyColumn(context.sde_primary_key)

                    uri = sde_uri.uri()
                    file_name = None
                else:
                    context.unsupported_object_callback(
                        f'Could not convert Oracle table name {name.name}. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                        level=Context.CRITICAL)
            elif provider == 'mssql':

                parts = DatasetNameConverter.split_to_tokens(name.name)
                if len(parts) == 3:
                    sde_uri.setSchema(parts[1])
                    sde_uri.setTable(DatasetNameConverter.convert_sde_table_name(parts[2], context))

                    if not isinstance(name, TableName):
                        sde_uri.setSrid(str(crs.postgisSrid()))
                        wkb_type = DatasetNameConverter.GEOMETRY_TYPE_TO_WKB_TYPE[name.shape_type]
                        sde_uri.setWkbType(wkb_type)
                        sde_uri.setGeometryColumn(name.shape_field_name)
                    else:
                        sde_uri.setWkbType(QgsWkbTypes.NoGeometry)

                    sde_uri.setSql(subset)
                    sde_uri.setKeyColumn(context.sde_primary_key)

                    uri = sde_uri.uri()
                    file_name = None
                else:
                    context.unsupported_object_callback(
                        f'Could not convert SQL Server table name {name.name}. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                        level=Context.CRITICAL)
            elif provider == 'postgres':
                parts = DatasetNameConverter.split_to_tokens(name.name)
                if len(parts) == 3:
                    sde_uri.setSchema(parts[1])
                    sde_uri.setTable(DatasetNameConverter.convert_sde_table_name(parts[2], context))

                    if not isinstance(name, TableName):
                        sde_uri.setSrid(str(crs.postgisSrid()))
                        wkb_type = DatasetNameConverter.GEOMETRY_TYPE_TO_WKB_TYPE[name.shape_type]
                        sde_uri.setWkbType(wkb_type)
                        sde_uri.setGeometryColumn(name.shape_field_name)
                    else:
                        sde_uri.setWkbType(QgsWkbTypes.NoGeometry)

                    sde_uri.setSql(subset)
                    sde_uri.setKeyColumn(context.sde_primary_key)

                    uri = sde_uri.uri()
                    file_name = None
                else:
                    context.unsupported_object_callback(
                        f'Could not convert PostgreSQL table name {name.name}. Please email this file to info@north-road.com so that we can add support in a future SLYR release.',
                        level=Context.CRITICAL)
        else:
            provider = 'ogr'
            if name.__class__.__name__ in ('DBTableName', 'TableName'):
                wkb_type = QgsWkbTypes.NoGeometry
            else:
                wkb_type = DatasetNameConverter.geometry_type_to_wkb(name.shape_type)
            if not is_sdc:
                uri = '{}|layername={}'.format(file_name, name.name)
            else:
                file_name = ConversionUtils.get_absolute_path(name.name, file_name)
                uri = file_name

        return DataSourceProperties(uri=uri,
                                    wkb_type=wkb_type,
                                    provider=provider,
                                    file_name=file_name)

    @staticmethod
    def convert_sde_workspace(name, workspace_name: WorkspaceName, base: str, crs: QgsCoordinateReferenceSystem,
                              subset: str, context: Context) -> DataSourceProperties:
        """
        Convert SdeWorkspaceFactory
        """
        return DatasetNameConverter.convert_sde_sdc_workspace(name, workspace_name, base, crs,
                                                              subset, context, False)

    @staticmethod
    def convert_sdc_workspace(name, workspace_name: WorkspaceName, base: str, crs: QgsCoordinateReferenceSystem,
                              subset: str, context: Context) -> DataSourceProperties:
        """
        Convert SdcWorkspaceFactory
        """
        return DatasetNameConverter.convert_sde_sdc_workspace(name, workspace_name, base, crs,
                                                              subset, context, True)

    @staticmethod
    def convert_fme_workspace(name, workspace_name: WorkspaceName, base: str, crs: QgsCoordinateReferenceSystem,
                              subset: str, context: Context) -> DataSourceProperties:
        """
        Convert FMEWorkspaceFactory
        """
        folder = ConversionUtils.get_absolute_path(workspace_name.name, base)
        file_name = ConversionUtils.get_absolute_path(name.name, folder)
        uri = file_name
        provider = 'ogr'

        return DataSourceProperties(uri=uri,
                                    provider=provider,
                                    file_name=file_name)

    @staticmethod
    def convert_street_map_workspace(name, workspace_name: WorkspaceName, base: str, crs: QgsCoordinateReferenceSystem,
                                     subset: str, context: Context) -> DataSourceProperties:
        """
        Convert StreetMapWorkspaceFactory
        """
        if context.unsupported_object_callback:
            context.unsupported_object_callback(
                '{}: Street map data sources are not supported in QGIS'.format(
                    context.layer_name), level=Context.WARNING)

        folder = ConversionUtils.get_absolute_path(workspace_name.name, base)
        file_name = ConversionUtils.get_absolute_path(name.name, folder)
        uri = file_name
        provider = 'ogr'
        wkb_type = DatasetNameConverter.geometry_type_to_wkb(name.shape_type)

        return DataSourceProperties(uri=uri,
                                    provider=provider,
                                    file_name=file_name,
                                    wkb_type=wkb_type)

    # pylint: enable=unused-argument

    @staticmethod
    def convert(name, base: str, crs: QgsCoordinateReferenceSystem,
                context: Context, subset: Optional[str] = None) -> DataSourceProperties:
        """
        Converts a data source name to qgis data source components
        """

        # special handling
        if name.__class__.__name__ == 'RelQueryTableName':
            # this is a special beast -- we need to handle this elsewhere!
            return DataSourceProperties(uri='temp', provider='ogr', wkb_type=QgsWkbTypes.Unknown)
        elif name.__class__.__name__ == 'RouteEventSourceName':
            if context.unsupported_object_callback:
                context.unsupported_object_callback(
                    '{}: Route event sources are not supported in QGIS, layer has been converted to a simple layer'.format(
                        context.layer_name), level=Context.CRITICAL)
            else:
                raise NotImplementedException('Route event sources are not supported in QGIS')

            # get the line feature name from RouteMeasureLocatorName
            return DatasetNameConverter.convert(name.dataset_name.dataset_name, base, crs, context, subset)
        elif name.__class__.__name__ == 'XYEventSourceName':
            # We can't directly map these -- best we can do is try to get the original file
            if context.unsupported_object_callback:
                context.unsupported_object_callback(
                    '{}: XY event sources are not supported in QGIS, layer has been converted to a simple layer'.format(
                        context.layer_name), level=Context.CRITICAL)
            else:
                raise NotImplementedException('XY event sources are not supported in QGIS')

            # get the line feature name from XYEventSourceName
            name = name.feature_dataset_name
            return DatasetNameConverter.convert(name, base, crs, context, subset)

        # the logic here looks like this:
        # - we first need to find the workspace name object
        # - this can be buried any number of levels deep though...!
        # - when we've found the workspace name, we can get the workspace factory
        #   as that tells us what the actual type of dataset we are working with is

        def find_workspace_name(obj) -> Optional[WorkspaceName]:
            if hasattr(obj, 'workspace_name') and isinstance(obj.workspace_name, WorkspaceName):
                return obj.workspace_name

            elif hasattr(obj, 'dataset_name') and isinstance(obj.dataset_name, WorkspaceName):
                return obj.dataset_name

            elif hasattr(obj, 'dataset_name'):
                return find_workspace_name(obj.dataset_name)

            elif hasattr(obj, 'feature_dataset_name'):
                return find_workspace_name(obj.feature_dataset_name)

            return None

        workspace_name = find_workspace_name(name)
        factory = workspace_name.workspace_factory

        FACTORY_MAP = {
            'FileGDBWorkspaceFactory': DatasetNameConverter.convert_file_gdb_workspace,
            'ShapefileWorkspaceFactory': DatasetNameConverter.convert_shapefile_workspace,
            'AccessWorkspaceFactory': DatasetNameConverter.convert_access_workspace,
            'CadWorkspaceFactory': DatasetNameConverter.convert_cad_workspace,
            'NetCDFWorkspaceFactory': DatasetNameConverter.convert_netcdf_workspace,
            'GpkgWorkspaceFactory': DatasetNameConverter.convert_gpkg_workspace,
            'ArcInfoWorkspaceFactory': DatasetNameConverter.convert_arcinfo_workspace,
            'ExcelOrMdbWorkspaceFactory': DatasetNameConverter.convert_excel_or_mdb_workspace,
            'OLEDBWorkspaceFactory': DatasetNameConverter.convert_oledb_workspace,
            'TextFileWorkspaceFactory': DatasetNameConverter.convert_text_file_workspace,
            'FeatureServiceWorkspaceFactory': DatasetNameConverter.convert_feature_service_workspace,
            'TinWorkspaceFactory': DatasetNameConverter.convert_tin_workspace,
            'LasDatasetWorkspaceFactory': DatasetNameConverter.convert_las_dataset_workspace,
            'SdeWorkspaceFactory': DatasetNameConverter.convert_sde_workspace,
            'SdcWorkspaceFactory': DatasetNameConverter.convert_sdc_workspace,
            'S57WorkspaceFactory': DatasetNameConverter.convert_s57_workspace,
            'FMEWorkspaceFactory': DatasetNameConverter.convert_fme_workspace,
            'StreetMapWorkspaceFactory': DatasetNameConverter.convert_street_map_workspace,
            'IMSWorkspaceFactory': DatasetNameConverter.convert_ims_workspace
        }

        conversion_function = FACTORY_MAP.get(factory.__class__.__name__)
        if not conversion_function:
            print(name.to_dict())

        assert conversion_function

        res = conversion_function(name, workspace_name, base, crs, subset, context)
        res.factory = factory
        context.dataset_name = name.name
        return res

    @staticmethod
    def dataset_name_to_wkb_type(name) -> QgsWkbTypes.Type:
        """
        Determines a WKB type from a dataset name
        """
        if name.__class__.__name__ == 'XYEventSourceName':
            return QgsWkbTypes.Point
        elif not hasattr(name, 'shape_type'):
            return QgsWkbTypes.Unknown
        elif name.shape_type == 0:
            # not stored
            return QgsWkbTypes.Unknown
        return DatasetNameConverter.geometry_type_to_wkb(name.shape_type)

    @staticmethod
    def geometry_type_to_wkb(geometry_type) -> QgsWkbTypes.Type:
        """
        Converts ESRI geometry type to QGIS wkb type
        """
        GEOMETRY_TYPES = {
            0: QgsWkbTypes.NoGeometry,
            1: QgsWkbTypes.Point,
            2: QgsWkbTypes.MultiPoint,
            3: QgsWkbTypes.MultiLineString,
            4: QgsWkbTypes.MultiPolygon,
            5: QgsWkbTypes.MultiPolygon,
            6: QgsWkbTypes.MultiLineString,
            7: QgsWkbTypes.Unknown,
            9: QgsWkbTypes.MultiPolygon,
            11: QgsWkbTypes.MultiLineString,
            13: QgsWkbTypes.MultiLineString,
            14: QgsWkbTypes.CircularString,
            15: QgsWkbTypes.Unknown,
            16: QgsWkbTypes.Unknown,
            17: QgsWkbTypes.Unknown,
            18: QgsWkbTypes.Unknown,
            19: QgsWkbTypes.Unknown,
            20: QgsWkbTypes.Unknown,
            21: QgsWkbTypes.Unknown,
            22: QgsWkbTypes.Unknown,
        }
        return GEOMETRY_TYPES[geometry_type]

    GEOMETRY_TYPE_TO_WKB_TYPE = {
        0: QgsWkbTypes.NoGeometry,
        1: QgsWkbTypes.Point,
        2: QgsWkbTypes.MultiPoint,
        3: QgsWkbTypes.LineString,
        4: QgsWkbTypes.Polygon,
        5: QgsWkbTypes.Polygon,
        6: QgsWkbTypes.LineString,
        7: QgsWkbTypes.GeometryCollection,  # 'GEOMETRY_ANY',
        9: None,  # 'GEOMETRY_MULTIPATCH',
        11: QgsWkbTypes.LineString,
        13: QgsWkbTypes.LineString,
        14: QgsWkbTypes.CircularString,
        15: QgsWkbTypes.LineString,
        16: QgsWkbTypes.LineString,
        17: None,  # 'GEOMETRY_BAG',
        18: None,  # 'GEOMETRY_TRIANGLE_STRIP',
        19: None,  # 'GEOMETRY_TRIANGLE_FAN',
        20: None,  # 'GEOMETRY_RAY',
        21: None,  # 'GEOMETRY_SPHERE',
        22: None,  # 'GEOMETRY_TRIANGLES',
    }
