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

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Union

from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.core import (
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsDataSourceUri,
    QgsWkbTypes,
    QgsProviderRegistry,
    QgsBlockingNetworkRequest,
    QgsSettings,
    QgsSQLStatement,
)

from .connection import ConnectionConverter
from .context import Context
from .converter import NotImplementedException
from .crs import CrsConverter
from .utils import ConversionUtils

from ..parser.objects import (
    GpkgFeatureClassQuery,
    DBTableName,
    TableName,
    WorkspaceFactory,
    WorkspaceName,
)


class SqlVisitor(QgsSQLStatement.RecursiveVisitor):
    def __init__(self, statement):
        super().__init__()
        self.tables = []
        self.visit(statement.rootNode())

    def visit(self, node):
        if isinstance(node, QgsSQLStatement.NodeUnaryOperator):
            self.visit_unary_operator(node)
        elif isinstance(node, QgsSQLStatement.NodeBinaryOperator):
            self.visit_binary_operator(node)
        elif isinstance(node, QgsSQLStatement.NodeInOperator):
            self.visit_in_operator(node)
        elif isinstance(node, QgsSQLStatement.NodeBetweenOperator):
            self.visit_between_operator(node)
        elif isinstance(node, QgsSQLStatement.NodeFunction):
            self.visit_function(node)
        elif isinstance(node, QgsSQLStatement.NodeLiteral):
            self.visit_literal(node)
        elif isinstance(node, QgsSQLStatement.NodeColumnRef):
            self.visit_column_ref(node)
        elif isinstance(node, QgsSQLStatement.NodeSelectedColumn):
            self.visit_selected_column(node)
        elif isinstance(node, QgsSQLStatement.NodeTableDef):
            self.visit_table_def(node)
        elif isinstance(node, QgsSQLStatement.NodeSelect):
            self.visit_select(node)
        elif isinstance(node, QgsSQLStatement.NodeJoin):
            self.visit_join(node)
        elif isinstance(node, QgsSQLStatement.NodeColumnSorted):
            self.visit_column_sorted(node)
        elif isinstance(node, QgsSQLStatement.NodeCast):
            self.visit_cast(node)

    def visit_unary_operator(self, node):
        self.visit(node.operand())

    def visit_binary_operator(self, node):
        self.visit(node.opLeft())
        self.visit(node.opRight())

    def visit_in_operator(self, node):
        self.visit(node.node())
        for i in range(node.node().count()):
            self.visit(node.list().list()[i])

    def visit_between_operator(self, node):
        self.visit(node.node())
        self.visit(node.minVal())
        self.visit(node.maxVal())

    def visit_function(self, node):
        for i in range(node.args().count()):
            self.visit(node.args().list()[i])

    def visit_literal(self, node):
        pass

    def visit_column_ref(self, node):
        pass

    def visit_selected_column(self, node):
        self.visit(node.column())

    def visit_table_def(self, node):
        self.tables.append((node.schema(), node.name()))

    def visit_select(self, node):
        for table in node.tables():
            self.visit(table)

    def visit_join(self, node):
        pass

    def visit_column_sorted(self, node):
        self.visit(node.column())

    def visit_cast(self, node):
        self.visit(node.node())


@dataclass
class QueryProperties:
    """
    Properties extracted from a query
    """

    table: Optional[str] = None
    schema: Optional[str] = None
    crs: Optional[QgsCoordinateReferenceSystem] = None
    geometry_column: Optional[str] = None
    wkb_type: Optional[QgsWkbTypes.Type] = None


class DataSourceProperties:
    """
    Encapsulates properties of a data source required for QGIS layers
    """

    def __init__(
        self,
        uri: Optional[str] = None,
        wkb_type: Optional[QgsWkbTypes.Type] = None,
        provider: Optional[str] = None,
        encoding: Optional[str] = None,
        file_name: Optional[str] = None,
        factory: Optional[WorkspaceFactory] = None,
        band: Optional[int] = -1,
    ):
        self.uri: Optional[str] = uri
        self.wkb_type: Optional[QgsWkbTypes.Type] = wkb_type
        self.provider: Optional[str] = provider
        self.encoding: Optional[str] = encoding
        self.file_name: Optional[str] = file_name
        self.factory = factory
        self.band = band

    def to_dict(self) -> dict:
        """
        Converts the properties to a dict
        """
        res = {
            "uri": self.uri,
            "provider": self.provider,
        }
        if self.wkb_type is not None:
            res["wkb_type"] = self.wkb_type
        if self.encoding is not None:
            res["encoding"] = self.encoding
        if self.file_name is not None:
            res["file_name"] = self.file_name
        return res


class DatasetNameConverter:  # pylint: disable=too-many-public-methods
    """
    Dataset name converter
    """

    # pylint: disable=unused-argument

    @staticmethod
    def convert_file_gdb_workspace(
        name,
        workspace_name: WorkspaceName,
        base: str,
        crs: QgsCoordinateReferenceSystem,
        subset: str,
        context: Context,
        document_file: Optional[str] = None,
        wkb_type_hint: QgsWkbTypes.Type = QgsWkbTypes.Type.Unknown,
    ) -> DataSourceProperties:
        """
        Convert FileGDBWorkspaceFactory
        """
        provider = "ogr"
        file_name = ConversionUtils.get_absolute_path(workspace_name.name, base)

        if document_file:
            file_name = context.resolve_filename(document_file, file_name)

        layer_name = name.name
        uri = "{}|layername={}".format(file_name, layer_name)

        wkb_type = None
        if name.__class__.__name__ == "FgdbFeatureClassName":
            wkb_type = DatasetNameConverter.geometry_type_to_wkb(name.shape_type)
        elif name.__class__.__name__ == "FgdbTableName":
            wkb_type = QgsWkbTypes.Type.NoGeometry
        elif name.__class__.__name__ == "RasterCatalogName":
            wkb_type = QgsWkbTypes.Type.MultiPolygon

        if os.path.exists(file_name):
            # try to open the gdb and see if it's compressed
            cdf_files = Path(file_name).glob("*.cdf")
            try:
                next(cdf_files)
                context.push_warning(
                    "Compressed Geodatabase files are not supported in QGIS, the database {} will need to be decompressed before it can be used outside of ArcGIS".format(
                        file_name
                    ),
                    level=Context.CRITICAL,
                )
            except StopIteration:
                pass
        elif name.datasource_type == "File Geodatabase Feature Class (compressed)":
            context.push_warning(
                "Compressed Geodatabase files are not supported in QGIS, the database {} will need to be decompressed before it can be used outside of ArcGIS".format(
                    file_name
                ),
                level=Context.CRITICAL,
            )

        return DataSourceProperties(
            uri=uri, wkb_type=wkb_type, provider=provider, file_name=file_name
        )

    @staticmethod
    def convert_shapefile_workspace(
        name,
        # pylint: disable=too-many-locals,too-many-branches
        workspace_name: WorkspaceName,
        base: str,
        crs: QgsCoordinateReferenceSystem,
        subset: str,
        context: Context,
        document_file: Optional[str] = None,
        wkb_type_hint: QgsWkbTypes.Type = QgsWkbTypes.Type.Unknown,
    ) -> DataSourceProperties:
        """
        Convert ShapefileWorkspaceFactory
        """
        provider = "ogr"
        folder = ConversionUtils.get_absolute_path(workspace_name.name, base)

        if name.__class__.__name__ == "FeatureClassName":
            wkb_type = DatasetNameConverter.geometry_type_to_wkb(name.shape_type)
            extension = ".shp"
        elif name.__class__.__name__ == "TableName":
            wkb_type = QgsWkbTypes.Type.NoGeometry
            extension = ".dbf"
        else:
            assert False

        file_name = ConversionUtils.path_insensitive(
            folder + "/" + name.name + extension
        )
        uri = file_name

        return DataSourceProperties(
            uri=uri, wkb_type=wkb_type, provider=provider, file_name=file_name
        )

    @staticmethod
    def convert_access_workspace(
        name,
        workspace_name: WorkspaceName,
        base: str,
        crs: QgsCoordinateReferenceSystem,
        subset: str,
        context: Context,
        document_file: Optional[str] = None,
        wkb_type_hint: QgsWkbTypes.Type = QgsWkbTypes.Type.Unknown,
    ) -> DataSourceProperties:
        """
        Convert AccessWorkspaceFactory
        """
        provider = "ogr"
        file_name = ConversionUtils.get_absolute_path(workspace_name.name, base)
        layer_name = name.name
        uri = "{}|layername={}".format(file_name, layer_name)

        if name.__class__.__name__ == "TableName":
            wkb_type = QgsWkbTypes.Type.NoGeometry
        elif name.__class__.__name__ == "FeatureClassName":
            wkb_type = DatasetNameConverter.geometry_type_to_wkb(name.shape_type)
        else:
            assert False

        return DataSourceProperties(
            uri=uri, wkb_type=wkb_type, provider=provider, file_name=file_name
        )

    @staticmethod
    def convert_cad_workspace(
        name,
        workspace_name: WorkspaceName,
        base: str,
        crs: QgsCoordinateReferenceSystem,
        subset: str,
        context: Context,
        document_file: Optional[str] = None,
        wkb_type_hint: QgsWkbTypes.Type = QgsWkbTypes.Type.Unknown,
    ) -> DataSourceProperties:
        """
        Convert CadWorkspaceFactory
        """
        provider = "ogr"
        file_name = (
            ConversionUtils.get_absolute_path(workspace_name.name, base) + ".dwg"
        )
        layer_name = name.name
        uri = "{}|layername={}".format(file_name, layer_name)

        wkb_type = DatasetNameConverter.geometry_type_to_wkb(name.shape_type)

        return DataSourceProperties(
            uri=uri, wkb_type=wkb_type, provider=provider, file_name=file_name
        )

    @staticmethod
    def convert_netcdf_workspace(
        name,
        workspace_name: WorkspaceName,
        base: str,
        crs: QgsCoordinateReferenceSystem,
        subset: str,
        context: Context,
        document_file: Optional[str] = None,
        wkb_type_hint: QgsWkbTypes.Type = QgsWkbTypes.Type.Unknown,
    ) -> DataSourceProperties:
        """
        Convert NetCDFWorkspaceFactory

        untested!!... why is this a vector anyway?
        """
        provider = "ogr"
        file_name = ConversionUtils.get_absolute_path(workspace_name.name, base)
        layer_name = name.name
        uri = "{}|layername={}".format(file_name, layer_name)

        if name.__class__.__name__ == "NetCDFTableName":
            wkb_type = QgsWkbTypes.Type.NoGeometry
        else:
            assert False

        return DataSourceProperties(
            uri=uri, wkb_type=wkb_type, provider=provider, file_name=file_name
        )

    @staticmethod
    def convert_gpkg_workspace(
        name,
        workspace_name: WorkspaceName,
        base: str,
        crs: QgsCoordinateReferenceSystem,
        subset: str,
        context: Context,
        document_file: Optional[str] = None,
        wkb_type_hint: QgsWkbTypes.Type = QgsWkbTypes.Type.Unknown,
    ) -> DataSourceProperties:
        """
        Convert GpkgWorkspaceFactory
        """
        file_name = ConversionUtils.get_absolute_path(workspace_name.name, base)
        layer_name = re.sub(r"main\.%?", "", name.name)
        uri = "{}|layername={}".format(file_name, layer_name)
        provider = "ogr"

        if name.__class__.__name__ == "DBTableName":
            if name.shape_field_name:
                wkb_type = DatasetNameConverter.GEOMETRY_TYPE_TO_WKB_TYPE[
                    name.geometry_type
                ]
                if wkb_type is None:
                    raise NotImplementedException(
                        "Cannot convert gpkg of geometry type: {}".format(
                            name.geometry_type
                        )
                    )
            else:
                wkb_type = QgsWkbTypes.Type.NoGeometry
        else:
            if name.query.geometry_field:
                geometry_type = [
                    f
                    for f in name.query.fields.fields
                    if f.name == name.query.geometry_field
                ][0].geometry_def.geometry_type
                wkb_type = DatasetNameConverter.GEOMETRY_TYPE_TO_WKB_TYPE[geometry_type]
                if wkb_type is None:
                    raise NotImplementedException(
                        "Cannot convert gpkg of geometry type: {}".format(geometry_type)
                    )
            else:
                wkb_type = QgsWkbTypes.Type.NoGeometry

        return DataSourceProperties(
            uri=uri, wkb_type=wkb_type, provider=provider, file_name=file_name
        )

    @staticmethod
    def convert_arcinfo_workspace(
        name,
        workspace_name: WorkspaceName,
        base: str,
        crs: QgsCoordinateReferenceSystem,
        subset: str,
        context: Context,
        document_file: Optional[str] = None,
        wkb_type_hint: QgsWkbTypes.Type = QgsWkbTypes.Type.Unknown,
    ) -> DataSourceProperties:
        """
        Convert ArcInfoWorkspaceFactory
        """
        provider = "ogr"
        if name.__class__.__name__ == "TableName":
            file_name = ConversionUtils.get_absolute_path(workspace_name.name, base)
            wkb_type = QgsWkbTypes.Type.NoGeometry
            layer_name = name.name
            if layer_name.endswith(".dat"):
                layer_name = layer_name[:-4]
        else:
            assert name.dataset_name.__class__.__name__ == "CoverageName"

            workspace_folder_name = ConversionUtils.get_absolute_path(
                workspace_name.name, base
            )
            file_name = ConversionUtils.get_absolute_path(
                name.dataset_name.name, workspace_folder_name
            )
            wkb_type = DatasetNameConverter.geometry_type_to_wkb(name.shape_type)
            if name.datasource_type == "Label Feature Class":
                layer_name = "LAB"
            elif name.name == "point":
                layer_name = "LAB"
            elif name.name in ("arc", "line"):
                layer_name = "ARC"
            elif name.name == "polygon":
                layer_name = "PAL"
            elif name.name.startswith("region."):
                layer_name = name.name[len("region.") :]
            elif name.name.startswith("annotation."):
                layer_name = name.name[len("annotation.") :]
            else:
                layer_name = name.name

            if layer_name.endswith(".dat"):
                layer_name = layer_name[:-4]

        uri = "{}|layername={}".format(file_name, layer_name)

        return DataSourceProperties(
            uri=uri, wkb_type=wkb_type, provider=provider, file_name=file_name
        )

    @staticmethod
    def convert_excel_or_mdb_workspace(
        name,
        workspace_name: WorkspaceName,
        base: str,
        crs: QgsCoordinateReferenceSystem,
        subset: str,
        context: Context,
        document_file: Optional[str] = None,
        wkb_type_hint: QgsWkbTypes.Type = QgsWkbTypes.Type.Unknown,
    ) -> DataSourceProperties:
        """
        Convert ExcelOrMdbWorkspaceFactory
        """
        provider = "ogr"
        file_name = ConversionUtils.get_absolute_path(workspace_name.name, base)

        sheet_name = name.name
        if sheet_name.endswith("'"):
            sheet_name = sheet_name[:-1]
        if sheet_name.startswith("'"):
            sheet_name = sheet_name[1:]
        if sheet_name.endswith("$"):
            sheet_name = sheet_name[:-1]
        uri = "{}|layername={}".format(file_name, sheet_name)

        if name.__class__.__name__ == "TableName":
            wkb_type = QgsWkbTypes.Type.NoGeometry
        else:
            assert False

        return DataSourceProperties(
            uri=uri, wkb_type=wkb_type, provider=provider, file_name=file_name
        )

    @staticmethod
    def convert_oledb_workspace(
        name,
        workspace_name: WorkspaceName,
        base: str,
        crs: QgsCoordinateReferenceSystem,
        subset: str,
        context: Context,
        document_file: Optional[str] = None,
        wkb_type_hint: QgsWkbTypes.Type = QgsWkbTypes.Type.Unknown,
    ) -> DataSourceProperties:
        """
        Convert OLEDBWorkspaceFactory
        """
        provider = "ogr"
        file_name = ConversionUtils.get_absolute_path(workspace_name.name, base)
        file_name += ".xlsx"  # this is a guess.. maybe .xls?

        sheet_name = name.name
        if sheet_name.endswith("'"):
            sheet_name = sheet_name[:-1]
        if sheet_name.startswith("'"):
            sheet_name = sheet_name[1:]
        if sheet_name.endswith("$"):
            sheet_name = sheet_name[:-1]
        uri = "{}|layername={}".format(file_name, sheet_name)

        if name.__class__.__name__ == "TableName":
            wkb_type = QgsWkbTypes.Type.NoGeometry
        else:
            assert False

        return DataSourceProperties(
            uri=uri, wkb_type=wkb_type, provider=provider, file_name=file_name
        )

    @staticmethod
    def convert_text_file_workspace(
        name,
        workspace_name: WorkspaceName,
        base: str,
        crs: QgsCoordinateReferenceSystem,
        subset: str,
        context: Context,
        document_file: Optional[str] = None,
        wkb_type_hint: QgsWkbTypes.Type = QgsWkbTypes.Type.Unknown,
    ) -> DataSourceProperties:
        """
        Convert TextFileWorkspaceFactory
        """
        folder_name = ConversionUtils.get_absolute_path(workspace_name.name, base)

        if name.__class__.__name__ == "XYEventSourceName":
            file_name = ConversionUtils.get_absolute_path(
                name.feature_dataset_name.name, folder_name
            )

            # use delimited text provider
            provider = "delimitedtext"

            open_options = [
                "type=csv",
                "maxFields=10000",
                "detectTypes=yes",
                "spatialIndex=yes",
                "subsetIndex=no",
                "watchFile=no",
            ]
            wkb_type = QgsWkbTypes.Type.Point
            open_options.append("xField={}".format(name.event_properties.x_field))
            open_options.append("yField={}".format(name.event_properties.y_field))
            if name.event_properties.z_field:
                wkb_type = QgsWkbTypes.Type.PointZ
                open_options.append("zField={}".format(name.event_properties.z_field))

            crs = CrsConverter.convert_crs(name.crs, context)
            if crs.isValid():
                open_options.append("crs={}".format(crs.authid()))

            uri_parts = {"openOptions": open_options, "path": file_name}
            uri = QgsProviderRegistry.instance().encodeUri(provider, uri_parts)
        else:
            file_name = ConversionUtils.get_absolute_path(name.name, folder_name)
            provider = "ogr"
            uri = file_name

            if name.__class__.__name__ == "TableName":
                wkb_type = QgsWkbTypes.Type.NoGeometry
            else:
                assert False

        return DataSourceProperties(
            uri=uri, wkb_type=wkb_type, provider=provider, file_name=file_name
        )

    @staticmethod
    def convert_feature_service_workspace(
        name,
        workspace_name: WorkspaceName,
        base: str,
        crs: QgsCoordinateReferenceSystem,
        subset: str,
        context: Context,
        document_file: Optional[str] = None,
        wkb_type_hint: QgsWkbTypes.Type = QgsWkbTypes.Type.Unknown,
    ) -> DataSourceProperties:
        """
        Convert FeatureServiceWorkspaceFactory
        """
        # todo -- auto create auth service?
        crs_text = crs.authid()
        if not crs_text:
            crs_text = "WKT:{}".format(crs.toWkt())

        url = "{}/{}".format(workspace_name.name, name.name)

        if context.upgrade_http_to_https:
            url = url.replace("http://", "https://")

        uri = "crs='{}' url='{}'".format(crs_text, url)
        if context.ignore_online_sources:
            uri = ""

        provider = "arcgisfeatureserver"
        wkb_type = DatasetNameConverter.geometry_type_to_wkb(name.shape_type)

        return DataSourceProperties(uri=uri, wkb_type=wkb_type, provider=provider)

    @staticmethod
    def convert_ims_workspace(
        name,
        workspace_name: WorkspaceName,
        base: str,
        crs: QgsCoordinateReferenceSystem,
        subset: str,
        context: Context,
        document_file: Optional[str] = None,
        wkb_type_hint: QgsWkbTypes.Type = QgsWkbTypes.Type.Unknown,
    ) -> DataSourceProperties:
        """
        Convert IMSWorkspaceFactory
        """
        context.push_warning(
            "IMS data sources are not supported in QGIS", level=Context.WARNING
        )

        folder = ConversionUtils.get_absolute_path(workspace_name.name, base)
        file_name = ConversionUtils.get_absolute_path(name.name, folder)
        uri = file_name
        provider = "ogr"
        wkb_type = DatasetNameConverter.geometry_type_to_wkb(name.shape_type)
        return DataSourceProperties(
            uri=uri, provider=provider, file_name=file_name, wkb_type=wkb_type
        )

    @staticmethod
    def convert_tin_workspace(
        name,
        workspace_name: WorkspaceName,
        base: str,
        crs: QgsCoordinateReferenceSystem,
        subset: str,
        context: Context,
        document_file: Optional[str] = None,
        wkb_type_hint: QgsWkbTypes.Type = QgsWkbTypes.Type.Unknown,
    ) -> DataSourceProperties:
        """
        Convert TinWorkspaceFactory
        """
        folder = ConversionUtils.get_absolute_path(workspace_name.name, base)
        file_name = ConversionUtils.get_absolute_path(name.name, folder) + "/tedg.adf"
        uri = file_name
        provider = "mdal"
        return DataSourceProperties(uri=uri, provider=provider, file_name=file_name)

    @staticmethod
    def convert_las_dataset_workspace(
        name,
        workspace_name: WorkspaceName,
        base: str,
        crs: QgsCoordinateReferenceSystem,
        subset: str,
        context: Context,
        document_file: Optional[str] = None,
        wkb_type_hint: QgsWkbTypes.Type = QgsWkbTypes.Type.Unknown,
    ) -> DataSourceProperties:
        """
        Convert LasDatasetWorkspaceFactory
        """
        folder = ConversionUtils.get_absolute_path(workspace_name.name, base)
        file_name = ConversionUtils.get_absolute_path(name.name, folder)

        uri = file_name
        provider = "pdal"
        return DataSourceProperties(uri=uri, provider=provider, file_name=file_name)

    @staticmethod
    def convert_s57_workspace(
        name,
        workspace_name: WorkspaceName,
        base: str,
        crs: QgsCoordinateReferenceSystem,
        subset: str,
        context: Context,
        document_file: Optional[str] = None,
        wkb_type_hint: QgsWkbTypes.Type = QgsWkbTypes.Type.Unknown,
    ) -> DataSourceProperties:
        """
        Convert S57WorkspaceFactory
        """
        provider = "ogr"
        file_name = ConversionUtils.get_absolute_path(workspace_name.name, base)
        layer_name = name.name
        uri = "{}|layername={}".format(file_name, layer_name)

        if name.__class__.__name__ == "TableName":
            wkb_type = QgsWkbTypes.Type.NoGeometry
        elif name.__class__.__name__ == "FeatureClassName":
            wkb_type = DatasetNameConverter.geometry_type_to_wkb(name.shape_type)
        else:
            assert False

        return DataSourceProperties(
            uri=uri, wkb_type=wkb_type, provider=provider, file_name=file_name
        )

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
            if part2.startswith("."):
                part2 = part2[1:]

            return [part1] + DatasetNameConverter.split_to_tokens(part2)
        else:
            parts_search = re.search(r"^(.*?)\.(.*)$", value, re.IGNORECASE)
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
        if context.sde_table_name_conversion == "lower":
            return name.lower()
        elif context.sde_table_name_conversion == "upper":
            return name.upper()

        return name

    # pylint: disable=too-many-branches,too-many-statements,too-many-locals
    @staticmethod
    def convert_sde_sdc_workspace(
        name,
        workspace_name: WorkspaceName,
        base: str,
        crs: QgsCoordinateReferenceSystem,
        subset: str,
        context: Context,
        is_sdc: bool,
        wkb_type_hint: QgsWkbTypes.Type = QgsWkbTypes.Type.Unknown,
    ) -> DataSourceProperties:
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
                connection = ConnectionConverter.convert_connection(
                    workspace_name.connection_properties, context
                )
            elif sde_path.exists() and not sde_path.is_dir():
                connection = ConnectionConverter.convert_sde_connection(
                    sde_path, context
                )

        # pylint: disable=too-many-nested-blocks
        if connection is not None:
            sde_uri, provider = connection
            # what happens if there's more than one . ???
            if provider == "oracle":
                parts = DatasetNameConverter.split_to_tokens(name.name)
                if len(parts) == 2:
                    sde_uri.setSchema(parts[0])
                    sde_uri.setTable(
                        DatasetNameConverter.convert_sde_table_name(parts[1], context)
                    )
                    if not isinstance(name, TableName):
                        sde_uri.setSrid(str(crs.postgisSrid()))
                        wkb_type = DatasetNameConverter.GEOMETRY_TYPE_TO_WKB_TYPE[
                            name.shape_type
                        ]
                        if (
                            wkb_type
                            in (
                                QgsWkbTypes.Type.Unknown,
                                QgsWkbTypes.Type.GeometryCollection,
                            )
                            and wkb_type_hint != QgsWkbTypes.Type.Unknown
                        ):
                            wkb_type = wkb_type_hint
                        sde_uri.setWkbType(wkb_type)
                        sde_uri.setGeometryColumn(name.shape_field_name)
                    else:
                        sde_uri.setWkbType(QgsWkbTypes.Type.NoGeometry)

                    sde_uri.setSql(subset)
                    sde_uri.setKeyColumn(context.sde_primary_key)

                    uri = sde_uri.uri(False)
                    file_name = None
                else:
                    context.push_warning(
                        f"Could not convert Oracle table name {name.name}. Please email this file to info@north-road.com so that we can add support in a future SLYR release.",
                        level=Context.CRITICAL,
                    )
            elif provider == "mssql":
                schema = None
                table_name = None
                parts = DatasetNameConverter.split_to_tokens(name.name)
                if len(parts) == 3:
                    schema = parts[1]
                    table_name = parts[2]
                elif len(parts) == 2:
                    schema = parts[0]
                    table_name = parts[1]

                if table_name is not None:
                    if schema:
                        sde_uri.setSchema(schema)
                    sde_uri.setTable(
                        DatasetNameConverter.convert_sde_table_name(table_name, context)
                    )

                    if hasattr(name, "query"):
                        query = name.query
                        query_properties = (
                            DatasetNameConverter.extract_details_from_query(
                                query, sde_uri, context
                            )
                        )

                        if query_properties.table:
                            sde_uri.setTable(query_properties.table)
                        if query_properties.schema:
                            sde_uri.setSchema(query_properties.schema)

                        if query_properties.wkb_type is not None:
                            wkb_type = query_properties.wkb_type

                        if query_properties.geometry_column:
                            sde_uri.setGeometryColumn(query_properties.geometry_column)

                        if (
                            query_properties.crs is not None
                            and query_properties.crs.isValid()
                        ):
                            crs = query_properties.crs
                        if wkb_type != QgsWkbTypes.Type.NoGeometry:
                            sde_uri.setSrid(str(crs.postgisSrid()))

                        sde_uri.setWkbType(wkb_type)
                    elif isinstance(name, DBTableName):
                        if name.shape_field_name:
                            sde_uri.setSrid(str(crs.postgisSrid()))
                            wkb_type = DatasetNameConverter.GEOMETRY_TYPE_TO_WKB_TYPE[
                                name.geometry_type
                            ]
                            if (
                                wkb_type
                                in (
                                    QgsWkbTypes.Type.Unknown,
                                    QgsWkbTypes.Type.GeometryCollection,
                                )
                                and wkb_type_hint != QgsWkbTypes.Type.Unknown
                            ):
                                wkb_type = wkb_type_hint
                            sde_uri.setWkbType(wkb_type)
                            sde_uri.setGeometryColumn(name.shape_field_name)
                        else:
                            wkb_type = QgsWkbTypes.Type.NoGeometry
                    elif not isinstance(name, TableName):
                        sde_uri.setSrid(str(crs.postgisSrid()))
                        wkb_type = DatasetNameConverter.GEOMETRY_TYPE_TO_WKB_TYPE[
                            name.shape_type
                        ]
                        if (
                            wkb_type
                            in (
                                QgsWkbTypes.Type.Unknown,
                                QgsWkbTypes.Type.GeometryCollection,
                            )
                            and wkb_type_hint != QgsWkbTypes.Type.Unknown
                        ):
                            wkb_type = wkb_type_hint
                        sde_uri.setWkbType(wkb_type)
                        sde_uri.setGeometryColumn(name.shape_field_name)
                    else:
                        sde_uri.setWkbType(QgsWkbTypes.Type.NoGeometry)

                    if subset:
                        sde_uri.setSql(subset)
                    sde_uri.setKeyColumn(context.sde_primary_key)

                    if wkb_type != QgsWkbTypes.Type.NoGeometry:
                        sde_uri.setParam("disableInvalidGeometryHandling", "0")

                    if context.ignore_online_sources:
                        sde_uri.setParam("timeout", "1")
                    uri = sde_uri.uri(False)
                    file_name = None
                else:
                    context.push_warning(
                        f"Could not convert SQL Server table name {name.name}. Please email this file to info@north-road.com so that we can add support in a future SLYR release.",
                        level=Context.CRITICAL,
                    )
            elif provider == "postgres":
                parts = DatasetNameConverter.split_to_tokens(name.name)
                if len(parts) == 3:
                    sde_uri.setSchema(parts[1])
                    table_name = parts[2]
                    if table_name.startswith("%"):
                        table_name = table_name[1:]

                    sde_uri.setTable(
                        DatasetNameConverter.convert_sde_table_name(table_name, context)
                    )

                    if hasattr(name, "query"):
                        query = name.query
                        query_properties = (
                            DatasetNameConverter.extract_details_from_query(
                                query, sde_uri, context
                            )
                        )

                        if query_properties.table:
                            sde_uri.setTable(query_properties.table)
                        if query_properties.schema:
                            sde_uri.setSchema(query_properties.schema)

                        if query_properties.wkb_type is not None:
                            wkb_type = query_properties.wkb_type

                        if query_properties.geometry_column:
                            sde_uri.setGeometryColumn(query_properties.geometry_column)

                        if (
                            query_properties.crs is not None
                            and query_properties.crs.isValid()
                        ):
                            crs = query_properties.crs
                        if wkb_type != QgsWkbTypes.Type.NoGeometry:
                            sde_uri.setSrid(str(crs.postgisSrid()))

                        sde_uri.setWkbType(wkb_type)
                    elif not isinstance(name, TableName):
                        sde_uri.setSrid(str(crs.postgisSrid()))
                        wkb_type = DatasetNameConverter.GEOMETRY_TYPE_TO_WKB_TYPE[
                            name.shape_type
                        ]
                        if (
                            wkb_type
                            in (
                                QgsWkbTypes.Type.Unknown,
                                QgsWkbTypes.Type.GeometryCollection,
                            )
                            and wkb_type_hint != QgsWkbTypes.Type.Unknown
                        ):
                            wkb_type = wkb_type_hint
                        sde_uri.setWkbType(wkb_type)
                        sde_uri.setGeometryColumn(name.shape_field_name)
                    else:
                        sde_uri.setWkbType(QgsWkbTypes.Type.NoGeometry)

                    sde_uri.setSql(subset)
                    sde_uri.setKeyColumn(context.sde_primary_key)

                    uri = sde_uri.uri(False)
                    file_name = None
                else:
                    context.push_warning(
                        f"Could not convert PostgreSQL table name {name.name}. Please email this file to info@north-road.com so that we can add support in a future SLYR release.",
                        level=Context.CRITICAL,
                    )
        else:
            provider = "ogr"
            if name.__class__.__name__ in ("DBTableName", "TableName"):
                wkb_type = QgsWkbTypes.Type.NoGeometry
            else:
                wkb_type = DatasetNameConverter.geometry_type_to_wkb(name.shape_type)
            if not is_sdc:
                uri = "{}|layername={}".format(file_name, name.name)
            else:
                file_name = ConversionUtils.get_absolute_path(name.name, file_name)
                uri = file_name
        # pylint: enable=too-many-nested-blocks

        if context.ignore_online_sources:
            provider = "skipped"

        return DataSourceProperties(
            uri=uri, wkb_type=wkb_type, provider=provider, file_name=file_name
        )

    @staticmethod
    def extract_details_from_query(
        query: GpkgFeatureClassQuery, sde_uri, context: Context
    ) -> QueryProperties:
        """
        Extracts relevant details from a query
        """
        res = QueryProperties()

        # try to get table name from query
        sql_query = query.query
        if sql_query:
            table_name_search = re.search(
                r"from ((?:[a-zA-Z][a-zA-Z0-9_]*\.?)+)\b", sql_query, re.IGNORECASE
            )
            if table_name_search:
                schema_search = re.search(r"^(.+)\.(.*?)$", table_name_search.group(1))
                if schema_search:
                    schema = schema_search.group(1)
                    if schema.startswith(sde_uri.database() + "."):
                        schema = schema[len(sde_uri.database() + ".") :]
                    res.table = schema_search.group(2)
                    res.schema = schema
                else:
                    res.table = table_name_search.group(1)
                    res.schema = ""
        geometry_field = query.geometry_field
        if geometry_field:
            geometry_field_info = [
                f for f in query.fields.fields if f.name == geometry_field
            ][0]
            geometry_definition = geometry_field_info.geometry_def

            res.crs = CrsConverter.convert_crs(query.crs, context)
            res.wkb_type = DatasetNameConverter.GEOMETRY_TYPE_TO_WKB_TYPE[
                geometry_definition.geometry_type
            ]
            res.geometry_column = geometry_field
        else:
            res.wkb_type = QgsWkbTypes.Type.NoGeometry
        return res

    # pylint: enable=too-many-branches,too-many-statements,too-many-locals

    @staticmethod
    def convert_sde_workspace(
        name,
        workspace_name: WorkspaceName,
        base: str,
        crs: QgsCoordinateReferenceSystem,
        subset: str,
        context: Context,
        document_file: Optional[str] = None,
        wkb_type_hint: QgsWkbTypes.Type = QgsWkbTypes.Type.Unknown,
    ) -> DataSourceProperties:
        """
        Convert SdeWorkspaceFactory
        """
        return DatasetNameConverter.convert_sde_sdc_workspace(
            name,
            workspace_name,
            base,
            crs,
            subset,
            context,
            False,
            wkb_type_hint=wkb_type_hint,
        )

    @staticmethod
    def convert_sdc_workspace(
        name,
        workspace_name: WorkspaceName,
        base: str,
        crs: QgsCoordinateReferenceSystem,
        subset: str,
        context: Context,
        document_file: Optional[str] = None,
        wkb_type_hint: QgsWkbTypes.Type = QgsWkbTypes.Type.Unknown,
    ) -> DataSourceProperties:
        """
        Convert SdcWorkspaceFactory
        """
        return DatasetNameConverter.convert_sde_sdc_workspace(
            name,
            workspace_name,
            base,
            crs,
            subset,
            context,
            True,
            wkb_type_hint=wkb_type_hint,
        )

    @staticmethod
    def convert_fme_workspace(
        name,
        workspace_name: WorkspaceName,
        base: str,
        crs: QgsCoordinateReferenceSystem,
        subset: str,
        context: Context,
        document_file: Optional[str] = None,
        wkb_type_hint: QgsWkbTypes.Type = QgsWkbTypes.Type.Unknown,
    ) -> DataSourceProperties:
        """
        Convert FMEWorkspaceFactory
        """
        context.push_warning(
            "Converting Data Interoperability connections requires the licensed version of SLYR",
            level=context.CRITICAL,
        )
        return DataSourceProperties()

    @staticmethod
    def convert_street_map_workspace(
        name,
        workspace_name: WorkspaceName,
        base: str,
        crs: QgsCoordinateReferenceSystem,
        subset: str,
        context: Context,
        document_file: Optional[str] = None,
        wkb_type_hint: QgsWkbTypes.Type = QgsWkbTypes.Type.Unknown,
    ) -> DataSourceProperties:
        """
        Convert StreetMapWorkspaceFactory
        """
        context.push_warning(
            "Street map data sources are not supported in QGIS", level=Context.WARNING
        )

        folder = ConversionUtils.get_absolute_path(workspace_name.name, base)
        file_name = ConversionUtils.get_absolute_path(name.name, folder)
        uri = file_name
        provider = "ogr"
        wkb_type = DatasetNameConverter.geometry_type_to_wkb(name.shape_type)

        return DataSourceProperties(
            uri=uri, provider=provider, file_name=file_name, wkb_type=wkb_type
        )

    # pylint: enable=unused-argument

    @staticmethod
    def convert(
        name,
        base: str,
        crs: QgsCoordinateReferenceSystem,
        context: Context,
        subset: Optional[str] = None,
        document_file: Optional[str] = None,
        wkb_type_hint: QgsWkbTypes.Type = QgsWkbTypes.Type.Unknown,
    ) -> DataSourceProperties:
        """
        Converts a data source name to qgis data source components
        """

        # special handling
        if name.__class__.__name__ == "RelQueryTableName":
            # this is a special beast -- we need to handle this elsewhere!
            return DataSourceProperties(
                uri="temp", provider="ogr", wkb_type=QgsWkbTypes.Type.Unknown
            )
        elif name.__class__.__name__ == "RouteEventSourceName":
            context.push_warning(
                "Route event sources are not supported in QGIS, layer has been converted to a simple layer",
                level=Context.CRITICAL,
            )

            # get the line feature name from RouteMeasureLocatorName
            return DatasetNameConverter.convert(
                name.dataset_name.dataset_name,
                base,
                crs,
                context,
                subset,
                document_file=document_file,
                wkb_type_hint=wkb_type_hint,
            )

        # the logic here looks like this:
        # - we first need to find the workspace name object
        # - this can be buried any number of levels deep though...!
        # - when we've found the workspace name, we can get the workspace factory
        #   as that tells us what the actual type of dataset we are working with is

        def find_workspace_name(obj) -> Optional[WorkspaceName]:
            if hasattr(obj, "workspace_name") and isinstance(
                obj.workspace_name, WorkspaceName
            ):
                return obj.workspace_name

            elif hasattr(obj, "dataset_name") and isinstance(
                obj.dataset_name, WorkspaceName
            ):
                return obj.dataset_name

            elif hasattr(obj, "dataset_name"):
                return find_workspace_name(obj.dataset_name)

            elif hasattr(obj, "feature_dataset_name"):
                return find_workspace_name(obj.feature_dataset_name)

            return None

        workspace_name = find_workspace_name(name)
        factory = workspace_name.workspace_factory if workspace_name else None

        if name.__class__.__name__ == "XYEventSourceName":
            # if the file is a txt file then we can use the delimited text provider to read it
            if not factory or factory.__class__.__name__ != "TextFileWorkspaceFactory":
                # We can't directly map these -- best we can do is try to get the original file
                if hasattr(name.feature_dataset_name, "datasource_type"):
                    datasource_type = name.feature_dataset_name.datasource_type
                    context.push_warning(
                        "XY event sources from {} are not supported in QGIS, layer has been converted to a non-spatial table".format(
                            datasource_type
                        ),
                        level=Context.CRITICAL,
                    )
                elif workspace_name:
                    context.push_warning(
                        "XY event sources from {} are not supported in QGIS, layer has been converted to a non-spatial table".format(
                            workspace_name.name
                        ),
                        level=Context.CRITICAL,
                    )
                else:
                    context.push_warning(
                        "XY event sources from this layer type are not supported in QGIS, layer has been converted to a non-spatial table",
                        level=Context.CRITICAL,
                    )

                # get the line feature name from XYEventSourceName
                name = name.feature_dataset_name
                return DatasetNameConverter.convert(
                    name,
                    base,
                    crs,
                    context,
                    subset,
                    document_file=document_file,
                    wkb_type_hint=wkb_type_hint,
                )

        FACTORY_MAP = {
            "FileGDBWorkspaceFactory": DatasetNameConverter.convert_file_gdb_workspace,
            "ShapefileWorkspaceFactory": DatasetNameConverter.convert_shapefile_workspace,
            "AccessWorkspaceFactory": DatasetNameConverter.convert_access_workspace,
            "CadWorkspaceFactory": DatasetNameConverter.convert_cad_workspace,
            "NetCDFWorkspaceFactory": DatasetNameConverter.convert_netcdf_workspace,
            "GpkgWorkspaceFactory": DatasetNameConverter.convert_gpkg_workspace,
            "ArcInfoWorkspaceFactory": DatasetNameConverter.convert_arcinfo_workspace,
            "ExcelOrMdbWorkspaceFactory": DatasetNameConverter.convert_excel_or_mdb_workspace,
            "OLEDBWorkspaceFactory": DatasetNameConverter.convert_oledb_workspace,
            "TextFileWorkspaceFactory": DatasetNameConverter.convert_text_file_workspace,
            "FeatureServiceWorkspaceFactory": DatasetNameConverter.convert_feature_service_workspace,
            "TinWorkspaceFactory": DatasetNameConverter.convert_tin_workspace,
            "LasDatasetWorkspaceFactory": DatasetNameConverter.convert_las_dataset_workspace,
            "SdeWorkspaceFactory": DatasetNameConverter.convert_sde_workspace,
            "SdcWorkspaceFactory": DatasetNameConverter.convert_sdc_workspace,
            "S57WorkspaceFactory": DatasetNameConverter.convert_s57_workspace,
            "FMEWorkspaceFactory": DatasetNameConverter.convert_fme_workspace,
            "StreetMapWorkspaceFactory": DatasetNameConverter.convert_street_map_workspace,
            "IMSWorkspaceFactory": DatasetNameConverter.convert_ims_workspace,
        }

        conversion_function = FACTORY_MAP.get(factory.__class__.__name__)
        if not conversion_function:
            print(name.to_dict())

        assert conversion_function

        res = conversion_function(
            name,
            workspace_name,
            base,
            crs,
            subset,
            context,
            document_file,
            wkb_type_hint,
        )
        res.factory = factory
        context.dataset_name = name.name
        return res

    @staticmethod
    def dataset_name_to_wkb_type(name) -> QgsWkbTypes.Type:
        """
        Determines a WKB type from a dataset name
        """
        if name.__class__.__name__ == "XYEventSourceName":
            return QgsWkbTypes.Type.Point
        elif not hasattr(name, "shape_type"):
            return QgsWkbTypes.Type.Unknown
        elif name.shape_type == 0:
            # not stored
            return QgsWkbTypes.Type.Unknown
        return DatasetNameConverter.geometry_type_to_wkb(name.shape_type)

    @staticmethod
    def geometry_type_to_wkb(geometry_type) -> QgsWkbTypes.Type:
        """
        Converts ESRI geometry type to QGIS wkb type
        """
        GEOMETRY_TYPES = {
            0: QgsWkbTypes.Type.NoGeometry,
            1: QgsWkbTypes.Type.Point,
            2: QgsWkbTypes.Type.MultiPoint,
            3: QgsWkbTypes.Type.MultiLineString,
            4: QgsWkbTypes.Type.MultiPolygon,
            5: QgsWkbTypes.Type.MultiPolygon,
            6: QgsWkbTypes.Type.MultiLineString,
            7: QgsWkbTypes.Type.Unknown,
            9: QgsWkbTypes.Type.MultiPolygon,
            11: QgsWkbTypes.Type.MultiLineString,
            13: QgsWkbTypes.Type.MultiLineString,
            14: QgsWkbTypes.Type.CircularString,
            15: QgsWkbTypes.Type.Unknown,
            16: QgsWkbTypes.Type.Unknown,
            17: QgsWkbTypes.Type.Unknown,
            18: QgsWkbTypes.Type.Unknown,
            19: QgsWkbTypes.Type.Unknown,
            20: QgsWkbTypes.Type.Unknown,
            21: QgsWkbTypes.Type.Unknown,
            22: QgsWkbTypes.Type.Unknown,
        }
        return GEOMETRY_TYPES[geometry_type]

    GEOMETRY_TYPE_TO_WKB_TYPE = {
        0: QgsWkbTypes.Type.NoGeometry,
        1: QgsWkbTypes.Type.Point,
        2: QgsWkbTypes.Type.MultiPoint,
        3: QgsWkbTypes.Type.LineString,
        4: QgsWkbTypes.Type.Polygon,
        5: QgsWkbTypes.Type.Polygon,
        6: QgsWkbTypes.Type.LineString,
        7: QgsWkbTypes.Type.GeometryCollection,  # 'GEOMETRY_ANY',
        9: None,  # 'GEOMETRY_MULTIPATCH',
        11: QgsWkbTypes.Type.LineString,
        13: QgsWkbTypes.Type.LineString,
        14: QgsWkbTypes.Type.CircularString,
        15: QgsWkbTypes.Type.LineString,
        16: QgsWkbTypes.Type.LineString,
        17: None,  # 'GEOMETRY_BAG',
        18: None,  # 'GEOMETRY_TRIANGLE_STRIP',
        19: None,  # 'GEOMETRY_TRIANGLE_FAN',
        20: None,  # 'GEOMETRY_RAY',
        21: None,  # 'GEOMETRY_SPHERE',
        22: None,  # 'GEOMETRY_TRIANGLES',
    }
