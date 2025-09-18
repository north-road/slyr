#!/usr/bin/env python

# /***************************************************************************
# annotations.py
# ----------
# Date                 : September 2019
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

import os
import re
import base64
from typing import Tuple, Union, List, Optional

from qgis.core import (
    QgsCoordinateTransform,
    QgsWkbTypes,
    Qgis,
    QgsCoordinateReferenceSystem,
    QgsProject,
    QgsPointXY,
    QgsPoint,
    QgsMapLayer,
    QgsLineString,
    QgsFillSymbol,
    QgsMargins,
)

from qgis.PyQt.QtCore import Qt
from ..parser.objects.composite_graphics_layer import CompositeGraphicsLayer
from ..parser.objects.text_element import TextElement
from ..parser.objects.picture_element import PictureElement
from ..parser.objects.group_element import GroupElement
from .text_format import TextSymbolConverter
from .context import Context
from ..parser.exceptions import NotImplementedException

from .crs import CrsConverter
from .geometry import GeometryConverter
from .symbols import SymbolConverter
from ..parser.objects import (
    LineElement,
    MarkerElement,
    PolygonElement,
    RectangleElement,
    CircleElement,
    EllipseElement,
    ParagraphTextElement,
    EmfPictureElement,
    FrameElement,
    OleFrame,
    StdPicture,
    EmfPicture,
    BmpPicture,
    BmpPictureElement,
    PngPictureElement,
    JpgPictureElement,
    Jp2PictureElement,
    GifPictureElement,
    TifPictureElement,
)


class AnnotationConverter:
    @staticmethod
    def picture_element_to_path(
        element, context: Context
    ) -> Tuple[str, Optional[bool]]:
        picture_path = element.picture_path
        if not element.picture and not picture_path:
            picture_path = element.element_name

        picture_path = picture_path.replace("\\", "/")
        if element.picture:
            if issubclass(element.picture.__class__, StdPicture):
                p = element.picture.picture
            else:
                p = element.picture

            if issubclass(p.__class__, EmfPicture) or (
                issubclass(p.__class__, BmpPicture)
                and p.format == BmpPicture.FORMAT_EMF
            ):
                path = SymbolConverter.symbol_name_to_filename(
                    context.symbol_name, context.get_picture_store_folder(), "emf"
                )
                with open(path, "wb") as f:
                    f.write(p.content)

                svg_path = SymbolConverter.symbol_name_to_filename(
                    context.symbol_name, context.get_picture_store_folder(), "svg"
                )
                SymbolConverter.emf_to_svg(
                    path, svg_path, inkscape_path=context.inkscape_path, context=context
                )
                # no longer need the emf file
                try:
                    os.remove(path)
                except PermissionError:
                    pass

                if not os.path.exists(svg_path):
                    context.push_warning(
                        "{}: Conversion of EMF picture failed".format(
                            element.element_name
                        ),
                        level=Context.CRITICAL,
                    )

                if os.path.exists(svg_path):
                    with open(svg_path, "rb") as svg_file:
                        svg_content = base64.b64encode(svg_file.read()).decode("UTF-8")
                    # no longer need the svg
                    try:
                        os.remove(svg_path)
                    except PermissionError:
                        pass
                    svg_path = "base64:{}".format(svg_content)

                return svg_path, True
            else:
                picture_data = SymbolConverter.get_picture_data(
                    p, None, None, None, context=context
                )
                image_base64 = base64.b64encode(picture_data).decode("UTF-8")
                image_path = "base64:{}".format(image_base64)
                return image_path, False

        # no embedded picture
        if os.path.exists(picture_path):
            _, ext = os.path.splitext(picture_path)
            if ext.lower() == ".emf":
                svg_path = SymbolConverter.symbol_name_to_filename(
                    context.symbol_name, context.get_picture_store_folder(), "svg"
                )
                SymbolConverter.emf_to_svg(
                    picture_path,
                    svg_path,
                    inkscape_path=context.inkscape_path,
                    context=context,
                )
                # no longer need the emf file
                try:
                    os.remove(picture_path)
                except PermissionError:
                    pass
                if not os.path.exists(svg_path):
                    context.push_warning(
                        "{}: Conversion of EMF picture failed".format(
                            element.element_name
                        ),
                        level=Context.CRITICAL,
                    )
                else:
                    with open(svg_path, "rb") as svg_file:
                        svg_content = base64.b64encode(svg_file.read()).decode("UTF-8")
                    # no longer need the svg
                    try:
                        os.remove(svg_path)
                    except PermissionError:
                        pass
                    svg_path = "base64:{}".format(svg_content)
                    return svg_path, True

        is_svg = not isinstance(
            element,
            (
                PictureElement,
                BmpPictureElement,
                PngPictureElement,
                JpgPictureElement,
                Jp2PictureElement,
                GifPictureElement,
                TifPictureElement,
            ),
        )
        return picture_path, is_svg
