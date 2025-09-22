"""
Handles pasting layout elements from ArcMap
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
from io import BytesIO

from qgis.core import Qgis, QgsProject
from qgis.gui import QgsLayoutCustomDropHandler

from .browser_utils import BrowserUtils
from ...converters.context import Context
from ...converters.layout import LayoutConverter
from ...parser.stream import Stream


class LayoutDropHandler(QgsLayoutCustomDropHandler):
    """
    Handles pasting layout elements from ArcMap
    """

    def __init__(self, parent=None):  # pylint: disable=useless-super-delegation
        super().__init__(parent)

    def handlePaste(
        self,  # pylint: disable=missing-function-docstring,too-many-locals,too-many-statements
        designer_iface,
        pastePoint,  # pylint: disable=unused-argument
        data,
    ):
        if (
            'application/x-qt-windows-mime;value="Esri Graphics List"'
            not in data.formats()
        ):
            return False, []

        layout_data = data.data(
            'application/x-qt-windows-mime;value="Esri Graphics List"'
        )
        mime_binary = BytesIO(layout_data.data())
        stream = Stream(mime_binary)  # ,tolerant=True)

        layout = designer_iface.layout()

        stream.is_layer = True

        stream.read_ushort()
        stream.read_int("version number (eg 10651)")
        stream.read_ushort(expected=0)
        stream.read_int(expected=0)
        stream.read_int(expected=0)
        stream.read_int(expected=0)
        stream.read_double("page width")
        page_height = stream.read_double("page height")
        stream.read_int()
        stream.read_int()
        stream.read_int()
        stream.read_int()
        page_units = stream.read_int()

        base_units, conversion_factor = LayoutConverter.units_to_layout_units(
            page_units
        )

        context = Context()
        context.project = QgsProject.instance()

        warnings = set()
        errors = set()
        info = set()

        def unsupported_object_callback(msg, level=Context.WARNING):
            if level == Context.WARNING:
                warnings.add(html.escape(msg))
            elif level == Context.CRITICAL:
                errors.add(html.escape(msg))
            elif level == Context.INFO:
                info.add(msg)

        context.unsupported_object_callback = unsupported_object_callback

        count = stream.read_int("count")
        added_items = {}
        added_objects = []
        for _ in range(count):
            obj = stream.read_object()
            added_objects.append(obj)

            items = LayoutConverter.convert_element(
                obj, layout, page_height, context, base_units, conversion_factor, {}
            )
            if items is not None:
                for e, item in items.items():
                    added_items[e] = item

        # reconnect to maps, etc
        for e in added_objects:
            LayoutConverter.reconnect_element(e, layout, added_items, context)

        if warnings or errors or info:
            message = ""
            title = ""
            level = None

            if errors:
                message = "<p>The following errors were generated while pasting the elements:</p>"
                message += "<ul>"
                for w in errors:
                    message += "<li>{}</li>".format(
                        html.escape(w).replace("\n", "<br>")
                    )
                message += "</ul>"
                title = "Could not paste all elements"
                level = Qgis.MessageLevel.Critical

            if warnings:
                if message:
                    message += "<p>Additionally, some warnings were generated:</p>"
                else:
                    message += "<p>The following warnings were generated while pasting the elements:</p>"
                message += "<ul>"
                for w in warnings:
                    message += "<li>{}</li>".format(
                        html.escape(w).replace("\n", "<br>")
                    )
                message += "</ul>"
                if not title:
                    title = "Could not paste all elements"
                if level is None:
                    level = Qgis.MessageLevel.Warning

            if info:
                if message:
                    message += (
                        "<p>Additionally, some extra messages were generated:</p>"
                    )
                else:
                    message += "<p>The following information messages were generated pasting the elements"
                message += "<ul>"
                for w in info:
                    message += "<li>{}</li>".format(
                        html.escape(w).replace("\n", "<br>")
                    )
                message += "</ul>"
                if not title:
                    title = "Some messages were generated while pasting elements"
                if level is None:
                    level = Qgis.MessageLevel.Info

            BrowserUtils.show_warning(
                title,
                "Paste Elements",
                message,
                level=level,
                message_bar=designer_iface.messageBar(),
            )

        return True, added_items.values()
