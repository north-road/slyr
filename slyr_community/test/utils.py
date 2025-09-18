"""
Test utilities
"""

import re
from typing import List, Dict

import lxml.etree as ET
from qgis.PyQt.QtGui import QColor
from qgis.core import QgsSymbolLayer, QgsSymbol, QgsMapLayer


class Utils:
    """
    Test utilities
    """

    @staticmethod
    def symbol_layer_definition(layer: QgsSymbolLayer) -> dict:
        """
        Exports the non-default properties of a symbol layer
        """

        # create a new default version of the layer, and then remove all the default properties
        # so that we keep the result minimal
        default_layer = layer.__class__.create({})

        default_properties = default_layer.properties()
        layer_properties = layer.properties()

        for k, v in default_properties.items():
            if k in layer_properties and layer_properties[k] == v:
                del layer_properties[k]

        layer_properties["class"] = default_layer.__class__.__name__

        if layer.subSymbol():
            layer_properties["subsymbol"] = Utils.symbol_definition(layer.subSymbol())

        return layer_properties

    @staticmethod
    def symbol_definition(symbol: QgsSymbol) -> List[Dict]:
        """
        Exports a minimal definition of a symbol
        """
        return [Utils.symbol_layer_definition(layer) for layer in symbol]

    # pylint: disable=too-many-locals, too-many-statements
    @staticmethod
    def normalize_xml(xml_string) -> str:
        """
        Normalizes XML output for a test comparison
        """
        et = ET.fromstring(xml_string)

        for option in et.iter("Option"):
            if option.get("name") == "lineSymbol" and option.get("type") == "QString":
                symbol_xml = ET.fromstring(option.get("value"))
                normalized = ET.tostring(symbol_xml, method="c14n").decode()
                option.set("value", normalized)

        # force stable order for maplayers items
        map_layers_container = et.find("projectlayers")
        if map_layers_container is None:
            map_layers_container = et.find("maplayers")

        def get_map_layer_key(elem):
            data_source = elem.find("datasource").text
            layer_name = elem.find("layername").text

            key = "{},{}".format(layer_name, data_source)

            renderer = elem.find("renderer-v2")
            if renderer and renderer.get("type") == "singleSymbol":
                symbol = renderer.find("symbols/symbol")

                layer_options = symbol.findall("layer/Option/Option")
                for layer_option in layer_options:
                    if layer_option.get("name") == "color":
                        key += "," + layer_option.get("value")
                    if layer_option.get("name") == "line_color":
                        key += "," + layer_option.get("value")

            return key

        if map_layers_container is not None:
            map_layers_container[:] = sorted(
                map_layers_container, key=get_map_layer_key
            )

        # force stable order for annotation items
        def sort_item_container(container):  # pylint: disable=unused-argument
            def get_item_key(elem):
                if "wkt" in elem.attrib:
                    return str(elem.get("wkt"))
                elif "x" in elem.attrib:
                    return "{},{}".format(elem.get("x"), elem.get("y"))
                assert False

            items_container[:] = sorted(items_container, key=get_item_key)

            for idx, item in enumerate(items_container):
                item.attrib["id"] = f"item_{idx}"

        items_containers = et.findall("maplayers/maplayer/items")
        if items_containers is None:
            items_containers = et.findall("projectlayers/maplayer/items")
        for items_container in items_containers:
            sort_item_container(items_container)

        items_containers = et.findall("main-annotation-layer/items")
        for items_container in items_containers:
            sort_item_container(items_container)

        ET.indent(et, space=" ")
        res = ET.tostring(et, method="c14n").decode()

        # remove layer ids
        # layer_id_rx = re.compile(r'<id>[a-zA-Z0-9_]+?</id>', re.DOTALL)
        # res = re.sub(layer_id_rx, '<id>...</id>', res)

        for layer_id in re.findall(r"<id>([a-zA-Z0-9_]+?)</id>", res):
            res = res.replace(layer_id, "...")

        # layer_id2_rx = re.compile(r'\bid="[a-zA-Z0-9_{}]+?"', re.DOTALL)
        # res = re.sub(layer_id2_rx, 'id="..."', res)

        # remove rule based ids
        layer_id_rx = re.compile(r'key="{.*?}"', re.DOTALL)
        res = re.sub(layer_id_rx, 'key="..."', res)

        # remove symbol layer ids
        layer_id_rx = re.compile(r'id="{.*?}"', re.DOTALL)
        res = re.sub(layer_id_rx, 'id="..."', res)
        layer_id_rx = re.compile(r"id=&quot;{.*?}&quot;", re.DOTALL)
        res = re.sub(layer_id_rx, "id=&quot;...&quot;", res)

        item_id_rx = re.compile(r"<item>[a-zA-Z0-9_]+?</item>", re.DOTALL)
        res = re.sub(item_id_rx, "<item>...</item>", res)

        save_dt_rx = re.compile(r'saveDateTime="[0-9\-:T]+?"', re.DOTALL)
        res = re.sub(save_dt_rx, 'saveDateTime="..."', res)

        project_style_id_rx = re.compile(
            r'projectStyleId="[a-zA-Z0-9_:/.]+?"', re.DOTALL
        )
        res = re.sub(project_style_id_rx, 'projectStyleId="..."', res)

        creation_id_rx = re.compile(r"<creation>[0-9\-:T]+?</creation>", re.DOTALL)
        res = re.sub(creation_id_rx, "<creation>...</creation>", res)

        layer_id_rx = re.compile(r'<date type="Created" value=".*?"></date>', re.DOTALL)
        res = re.sub(layer_id_rx, '<date type="Created" value="..."></date>', res)

        # remove layout item uuids
        layer_id_rx = re.compile(r'templateUuid="{.*?}"', re.DOTALL)
        res = re.sub(layer_id_rx, 'templateUuid="..."', res)
        layer_id_rx = re.compile(r'uuid="{.*?}"', re.DOTALL)
        res = re.sub(layer_id_rx, 'uuid="..."', res)
        layer_id_rx = re.compile(r'frameMap="{.*?}"', re.DOTALL)
        res = re.sub(layer_id_rx, 'frameMap="..."', res)
        layer_id_rx = re.compile(r'mapUuid="{.*?}"', re.DOTALL)
        res = re.sub(layer_id_rx, 'mapUuid="..."', res)

        layer_id_rx = re.compile(r'projectStyleId=".*?"', re.DOTALL)
        res = re.sub(layer_id_rx, 'projectStyleId="..."', res)

        layer_id_rx = re.compile(r'id="{.+?}" name="Bookmark', re.DOTALL)
        res = re.sub(layer_id_rx, 'id="{...}" name="Bookmark', res)

        return res

    # pylint: enable=too-many-locals, too-many-statements

    @staticmethod
    def normalize_layer_for_test(layer: QgsMapLayer):
        """
        Normalizes a QGIS layer for test comparisons
        """
        try:
            layer.elevationProperties().profileLineSymbol().setColor(QColor(255, 0, 0))
        except AttributeError:
            pass
        try:
            layer.elevationProperties().profileMarkerSymbol().setColor(
                QColor(255, 0, 0)
            )
            for symbol_layer in layer.elevationProperties().profileMarkerSymbol():
                symbol_layer.setColor(QColor(255, 0, 0))
                symbol_layer.setStrokeColor(QColor(255, 255, 0))
        except AttributeError:
            pass
        try:
            layer.elevationProperties().profileFillSymbol().setColor(QColor(255, 0, 0))
            for symbol_layer in layer.elevationProperties().profileFillSymbol():
                symbol_layer.setColor(QColor(255, 0, 0))
                symbol_layer.setStrokeColor(QColor(255, 255, 0))
        except AttributeError:
            pass
        try:
            layer.elevationProperties().setPointColor(QColor(255, 0, 0))
        except AttributeError:
            pass
