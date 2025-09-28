"""
Project file converter
"""

# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

import os
from typing import Optional, Dict

from qgis.core import (
    Qgis,
    QgsProject,
    QgsLabelingEngineSettings,
    QgsCoordinateReferenceSystem,
    QgsLayerTree,
    QgsReferencedRectangle,
    QgsRectangle,
    QgsMapLayer,
    QgsProjectMetadata,
    QgsMapThemeCollection,
    QgsRelation,
    QgsRasterLayer,
    QgsVectorLayer,
    QgsLayerTreeGroup,
)

try:
    from qgis.core import QgsRelationContext

    import_relations = True
except ImportError:
    import_relations = False

from qgis.utils import iface

from ..parser.object import CustomObject

from ..parser.objects import (
    MemoryRelationshipClassName,
    FeatureLayer,
    BasicOverposterProperties,
    Map,
)

from ..parser.streams import MapDocument

from .color import ColorConverter
from .context import Context
from .layers import LayerConverter
from .vector_layer import VectorLayerConverter
from .symbols import SymbolConverter
from .crs import CrsConverter
from .layout import LayoutConverter
from ..parser.exceptions import RequiresLicenseException


class ProjectConverter:
    """
    Project file converter
    """

    @staticmethod
    def convert_project(
        input_file: str,
        document: MapDocument,
        context: Context,
        fallback_crs=None,
    ) -> QgsProject:
        """
        Converts a project document to a QGIS project
        """

        if Qgis.QGIS_VERSION_INT >= 32601:
            # don't allow for project embedded styles
            p = QgsProject(capabilities=Qgis.ProjectCapabilities())
        else:
            p = QgsProject()

        context.project = p
        ProjectConverter.convert_target_project(
            p, input_file, document, context, fallback_crs
        )
        return p

    @staticmethod
    def set_project_home_paths(project: QgsProject, input_file: str):
        """
        Sets appropriate home paths on a project
        """
        home_path, _ = os.path.split(input_file)
        project.setPresetHomePath(home_path)

        try:
            project.setOriginalPath(input_file)
        except AttributeError:
            pass

    @staticmethod
    def convert_target_project(
        project: QgsProject,
        input_file: str,
        document: MapDocument,
        context: Context,
        fallback_crs=None,
        canvas=None,
    ):
        """
        Converts a map document into a target QGIS project
        """
        ProjectConverter.set_project_home_paths(project, input_file)

        if document.frames:
            layer_to_layer_map = ProjectConverter.update_project(
                project,
                input_file,
                document.frames[0],
                context,
                fallback_crs=fallback_crs,
                multiframes=len(document.frames) > 1,
            )
            for frame in document.frames[1:]:
                frame_layer_to_layer_map = ProjectConverter.update_project(
                    project,
                    input_file,
                    frame,
                    context,
                    multiframes=True,
                    fallback_crs=fallback_crs,
                )
                layer_to_layer_map = {**layer_to_layer_map, **frame_layer_to_layer_map}
        else:
            layer_to_layer_map = {}

        # loaded all layers. Now resolve relations
        for l, parent in layer_to_layer_map.items():
            if not isinstance(l, FeatureLayer):
                continue

            for r in l.relations:
                if isinstance(r, MemoryRelationshipClassName):
                    if not import_relations:
                        context.push_warning(
                            "{}: Converting relationships requires QGIS 3.12 or later".format(
                                l.name
                            ),
                            level=Context.CRITICAL,
                        )
                        break

                    # assume this is always the case??
                    # if not r.destination_name.to_dict() == l.dataset_name.to_dict():
                    #    if context.unsupported_object_callback:
                    #        context.unsupported_object_callback(
                    #            '{}: Could not convert relationship {}'.format(l.name, r.name),
                    #            level=Context.WARNING)

                    other = [
                        converted_layer
                        for o, converted_layer in layer_to_layer_map.items()
                        if hasattr(o, "dataset_name")
                        and o.dataset_name.to_dict() == r.origin_name.to_dict()
                    ]
                    if not other:
                        # a layer not currently in project, need to load it
                        child = VectorLayerConverter.source_to_QgsVectorLayer(
                            r.origin_name, r.forward_path_label, input_file, context
                        )
                        project.addMapLayer(child)
                    else:
                        child = other[0]

                    rel_context = QgsRelationContext(project)
                    rel = QgsRelation(rel_context)
                    rel.setId(r.name)
                    rel.setName(r.name)
                    rel.setReferencedLayer(parent.id())
                    rel.setReferencingLayer(child.id())
                    rel.addFieldPair(r.origin_foreign_key, r.origin_primary_key)
                    rel.updateRelationStatus()
                    # assert rel.isValid()

                    project.relationManager().addRelation(rel)

                else:
                    context.push_warning(
                        "{}: {} relationships are not yet supported".format(
                            l.name, r.__class__.__name__
                        ),
                        level=Context.CRITICAL,
                    )

        # hm, what to do with multiframes here?
        for frame_index, frame in enumerate(document.frames):
            ProjectConverter.convert_project_properties(
                frame,
                project,
                context,
                layer_to_layer_map,
                canvas,
                is_first_frame=frame_index == 0,
                has_multiple_frames=len(document.frames) > 1,
            )

        metadata = QgsProjectMetadata()
        metadata.setAuthor(document.author)
        # TODO metadata.setCreationDateTime()
        metadata.setTitle(document.title)
        metadata.setAbstract((document.summary + "\n" + document.description).strip())
        metadata.addKeywords("Tags", document.tags.split(","))
        project.setMetadata(metadata)

        # todo - convert other document stuff, e.g. defaults,...

        if document.layout_read_error:
            context.push_warning(
                "An error was encountered while reading the Page Layout: {}".format(
                    document.layout_read_error
                ),
                level=Context.CRITICAL,
            )

        elif document.page_layout:
            layout = LayoutConverter.convert_layout(
                document.page_layout,
                project,
                input_file,
                context,
                layer_to_layer_map,
            )
            project.layoutManager().addLayout(layout)

        project.writeEntry("Paths", "/Absolute", not document.use_relative_sources)

    @staticmethod
    def update_project(
        project: QgsProject,
        input_file: str,
        map_object: Map,
        context: Context,
        fallback_crs=None,
        multiframes=False,
        canvas=None,
    ) -> Dict:
        """
        Adds layers from a map document to an existing project
        """
        context.map_reference_scale = map_object.reference_scale
        return ProjectConverter.add_layers_to_project(
            project,
            input_file,
            map_object,
            context=context,
            fallback_crs=fallback_crs,
            parent_group_name=map_object.name if multiframes else None,
        )
        # ProjectConverter.convert_project_properties(map, project, context, canvas=canvas)

    @staticmethod
    def set_group_scale_range(
        group: QgsLayerTreeGroup, min_scale: float, max_scale: float
    ):
        """
        Sets the scale based visibility for an entire layer tree group
        """
        for _node in group.children():
            if QgsLayerTree.isLayer(_node):
                if _node.layer() is not None:
                    # TODO - merge with existing layer zoom ranges
                    _node.layer().setMinimumScale(min_scale)
                    _node.layer().setMaximumScale(max_scale)
                    _node.layer().setScaleBasedVisibility(True)
            elif QgsLayerTree.isGroup(_node):
                ProjectConverter.set_group_scale_range(_node, min_scale, max_scale)

    @staticmethod
    def set_group_transparency(group: QgsLayerTreeGroup, transparency: float):
        """
        Sets the layer transparency for an entire layer tree group
        """
        new_opacity = 1.0 - transparency / 100
        for _node in group.children():
            if QgsLayerTree.isLayer(_node):
                if _node.layer() is not None:
                    # We have to merge with existing layer opacity!
                    if (
                        isinstance(_node.layer(), QgsRasterLayer)
                        and _node.layer().renderer() is not None
                    ):
                        _node.layer().renderer().setOpacity(
                            new_opacity * _node.layer().renderer().opacity()
                        )
                    elif isinstance(_node.layer(), QgsVectorLayer):
                        _node.layer().setOpacity(new_opacity * _node.layer().opacity())
            elif QgsLayerTree.isGroup(_node):
                ProjectConverter.set_group_transparency(_node, transparency)

    @staticmethod
    def add_layers_to_project(
        project: QgsProject,
        input_file: str,
        map_object: Map,
        context: Context,
        fallback_crs=None,
        parent_group_name: Optional[str] = None,
    ) -> Dict:
        """
        Adds layers from a map to an existing QGIS project
        """
        theme = QgsMapThemeCollection.MapThemeRecord()
        if not fallback_crs:
            fallback_crs = QgsCoordinateReferenceSystem()

        context.map_reference_scale = map_object.reference_scale
        context.frame_crs = CrsConverter.convert_crs(map_object.crs, context)

        layer_to_layer_map = {}

        def add_layer(layer, group_node):
            nonlocal fallback_crs
            layers = LayerConverter.layer_to_QgsLayer(
                layer, input_file, context=context, fallback_crs=fallback_crs
            )

            if layers:
                for l in layers:
                    if l.name() == layer.name:
                        layer_to_layer_map[layer] = l

            for l in layers:
                if not fallback_crs.isValid() and l.crs().isValid():
                    fallback_crs = l.crs()
                project.addMapLayer(l, False)

                if l.customProperty("_slyr_group_name"):
                    new_group_name = l.customProperty("_slyr_group_name")
                    child_group = group_node.findGroup(new_group_name)
                    if not child_group:
                        child_group = group_node.addGroup(new_group_name)
                        child_group.setExpanded(
                            l.customProperty("_slyr_group_expanded")
                        )
                        child_group.setItemVisibilityChecked(
                            l.customProperty("_slyr_group_visible")
                        )
                    node = child_group.addLayer(l)
                    l.removeCustomProperty("_slyr_group_name")
                    l.removeCustomProperty("_slyr_group_expanded")
                    l.removeCustomProperty("_slyr_group_visible")
                else:
                    node = group_node.addLayer(l)

                if l.isSpatial() and (
                    not layer.visible or l.customProperty("_slyr_hidden_layer")
                ):
                    l.removeCustomProperty("_slyr_hidden_layer")
                    node.setItemVisibilityChecked(False)
                if hasattr(layer, "renderer") and hasattr(
                    layer.renderer, "legend_group"
                ):
                    node.setExpanded(layer.renderer.legend_group.editable_or_expanded)
                elif (
                    l.type() == QgsMapLayer.LayerType.VectorLayer
                    and l.renderer()
                    and len(l.renderer().legendSymbolItems()) > 10
                ):
                    node.setExpanded(False)

                theme_record = QgsMapThemeCollection.MapThemeLayerRecord(l)
                theme.addLayerRecord(theme_record)

            return layers

        def add_group(group, parent):
            group_node = parent.addGroup(group.name)
            group_layers = []

            for c in group.children:
                if LayerConverter.is_layer(c):
                    group_layers.extend(add_layer(c, group_node))
                else:
                    add_group(c, group_node)

            # layer.zoom_max = "don't show when zoomed out beyond"
            zoom_max = group.zoom_max or 0
            # layer.zoom_min = "don't show when zoomed in beyond"
            zoom_min = group.zoom_min or 0

            enabled_scale_range = bool(zoom_max or zoom_min)
            if zoom_max and zoom_min and zoom_min > zoom_max:
                # inconsistent scale range -- zoom_max should be bigger number than zoom_min
                zoom_min, zoom_max = zoom_max, zoom_min

            if enabled_scale_range:
                # qgis has no ability to set scale range based on layer tree groups, so push this down to layers
                ProjectConverter.set_group_scale_range(group_node, zoom_max, zoom_min)

            group_node.setItemVisibilityChecked(group.visible)
            group_node.setExpanded(group.expanded)

            if group.transparency:
                if Qgis.QGIS_VERSION_INT >= 32400:
                    from qgis.core import QgsGroupLayer

                    options = QgsGroupLayer.LayerOptions(project.transformContext())
                    group_layer = group_node.convertToGroupLayer(options)
                    group_layer.setOpacity(1 - group.transparency / 100)
                    project.addMapLayer(group_layer, False)
                else:
                    child_count = len(group.children)

                    if child_count > 1:
                        context.push_warning(
                            "{}: Group transparency was converted to individual layer transparency (group transparency requires QGIS 3.24 or later)".format(
                                group.name
                            ),
                            level=Context.WARNING,
                        )
                    ProjectConverter.set_group_transparency(
                        group_node, group.transparency
                    )

        # ouch, Arc allows multiple data frames to share a single name!!
        theme_name = map_object.name
        try_index = 1
        while project.mapThemeCollection().hasMapTheme(theme_name):
            try_index += 1
            theme_name = "{} ({})".format(map_object.name, try_index)

        if parent_group_name:
            root = project.layerTreeRoot().addGroup(theme_name)
        else:
            root = project.layerTreeRoot()

        # convert standalone tables BEFORE standard map layers, so that
        # they are already available for joins
        for t in map_object.standalone_tables:
            add_layer(t, root)

        root_layers = map_object.root_groups

        for c in root_layers:
            if isinstance(c, CustomObject):
                context.push_warning(
                    "An unknown custom object was removed from the project ({})".format(
                        c.clsid
                    ),
                    level=Context.WARNING,
                )
            elif LayerConverter.is_layer(c):
                add_layer(c, root)
            else:
                add_group(c, root)

        project.mapThemeCollection().insert(theme_name, theme)
        layer_to_layer_map[map_object] = theme_name

        return layer_to_layer_map

    @staticmethod
    def convert_project_properties(
        map_object: Map,
        destination_project: QgsProject,
        context: Context,
        layer_to_layer_map: Dict,
        canvas=None,
        is_first_frame: bool = True,
        has_multiple_frames: bool = False,
    ):
        """
        Converts general properties from a map object to a target QGIS project
        """
        if is_first_frame:
            destination_project.setCrs(
                CrsConverter.convert_crs(map_object.crs, context)
            )

        context.map_reference_scale = map_object.reference_scale
        theme_name = layer_to_layer_map.get(map_object)

        context.can_place_annotations_in_main_annotation_layer = not has_multiple_frames
        if map_object.graphics_layer:
            for g in map_object.graphics_layer.groups:
                if g:
                    raise RequiresLicenseException(
                        "Converting annotations or graphics layers requires the licensed version of SLYR"
                    )

        if is_first_frame:
            # better match for ArcGIS
            label_settings = destination_project.labelingEngineSettings()
            label_settings.setFlag(
                QgsLabelingEngineSettings.Flag.UsePartialCandidates, False
            )
            destination_project.setLabelingEngineSettings(label_settings)

        if is_first_frame:
            if map_object.scales:
                destination_project.viewSettings().setMapScales(
                    [float(s) for s in map_object.scales]
                )
                destination_project.viewSettings().setUseProjectScales(True)

            if Qgis.QGIS_VERSION_INT >= 31700 and map_object.fixed_extent:
                rect = QgsRectangle(
                    map_object.fixed_extent.x_min,
                    map_object.fixed_extent.y_min,
                    map_object.fixed_extent.x_max,
                    map_object.fixed_extent.y_max,
                )
                destination_project.viewSettings().setPresetFullExtent(
                    QgsReferencedRectangle(
                        rect,
                        CrsConverter.convert_crs(map_object.fixed_extent.crs, context),
                    )
                )

            if map_object.initial_view:
                rect = QgsRectangle(
                    map_object.initial_view.x_min,
                    map_object.initial_view.y_min,
                    map_object.initial_view.x_max,
                    map_object.initial_view.y_max,
                )
                destination_project.viewSettings().setDefaultViewExtent(
                    QgsReferencedRectangle(
                        rect,
                        CrsConverter.convert_crs(map_object.initial_view.crs, context),
                    )
                )

            if map_object.rotation:
                try:
                    destination_project.viewSettings().setDefaultRotation(
                        -map_object.rotation
                    )
                except AttributeError:
                    pass

                if destination_project == QgsProject.instance() and iface is not None:
                    iface.mapCanvas().setRotation(-map_object.rotation)

            if canvas and map_object.initial_view:
                rect = QgsRectangle(
                    map_object.initial_view.x_min,
                    map_object.initial_view.y_min,
                    map_object.initial_view.x_max,
                    map_object.initial_view.y_max,
                )
                canvas.setReferencedExtent(
                    QgsReferencedRectangle(
                        rect,
                        CrsConverter.convert_crs(map_object.initial_view.crs, context),
                    )
                )

            if map_object.background and map_object.background.symbol:
                background_symbol = SymbolConverter.Symbol_to_QgsSymbol(
                    map_object.background.symbol, context
                )
                color = background_symbol.color()
                destination_project.setBackgroundColor(color)

            if map_object.overposter_properties:
                settings = destination_project.labelingEngineSettings()
                if isinstance(
                    map_object.overposter_properties, BasicOverposterProperties
                ):
                    settings.setUnplacedLabelColor(
                        ColorConverter.color_to_qcolor(
                            map_object.overposter_properties.unplaced_label_color
                        )
                    )
                    if map_object.overposter_properties.view_unplaced:
                        settings.setFlag(
                            QgsLabelingEngineSettings.Flag.DrawUnplacedLabels, True
                        )
                destination_project.setLabelingEngineSettings(settings)
