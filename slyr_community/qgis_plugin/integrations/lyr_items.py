"""
Browser and app integrations for LYR/lyrx file integration with QGIS
"""

# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

import html
import os
from io import BytesIO
from pathlib import Path
from struct import unpack

from qgis.PyQt.QtCore import QFileInfo, QDir, QCoreApplication
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from qgis.core import (
    Qgis,
    QgsDataItem,
    QgsMimeDataUtils,
    QgsStyle,
    QgsSymbol,
    QgsColorRamp,
    QgsProject,
    QgsWkbTypes,
    QgsCoordinateReferenceSystem,
    QgsDataCollectionItem,
    QgsLayerItem,
    QgsTextFormat,
)
from qgis.gui import QgsCustomDropHandler, QgsStyleManagerDialog
from qgis.utils import iface

from .browser_utils import BrowserUtils
from ..gui_utils import GuiUtils
from ...converters.context import Context
from ...converters.layers import LayerConverter
from ...converters.vector_layer import VectorLayerConverter
from ...converters.vector_renderer import VectorRendererConverter

from ...parser.exceptions import (
    UnreadableSymbolException,
    UnsupportedVersionException,
    NotImplementedException,
    UnknownClsidException,
    UnreadablePictureException,
    CorruptDocumentException,
)

from ...parser.exceptions import RequiresLicenseException
from ...parser.objects.base_map_layer import BaseMapLayer
from ...parser.objects.feature_layer import FeatureLayer
from ...parser.objects.group_layer import GroupLayer
from ...parser.stream import Stream

from qgis.core import QgsErrorItem


class LyrDropHandler(QgsCustomDropHandler):
    """
    .avl/.lyr/.lyrx file drop handler
    """

    def handleFileDrop(self, file):  # pylint: disable=missing-docstring
        if file.lower().endswith(".lyr"):
            self.open_lyr(file)
            return True
        elif file.lower().endswith(".lyrx"):
            self.open_lyrx(file)
            return True
        elif file.lower().endswith(".avl"):
            self.open_avl(file)
            return True

        return False

    def canHandleMimeData(self, data):  # pylint: disable=missing-function-docstring
        return data.hasFormat('application/x-qt-windows-mime;value="ESRI Layers"')

    def handleMimeDataV2(self, data):  # pylint: disable=missing-function-docstring
        if data.hasFormat('application/x-qt-windows-mime;value="ESRI Layers"'):
            byte_array = data.data('application/x-qt-windows-mime;value="ESRI Layers"')
            mime_data = byte_array.data()
            mime_binary = BytesIO(mime_data)

            count = unpack("<L", mime_binary.read(4))[0]
            offset = mime_binary.tell()
            try:
                stream = Stream(
                    mime_binary,
                    False,
                    force_layer=True,
                    offset=offset,
                    extract_doc_structure=False,
                )

                for _ in range(count):
                    LyrDropHandler.open_lyr_stream(stream)

                return True
            except UnreadableSymbolException:
                pass
            except NotImplementedException:
                pass
            except UnsupportedVersionException:
                pass
            except UnknownClsidException:
                pass
            except UnreadablePictureException:
                pass

        return False

    @staticmethod
    def open_lyr_stream(stream, input_file=""):  # pylint:disable=too-many-statements
        """
        Opens a lyr file from a binary object
        """

        # maybe we should create a cache of unknown crs properties to selected crs?
        fallback_crs = QgsCoordinateReferenceSystem()

        warnings = set()
        errors = set()
        info = set()

        def unsupported_object_callback(msg, level=Context.WARNING):
            if level == Context.WARNING:
                warnings.add(msg)
            elif level == Context.CRITICAL:
                errors.add(msg)
            elif level == Context.INFO:
                info.add(msg)

        context = Context()
        context.project = QgsProject.instance()
        context.can_place_annotations_in_main_annotation_layer = False
        context.unsupported_object_callback = unsupported_object_callback

        def add_layer(layer, group_node):
            nonlocal fallback_crs
            layers = LayerConverter.layer_to_QgsLayer(
                layer, input_file, context, fallback_crs
            )
            for _layer in layers:
                if not fallback_crs.isValid() and _layer.crs().isValid():
                    fallback_crs = _layer.crs()
                QgsProject.instance().addMapLayer(_layer, False)

                if _layer.customProperty("_slyr_group_name"):
                    new_group_name = _layer.customProperty("_slyr_group_name")
                    child_group = group_node.findGroup(new_group_name)
                    if not child_group:
                        child_group = group_node.addGroup(new_group_name)
                        child_group.setExpanded(
                            _layer.customProperty("_slyr_group_expanded")
                        )
                        child_group.setItemVisibilityChecked(
                            _layer.customProperty("_slyr_group_visible")
                        )
                    node = child_group.addLayer(_layer)
                    _layer.removeCustomProperty("_slyr_group_name")
                    _layer.removeCustomProperty("_slyr_group_expanded")
                    _layer.removeCustomProperty("_slyr_group_visible")
                else:
                    node = group_node.addLayer(_layer)

                if not layer.visible or _layer.customProperty("_slyr_hidden_layer"):
                    _layer.removeCustomProperty("_slyr_hidden_layer")
                    node.setItemVisibilityChecked(False)
                if hasattr(layer, "renderer") and hasattr(
                    layer.renderer, "legend_group"
                ):
                    node.setExpanded(layer.renderer.legend_group.editable_or_expanded)
                elif len(node.children()) > 10:
                    node.setExpanded(False)
            return layers

        def add_group(group, parent):
            group_node = parent.addGroup(group.name)
            group_layers = []
            for c in group.children:
                if isinstance(c, (GroupLayer, BaseMapLayer)):
                    add_group(c, group_node)
                else:
                    group_layers.extend(add_layer(c, group_node))
            if not group.visible:
                group_node.setItemVisibilityChecked(False)
                group_node.setExpanded(group.expanded)

            if (group.transparency or 0) and Qgis.QGIS_VERSION_INT >= 32400:
                from qgis.core import QgsGroupLayer

                options = QgsGroupLayer.LayerOptions(
                    QgsProject.instance().transformContext()
                )
                group_layer = group_node.convertToGroupLayer(options)
                group_layer.setOpacity(1 - group.transparency / 100)
                QgsProject.instance().addMapLayer(group_layer, False)

        obj = stream.read_object()

        if LayerConverter.is_layer(obj):
            add_layer(obj, QgsProject.instance().layerTreeRoot())
        elif LayerConverter.is_group(obj):
            add_group(obj, QgsProject.instance().layerTreeRoot())
        else:
            iface.messageBar().pushCritical(
                "SLYR", "{} layers are not yet supported".format(obj.__class__.__name__)
            )
            return True

        if warnings or errors or info:
            message = ""
            title = ""
            level = None

            if errors:
                message = "<p>The following errors were generated while converting the LYR file:</p>"
                message += "<ul>"
                for w in errors:
                    message += "<li>{}</li>".format(
                        html.escape(w).replace("\n", "<br>")
                    )
                message += "</ul>"
                title = "LYR could not be completely converted"
                level = Qgis.MessageLevel.Critical
            if warnings:
                if message:
                    message += "<p>Additionally, some warnings were generated:</p>"
                else:
                    message += "<p>The following warnings were generated while converting the LYR file:</p>"
                message += "<ul>"
                for w in warnings:
                    message += "<li>{}</li>".format(
                        html.escape(w).replace("\n", "<br>")
                    )
                message += "</ul>"
                if not title:
                    title = "LYR could not be completely converted"
                if level is None:
                    level = Qgis.MessageLevel.Warning

            if info:
                if message:
                    message += (
                        "<p>Additionally, some extra messages were generated:</p>"
                    )
                else:
                    message += "<p>The following information messages were generated converting the LYR file:</p>"
                message += "<ul>"
                for w in info:
                    message += "<li>{}</li>".format(
                        html.escape(w).replace("\n", "<br>")
                    )
                message += "</ul>"
                if not title:
                    title = "Some messages were generated while converting LYR"
                if level is None:
                    level = Qgis.MessageLevel.Info

            BrowserUtils.show_warning(title, "Convert LYR", message, level=level)

        return True

    @staticmethod
    def open_lyr(input_file):
        """
        Opens a LYR file in the current project
        """

        with open(input_file, "rb") as f:
            try:
                stream = Stream(f, False, force_layer=True)
                return LyrDropHandler.open_lyr_stream(stream, input_file)
            except RequiresLicenseException as e:
                message = '<p>{}. Please see <a href="https://north-road.com/slyr/">here</a> for details.</p>'.format(
                    e
                )
                BrowserUtils.show_warning(
                    "Licensed version required",
                    "Convert LYR",
                    message,
                    level=Qgis.Critical,
                )
                return True

    @staticmethod
    def open_lyrx(input_file):  # pylint: disable=too-many-locals,too-many-statements
        """
        Opens a LYRX file in the current project
        """
        message = '<p>This functionality requires the licensed version of SLYR. Please see <a href="https://north-road.com/slyr/">here</a> for details.</p>'
        BrowserUtils.show_warning(
            "Licensed version required",
            "Convert LYRX",
            message,
            level=Qgis.Critical,
            message_bar=iface.messageBar(),
        )
        return True

    @staticmethod
    def open_avl(input_file):
        """
        Opens an AVL file in the current project
        """
        message = '<p>This functionality requires the licensed version of SLYR. Please see <a href="https://north-road.com/slyr/">here</a> for details.</p>'
        BrowserUtils.show_warning(
            "Licensed version required",
            "Convert LYRX",
            message,
            level=Qgis.Critical,
            message_bar=iface.messageBar(),
        )
        return True

    def customUriProviderKey(self):  # pylint: disable=missing-docstring
        return "esri_lyr"

    def handleCustomUriDrop(self, uri):  # pylint: disable=missing-docstring
        path = uri.uri
        if path.lower().endswith(".lyrx"):
            self.open_lyrx(path)
        elif path.lower().endswith(".avl"):
            self.open_avl(path)
        else:
            self.open_lyr(path)


class EsriLyrItem(QgsDataItem):
    """
    Data item for .avl/.lyr/.lyrx files
    """

    def __init__(
        self, parent, name, path, lyr_object=None, layer_path="", definitions=None
    ):
        super().__init__(QgsDataItem.Type.Custom, parent, name, path)
        if path and path.lower().endswith(".avl"):
            self.setCapabilities(QgsDataItem.Capability.Collapse)
            self.setState(QgsDataItem.State.Populated)
        else:
            self.setCapabilities(
                QgsDataItem.Capability.Fertile | QgsDataItem.Capability.Collapse
            )
        self.layer_path = layer_path or path
        self.object = lyr_object
        self.definitions = definitions
        if path:
            self.setIcon(GuiUtils.get_icon("icon.svg"))
        elif isinstance(self.object, (GroupLayer, BaseMapLayer)):
            self.setIcon(QgsDataCollectionItem.iconDir())
        elif self.object.__class__.__name__ in ("WmsMapLayer", "RasterLayer"):
            self.setIcon(QgsLayerItem.iconRaster())
        else:
            wkb_type = VectorLayerConverter.layer_to_wkb_type(self.object)
            geometry_type = QgsWkbTypes.geometryType(wkb_type)
            if geometry_type == QgsWkbTypes.GeometryType.PointGeometry:
                self.setIcon(QgsLayerItem.iconPoint())
            elif geometry_type == QgsWkbTypes.GeometryType.LineGeometry:
                self.setIcon(QgsLayerItem.iconLine())
            elif geometry_type == QgsWkbTypes.GeometryType.PolygonGeometry:
                self.setIcon(QgsLayerItem.iconPolygon())
            else:
                self.setIcon(QgsLayerItem.iconDefault())

        if self.object:
            if isinstance(self.object, (GroupLayer, BaseMapLayer)):
                self.add_children()
            self.setState(QgsDataItem.State.Populated)
        self.setToolTip(
            QDir.toNativeSeparators(path) if not lyr_object else lyr_object.name
        )
        self.child_items = []

    def hasDragEnabled(self):  # pylint: disable=missing-docstring
        return True

    def handleDoubleClick(self):  # pylint: disable=missing-docstring
        if self.path():
            self.open_lyr()
        else:
            self.open_object()
        return True

    def add_children(self):
        """
        Adds a child data item from the LYR
        """
        if self.definitions:
            for uri in self.object.layers:
                definitions = [
                    definition
                    for definition in self.definitions
                    if definition.uri == uri
                ]
                assert len(definitions) == 1

                definition = definitions[0]
                self.addChildItem(
                    EsriLyrItem(
                        self,
                        definition.name,
                        "",
                        definition,
                        self.layer_path,
                        definitions=self.definitions,
                    )
                )
        else:
            for c in self.object.children:
                self.addChildItem(EsriLyrItem(self, c.name, "", c, self.layer_path))

    def createChildren(self):  # pylint: disable=missing-function-docstring
        # Runs in a thread!

        if self.path().lower().endswith(".avl"):
            return []

        self.setState(QgsDataItem.State.Populating)
        if not self.object:
            with open(self.path(), "rb") as f:
                try:
                    stream = Stream(f, False, force_layer=True, offset=0)
                    self.object = stream.read_object()
                except RequiresLicenseException as e:
                    error_item = QgsErrorItem(self, str(e), self.path() + "/error")
                    self.child_items.append(error_item)
                    return self.child_items

        def add_layer(layer):
            self.child_items.append(
                EsriLyrItem(self, layer.name, "", layer, self.path())
            )

        def add_group(group):
            self.child_items.append(
                EsriLyrItem(self, group.name, "", group, self.path())
            )

        if LayerConverter.is_layer(self.object):
            add_layer(self.object)
        else:
            add_group(self.object)
        self.setState(QgsDataItem.State.Populated)
        return self.child_items

    def mimeUri(self):  # pylint: disable=missing-docstring
        u = QgsMimeDataUtils.Uri()
        u.layerType = "custom"
        u.providerKey = "esri_lyr"
        u.name = self.name()
        u.uri = self.layer_path
        return u

    def mimeUris(self):  # pylint: disable=missing-docstring
        return [self.mimeUri()]

    def open_lyr(self):
        """
        Handles opening .lyr files
        """

        if self.path().lower().endswith(".lyrx"):
            LyrDropHandler.open_lyrx(self.path())
            return True
        elif self.path().lower().endswith(".avl"):
            LyrDropHandler.open_avl(self.path())
            return True
        else:
            return LyrDropHandler.open_lyr(self.path())

    def open_object(self):
        """
        Opens a LYR or sublayer from a LYR file
        """

        fallback_crs = QgsCoordinateReferenceSystem()

        context = Context()
        context.project = QgsProject.instance()

        def add_layer(layer, group_node):
            nonlocal fallback_crs
            layers = LayerConverter.layer_to_QgsLayer(
                layer, self.layer_path, context, fallback_crs
            )
            for _layer in layers:
                if not fallback_crs.isValid() and _layer.crs().isValid():
                    fallback_crs = _layer.crs()
                QgsProject.instance().addMapLayer(_layer, False)

                if _layer.customProperty("_slyr_group_name"):
                    new_group_name = _layer.customProperty("_slyr_group_name")
                    child_group = group_node.findGroup(new_group_name)
                    if not child_group:
                        child_group = group_node.addGroup(new_group_name)
                        child_group.setExpanded(
                            _layer.customProperty("_slyr_group_expanded")
                        )
                        child_group.setItemVisibilityChecked(
                            _layer.customProperty("_slyr_group_visible")
                        )
                    node = child_group.addLayer(_layer)
                    _layer.removeCustomProperty("_slyr_group_name")
                    _layer.removeCustomProperty("_slyr_group_expanded")
                    _layer.removeCustomProperty("_slyr_group_visible")
                else:
                    node = group_node.addLayer(_layer)

                if not layer.visible or _layer.customProperty("_slyr_hidden_layer"):
                    _layer.removeCustomProperty("_slyr_hidden_layer")
                    node.setItemVisibilityChecked(False)
                if hasattr(layer, "renderer") and hasattr(
                    layer.renderer, "legend_group"
                ):
                    node.setExpanded(layer.renderer.legend_group.editable_or_expanded)
                elif len(node.children()) > 10:
                    node.setExpanded(False)

        def add_group(group, parent):
            group_node = parent.addGroup(group.name)

            for c in group.children:
                if isinstance(c, (GroupLayer, BaseMapLayer)):
                    add_group(c, group_node)
                else:
                    add_layer(c, group_node)

        if isinstance(self.object, (GroupLayer, BaseMapLayer)):
            add_group(self.object, QgsProject.instance().layerTreeRoot())
        else:
            add_layer(self.object, QgsProject.instance().layerTreeRoot())

        return True

    def extract_symbols(self):
        """
        Extract symbols from a lyr file
        """

        style = QgsStyle()
        style.createMemoryDatabase()

        context = Context()
        context.project = QgsProject.instance()

        with open(self.path(), "rb") as f:
            try:
                stream = Stream(f, False, force_layer=True, offset=-1)
                root_object = stream.read_object()
            except RequiresLicenseException as e:
                message = '<p>{}. Please see <a href="https://north-road.com/slyr/">here</a> for details.</p>'.format(
                    e
                )
                BrowserUtils.show_warning(
                    "Licensed version required",
                    "Convert LYR",
                    message,
                    level=Qgis.Critical,
                )
                return True

        layers = LayerConverter.unique_layer_name_map(root_object)

        for name, layer in layers.items():
            if not isinstance(layer, FeatureLayer):
                continue

            symbols = VectorRendererConverter.extract_symbols_from_renderer(
                layer,
                context,
                default_name=name,
                base_name=name if len(layers) > 1 else "",
            )

            for k, v in symbols.items():
                if isinstance(v, QgsSymbol):
                    style.addSymbol(k, v, True)
                elif isinstance(v, QgsColorRamp):
                    style.addColorRamp(k, v, True)
                elif isinstance(v, QgsTextFormat):
                    style.addTextFormat(k, v, True)

        dlg = QgsStyleManagerDialog(style, readOnly=True)
        dlg.setFavoritesGroupVisible(False)
        dlg.setSmartGroupsVisible(False)
        fi = QFileInfo(self.path())
        dlg.setBaseStyleName(fi.baseName())
        dlg.setWindowTitle(fi.baseName())
        dlg.exec()
        return True

    def save_as_qlr(self):
        """
        Saves the lyr as a QLR file
        """

        if not self.object:
            with open(self.path(), "rb") as f:
                try:
                    stream = Stream(f, False, force_layer=True, offset=0)
                    self.object = stream.read_object()
                except RequiresLicenseException as e:
                    message = '<p>{}. Please see <a href="https://north-road.com/slyr/">here</a> for details.</p>'.format(
                        e
                    )
                    BrowserUtils.show_warning(
                        "Licensed version required",
                        "Convert LYR",
                        message,
                        level=Qgis.Critical,
                    )
                    return True

        input_path = self.path() or self.layer_path
        input_folder, base = os.path.split(input_path)
        base, _ = os.path.splitext(self.name())
        default_name = os.path.join(input_folder, base + ".qlr")

        dest_path, _ = QFileDialog.getSaveFileName(
            None, "Save as QLR", default_name, "QLR files (*.qlr *.QLR)"
        )
        if dest_path:
            context = Context()
            context.project = QgsProject.instance()
            context.can_place_annotations_in_main_annotation_layer = False
            res, error = LayerConverter.object_to_qlr(
                self.object,
                input_path,
                dest_path,
                context,
                definitions=self.definitions,
            )
            if not res:
                iface.messageBar().pushMessage(
                    "Save as QLR", error, Qgis.MessageLevel.Critical
                )

        return True

    def save_as_qml(self):
        """
        Saves the lyr as a QML file
        """

        if not self.object:
            with open(self.path(), "rb") as f:
                try:
                    stream = Stream(f, False, force_layer=True, offset=0)
                    self.object = stream.read_object()
                except RequiresLicenseException as e:
                    message = '<p>{}. Please see <a href="https://north-road.com/slyr/">here</a> for details.</p>'.format(
                        e
                    )
                    BrowserUtils.show_warning(
                        "Licensed version required",
                        "Convert LYR",
                        message,
                        level=Qgis.Critical,
                    )
                    return True

        input_path = self.path() or self.layer_path
        input_folder, base = os.path.split(input_path)
        base, _ = os.path.splitext(self.name())
        default_name = os.path.join(input_folder, base + ".qml")

        errors = []

        def on_error(error):
            nonlocal errors
            errors.append(error)
            iface.messageBar().pushMessage(
                "Save as QML", error, Qgis.MessageLevel.Critical
            )

        dest_path, _ = QFileDialog.getSaveFileName(
            None, "Save as QML", default_name, "QML files (*.qml *.QML)"
        )
        if dest_path:
            context = Context()
            context.project = QgsProject.instance()
            context.can_place_annotations_in_main_annotation_layer = False
            LayerConverter.layers_to_qml(
                self.object,
                input_path,
                dest_path,
                context=context,
                on_error=on_error,
                definitions=self.definitions,
            )

        if not errors:
            iface.messageBar().pushMessage(
                "Save as QML",
                "Saved to {}".format(dest_path),
                Qgis.MessageLevel.Success,
            )

        return True

    def actions(self, parent):  # pylint: disable=missing-docstring
        save_as_qlr_action = QAction(
            QCoreApplication.translate("SLYR", "Save as &QLR…"), parent
        )
        save_as_qlr_action.triggered.connect(self.save_as_qlr)
        if self.path():
            open_action = QAction(
                QCoreApplication.translate("SLYR", "&Add Layer(s)"), parent
            )
            open_action.triggered.connect(self.open_lyr)
            if not self.path().lower().endswith(".avl"):
                save_as_qml_action = QAction(
                    QCoreApplication.translate("SLYR", "Save as QML…"), parent
                )
                save_as_qml_action.triggered.connect(self.save_as_qml)
                extract_symbols_action = QAction(
                    QCoreApplication.translate("SLYR", "&Extract Symbols…"), parent
                )
                extract_symbols_action.triggered.connect(self.extract_symbols)
                return [
                    open_action,
                    save_as_qlr_action,
                    save_as_qml_action,
                    extract_symbols_action,
                ]
            else:
                return [open_action]
        elif isinstance(self.object, GroupLayer):
            open_action = QAction(
                QCoreApplication.translate("SLYR", "&Add Group"), parent
            )
            open_action.triggered.connect(self.open_object)
            save_as_qml_action = QAction(
                QCoreApplication.translate("SLYR", "Save Group as QML…"), parent
            )
            save_as_qml_action.triggered.connect(self.save_as_qml)
            return [open_action, save_as_qlr_action, save_as_qml_action]
        else:
            open_action = QAction(
                QCoreApplication.translate("SLYR", "&Add Layer"), parent
            )
            open_action.triggered.connect(self.open_object)
            save_as_qml_action = QAction(
                QCoreApplication.translate("SLYR", "Save Layer as QML…"), parent
            )
            save_as_qml_action.triggered.connect(self.save_as_qml)
            return [open_action, save_as_qlr_action, save_as_qml_action]
