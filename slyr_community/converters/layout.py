#!/usr/bin/env python

# /***************************************************************************
# layout.py
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

import re
import base64
import math
from io import BytesIO
import xml.etree.ElementTree as ET

from typing import Union, Optional, Tuple, List

from qgis.PyQt.QtGui import (
    QColor,
    QTextDocument,
    QFont,
    QPicture,
    QPainter,
    QBrush,
    QTransform,
)
from qgis.PyQt.QtSvg import QSvgGenerator, QSvgRenderer
from qgis.core import (
    QgsMapLayer,
    QgsProject,
    QgsExpressionContextUtils,
    QgsPrintLayout,
    QgsLayoutSize,
    QgsUnitTypes,
    QgsLayoutPoint,
    QgsFillSymbol,
    QgsLayoutItemMap,
    QgsLayoutItem,
    QgsLegendRenderer,
    QgsLayoutMeasurement,
    QgsLayoutItemLabel,
    QgsLayoutItemPicture,
    QgsLayerTreeLayer,
    QgsRectangle,
    QgsLegendStyle,
    QgsLayoutItemScaleBar,
    QgsLayoutItemShape,
    QgsLayoutItemMapGrid,
    QgsLayoutItemPolygon,
    QgsLayoutItemPolyline,
    QgsCentroidFillSymbolLayer,
    QgsLayoutUtils,
    QgsCoordinateReferenceSystem,
    QgsLayoutObject,
    QgsProperty,
    QgsLayoutGuide,
    QgsLayoutItemMapOverview,
    Qgis,
    QgsSymbol,
    QgsWkbTypes,
    QgsSymbolLegendNode,
    QgsMapLayerLegendUtils,
    QgsLayerTreeModelLegendNode,
    QgsCategorizedSymbolRenderer,
    QgsSimpleFillSymbolLayer,
    QgsScaleBarSettings,
    QgsLayoutItemAttributeTable,
    QgsLayoutFrame,
    QgsLayoutTableColumn,
    QgsLayoutTable,
    QgsSimpleLegendNode,
    QgsTextRenderer,
    QgsRenderContext,
    QgsFontUtils,
    QgsLayout,
    QgsLayoutItemPage,
    QgsLayoutGuideCollection,
    QgsLayoutItemLegend,
    QgsTextBackgroundSettings,
)


USE_LAYOUT_MARKER = False
try:
    from qgis.core import QgsLayoutItemMarker, QgsLayoutNorthArrowHandler

    USE_LAYOUT_MARKER = True
except ImportError:
    pass

USE_LEGEND_PATCHES = False
try:
    from qgis.core import QgsLegendPatchShape

    USE_LEGEND_PATCHES = True
except ImportError:
    pass

from qgis.PyQt.QtCore import QRectF, Qt, QPointF, QSizeF, QTemporaryDir
from qgis.PyQt.QtGui import QFontMetricsF, QPolygonF
from ..parser.objects.units import Units
from ..parser.exceptions import NotImplementedException
from ..parser.objects import (
    PageLayout,
    MapFrame,
    MapSurroundFrame,
    LegendItemBase,
    Graticule,
    Element,
    FrameElement,
    TableFrame,
    Point,
    LatLonFormat,
    SimpleMapGridBorder,
    HorizontalLegendItem,
    SimpleRenderer,
    PictureElement,
    BmpPictureElement,
    EmfPictureElement,
    GifPictureElement,
    Jp2PictureElement,
    JpgPictureElement,
    PngPictureElement,
    TifPictureElement,
    ScaleLine,
    PieChartSymbol,
    AlternatingScaleBar,
    DoubleAlternatingScaleBar,
    ScaleText,
    ScalebarBase,
    RectangleElement,
    LineElement,
    TextElement,
    CircleElement,
    EllipseElement,
    ParagraphTextElement,
    MarkerNorthArrow,
    Legend,
    OleFrame,
    HollowScaleBar,
    SteppedScaleLine,
    SingleDivisionScaleBar,
    GroupElement,
    MeasuredGrid,
    PolygonElement,
    MarkerElement,
    DMSGridLabel,
    CornerGridLabel,
)
from .symbols import SymbolConverter
from .context import Context
from .color import ColorConverter
from .utils import ConversionUtils
from .text_format import TextSymbolConverter
from .vector_renderer import VectorRendererConverter
from .crs import CrsConverter
from .numeric_format import NumericFormatConverter
from .geometry import GeometryConverter
from ..parser.objects.arcobjects_enums import DMSGridLabelType
from .annotations import AnnotationConverter
from ..parser.objects.polygon import Polygon
from ..parser.stream import Stream


DYNAMIC_TEXT_REPLACEMENTS = {
    r'<dyn\s+type\s*=\s*"\s*document\s*"\s*property\s*=\s*"\s*title\s*"\s*(?:/>|>|/)': "[% @project_title %]",
    r'<dyn\s+type\s*=\s*"\s*date\s*"\s*format\s*=\s*"\s*[|]*\s*short\s*"\s*(?:/>|>|/)': "[% format_date(now(), 'dd/MM/yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*date\s*"\s*format\s*=\s*"\s*[|]*\s*month\s*"\s*(?:/>|>|/)': "[% format_date(now(), 'MMMM, yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*date\s*"\s*format\s*=\s*"\s*[|]*\s*MMMM yyyy?\s*"\s*(?:/>|>|/)': "[% format_date(now(), 'MMMM yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*date\s*"\s*format\s*=\s*"\s*[|]*\s*MMMM?\s*"\s*(?:/>|>|/)': "[% format_date(now(), 'MMMM') %]",
    r'<dyn\s+type\s*=\s*"\s*date\s*"\s*format\s*=\s*"\s*[|]*\s*MMM yyyy?\s*"\s*(?:/>|>|/)': "[% format_date(now(), 'MMM yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*date\s*"\s*format\s*=\s*"\s*[|]*\s*yyyy?\s*"\s*(?:/>|>|/)': "[% format_date(now(), 'yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*date\s*"\s*format\s*=\s*"\s*[|]*\s*dd MMM yyyy?\s*"\s*(?:/>|>|/)': "[% format_date(now(), 'dd MMM yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*date\s*"\s*format\s*=\s*"\s*[|]*\s*dd/MM/yyyy?\s*"\s*(?:/>|>|/)': "[% format_date(now(), 'dd/MM/yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*date\s*"\s*format\s*=\s*"\s*[|]*\s*MM/dd/yyyy?\s*"\s*(?:/>|>|/)': "[% format_date(now(), 'MM/dd/yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*date\s*"\s*format\s*=\s*"\s*[|]*\s*dd-MMM-yyyy?\s*"\s*(?:/>|>|/)': "[% format_date(now(), 'dd-MMM-yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*date\s*"\s*format\s*=\s*"\s*[|]*\s*MMMM dd, yyyy?\s*"\s*(?:/>|>|/)': "[% format_date(now(), 'MMMM dd, yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*date\s*"\s*format\s*=\s*"\s*[|]*\s*dd MMMM yyyy?\s*"\s*(?:/>|>|/)': "[% format_date(now(), 'dd MMMM yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*date\s*"\s*format\s*=\s*"\s*[|]*\s*dd. MMMM yyyy?\s*"\s*(?:/>|>|/)': "[% format_date(now(), 'dd. MMMM yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*date\s*"\s*format\s*=\s*"\s*[|]*\s*dd\s*"\s*(?:/>|>|/)': "[% format_date(now(), 'dd') %]",
    r'<dyn\s+type\s*=\s*"\s*date\s*"\s*format\s*=\s*"\s*[|]*\s*MM\s*"\s*(?:/>|>|/)': "[% format_date(now(), 'MM') %]",
    r'<dyn\s+type\s*=\s*"\s*date\s*"\s*format\s*=\s*"\s*"\s*(?:/>|>|/)': "[% format_date(now(), 'dd/MM/yyyy?') %]",
    r'<dyn\s+type\s*=\s*"\s*time\s*"\s*format\s*=\s*""\s*(?:/>|>|/)': "[% format_date(now(), 'h:mm:ss A') %]",
    r'<dyn\s+type\s*=\s*"\s*project\s*"\s*property\s*=\s*"\s*name\s*"\s*(?:/>|>|/)': "[% @project_title %]",
    r'<dyn\s+type\s*=\s*"\s*project\s*"\s*property\s*=\s*"\s*path\s*"\s*(?:/>|>|/)': "[% @project_path %]",
    r'<dyn\s+type\s*=\s*"\s*project\s*"\s*newLine\s*=\s*"\s*true\s*"\s*property\s*=\s*"\s*path\s*"\s*(?:/>|>|/)': "\n[% @project_path %]",
    r'<dyn\s+type\s*=\s*"\s*project\s*"\s*property\s*=\s*"\s*folder\s*"\s*(?:/>|>|/)': "[% @project_folder %]",
    r'<dyn\s+type\s*=\s*"\s*project\s*"\s*property\s*=\s*"\s*dateSaved\s*"\s*format\s*="\s*[|]*\s*short\s*"\s*(?:/>|>|/)': "[% format_date(@project_last_saved, 'dd/MM/yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*project\s*"\s*property\s*=\s*"\s*dateSaved\s*"\s*format\s*="\s*[|]*\s*MMMM yyyy\s*"\s*(?:/>|>|/)': "[% format_date(@project_last_saved, 'MMMM yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*project\s*"\s*property\s*=\s*"\s*dateSaved\s*"\s*format\s*="\s*[|]*\s*yyyy\s*"\s*(?:/>|>|/)': "[% format_date(@project_last_saved, 'yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*project\s*"\s*property\s*=\s*"\s*dateSaved\s*"\s*format\s*="\s*[|]*\s*dd MMM yyyy\s*"\s*(?:/>|>|/)': "[% format_date(@project_last_saved, 'dd MMM yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*project\s*"\s*property\s*=\s*"\s*dateSaved\s*"\s*format\s*="\s*[|]*\s*dd/MM/yyyy\s*"\s*(?:/>|>|/)': "[% format_date(@project_last_saved, 'dd/MM/yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*project\s*"\s*property\s*=\s*"\s*dateSaved\s*"\s*format\s*="\s*[|]*\s*MMMM dd, yyyy\s*"\s*(?:/>|>|/)': "[% format_date(@project_last_saved, 'MMMM dd, yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*project\s*"\s*property\s*=\s*"\s*dateSaved\s*"\s*format\s*="\s*[|]*\s*dd. MMMM yyyy\s*"\s*(?:/>|>|/)': "[% format_date(@project_last_saved, 'dd. MMMM yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*project\s*"\s*property\s*=\s*"\s*dateSaved\s*"\s*format\s*="\s*"\s*(?:/>|>|/)': "[% format_date(@project_last_saved, 'dd/MM/yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*document\s*"\s*property\s*=\s*"\s*date\s+saved\s*"\s*format\s*=\s*"\s*[|]*\s*short\s*"\s*(?:/>|>|/)': "[% format_date(@project_last_saved, 'dd/MM/yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*document\s*"\s*property\s*=\s*"\s*date\s+saved\s*"\s*format\s*=\s*"\s*[|]*\s*MMMM yyyy\s*"\s*(?:/>|>|/)': "[% format_date(@project_last_saved, 'MMMM yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*document\s*"\s*property\s*=\s*"\s*date\s+saved\s*"\s*format\s*=\s*"\s*[|]*\s*yyyy\s*"\s*(?:/>|>|/)': "[% format_date(@project_last_saved, 'yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*document\s*"\s*property\s*=\s*"\s*date\s+saved\s*"\s*format\s*=\s*"\s*[|]*\s*dd MMM yyyy\s*"\s*(?:/>|>|/)': "[% format_date(@project_last_saved, 'dd MMM yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*document\s*"\s*property\s*=\s*"\s*date\s+saved\s*"\s*format\s*=\s*"\s*[|]*\s*dd/MM/yyyy\s*"\s*(?:/>|>|/)': "[% format_date(@project_last_saved, 'dd/MM/yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*document\s*"\s*property\s*=\s*"\s*date\s+saved\s*"\s*format\s*=\s*"\s*[|]*\s*MMMM dd, yyyy\s*"\s*(?:/>|>|/)': "[% format_date(@project_last_saved, 'MMMM dd, yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*document\s*"\s*property\s*=\s*"\s*date\s+saved\s*"\s*format\s*=\s*"\s*[|]*\s*dd. MMMM yyyy\s*"\s*(?:/>|>|/)': "[% format_date(@project_last_saved, 'dd. MMMM yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*document\s*"\s*property\s*=\s*"\s*date\s+saved\s*"\s*format\s*=\s*"\s*"\s*(?:/>|>|/)': "[% format_date(@project_last_saved, 'dd/MM/yyyy') %]",
    r'<dyn\s+type\s*=\s*"\s*user\s*"\s*(?:/>|>|/)': "[% @user_account_name %]",
    r'<dyn\s+type\s*=\s*"\s*document\s*"\s*property\s*=\s*"\s*name\s*"\s*(?:/>|>|/)': "[% @project_filename %]",
    r'<dyn\s+type\s*=\s*"\s*document\s*"\s*property\s*=\s*"\s*path\s*"\s*(?:/>|>|/)': "[% @project_path %]",
    r'<dyn\s+type\s*=\s*"\s*document\s*"\s*property\s*=\s*"\s*author\s*"\s*(?:/>|>|/)': "[% @project_author %]",
    r'<dyn\s+type\s*=\s*"\s*page\s*"\s*property\s*=\s*"\s*number\s*"\s*(?:/>|>|/)': "[% @atlas_featurenumber %]",
    r'<dyn\s+type\s*=\s*"\s*page\s*"\s*property\s*=\s*"\s*index\s*"\s*(?:/>|>|/)': "[% @atlas_featurenumber %]",
    r'<dyn\s+type\s*=\s*"\s*page\s*"\s*property\s*=\s*"\s*name\s*"\s*(?:/>|>|/)': "[% @atlas_pagename %]",
    r'<dyn\s+type\s*=\s*"\s*page\s*"\s*property\s*=\s*"\s*count\s*"\s*(?:/>|>|/)': "[% @atlas_totalfeatures %]",
    r'<dyn\s+type\s*=\s*"\s*page\s*"\s*property\s*=\s*"\s*(?!count|index|name|number|attribute)(.*?)\s*"\s*(?:/>|>|/)': '[% "\\1" %]',
    r'<dyn\s+type\s*=\s*"\s*layout\s*"\s*property\s*=\s*"\s*name\s*"\s*(?:/>|>|/)': "[% @layout_name %]",
    r'<dyn\s+type\s*=\s*"\s*layout\s*"\s*property\s*=\s*"\s*metadata\s*"\s*attribute\s*=\s*"\s*title\s*"\s*emptyStr\s*=\s*"(.*?)"\s*(?:/>|>|/)': "[% coalesce(@layout_title, @layout_name) %]",
    r'<dyn\s+type\s*=\s*"\s*layout\s*"\s*property\s*=\s*"\s*metadata\s*"\s*attribute\s*=\s*"\s*contactname\s*"\s*emptyStr\s*=\s*"(.*?)"\s*(?:/>|>|/)': "[% coalesce(@project_author, '\\1') %]",
    r'<dyn\s+type\s*=\s*"\s*layout\s*"\s*property\s*=\s*"\s*metadata\s*"\s*attribute\s*=\s*"\s*title\s*"\s*(?:/>|>|/)': "[% coalesce(@layout_title, @layout_name) %]",
    r'<dyn\s+type\s*=\s*"\s*layout\s*"\s*property\s*=\s*"\s*title\s*"\s*(?:/>|>|/)': "[% coalesce(@layout_title, @layout_name) %]",
    r'<dyn\s+type\s*=\s*"\s*layout\s*"\s*property\s*=\s*"\s*metadata\s*"\s*attribute\s*=\s*"\s*title\s*"\s*preStr\s*=\s*"(.*?)"\s*newLine\s*=\s*"\s*true\s*"\s*emptyStr\s*=\s*""\s*(?:/>|>|/)': "\\n\\1[% coalesce(@layout_title, @layout_name) %]",
    r'<dyn\s+type\s*=\s*"\s*layout\s*"\s*property\s*=\s*"\s*metadata\s*"\s*attribute\s*=\s*"\s*tags\s*"\s*(?:/>|>|/)': "[% @layout_tags %]",
    r'<dyn\s+type\s*=\s*"\s*layout\s*"\s*property\s*=\s*"\s*tags\s*"\s*(?:/>|>|/)': "[% @layout_tags %]",
    r'<dyn\s+type\s*=\s*"\s*layout\s*"\s*property\s*=\s*"\s*metadata\s*"\s*attribute\s*=\s*"\s*tags\s*"\s*preStr\s*=\s*"(.*?)"\s*newLine\s*=\s*"\s*true\s*"\s*emptyStr\s*=\s*""\s*(?:/>|>|/)': "\\n\\1[% @layout_tags %]",
    r'<dyn\s+type\s*=\s*"\s*layout\s*"\s*property\s*=\s*"\s*metadata\s*"\s*attribute\s*=\s*"\s*summary\s*"\s*(?:/>|>|/)': "[% @layout_summary %]",
    r'<dyn\s+type\s*=\s*"\s*layout\s*"\s*property\s*=\s*"\s*summary\s*"\s*(?:/>|>|/)': "[% @layout_summary %]",
    r'<dyn\s+type\s*=\s*"\s*layout\s*"\s*property\s*=\s*"\s*metadata\s*"\s*attribute\s*=\s*"\s*summary\s*"\s*preStr\s*=\s*"(.*?)"\s*newLine\s*=\s*"\s*true\s*"\s*emptyStr\s*=\s*""\s*(?:/>|>|/)': "\\n\\1[% @layout_summary %]",
    r'<dyn\s+type\s*=\s*"\s*layout\s*"\s*property\s*=\s*"\s*metadata\s*"\s*attribute\s*=\s*"\s*description\s*"\s*(?:/>|>|/)': "[% @layout_description %]",
    r'<dyn\s+type\s*=\s*"\s*layout\s*"\s*property\s*=\s*"\s*description\s*"\s*(?:/>|>|/)': "[% @layout_description %]",
    r'<dyn\s+type\s*=\s*"\s*layout\s*"\s*property\s*=\s*"\s*metadata\s*"\s*attribute\s*=\s*"\s*description\s*"\s*preStr\s*=\s*"(.*?)"\s*newLine\s*=\s*"\s*true\s*"\s*emptyStr\s*=\s*""\s*(?:/>|>|/)': "\\n\\1[% @layout_description %]",
    r'<dyn\s+type\s*=\s*"\s*layout\s*"\s*property\s*=\s*"\s*metadata\s*"\s*attribute\s*=\s*"\s*credits\s*"\s*(?:/>|>|/)': "[% @layout_credits %]",
    r'<dyn\s+type\s*=\s*"\s*layout\s*"\s*property\s*=\s*"\s*credits\s*"\s*(?:/>|>|/)': "[% @layout_credits %]",
    r'<dyn\s+type\s*=\s*"\s*layout\s*"\s*property\s*=\s*"\s*metadata\s*"\s*attribute\s*=\s*"\s*credits\s*"\s*preStr\s*=\s*"(.*?)"\s*newLine\s*=\s*"\s*true\s*"\s*emptyStr\s*=\s*""\s*(?:/>|>|/)': "\\n\\1[% @layout_credits %]",
    r'<dyn\s+type\s*=\s*"\s*layout\s*"\s*property\s*=\s*"\s*metadata\s*"\s*attribute\s*=\s*"\s*uselimit\s*"\s*(?:/>|>|/)': "[% @layout_constraints %]",
    r'<dyn\s+type\s*=\s*"\s*layout\s*"\s*property\s*=\s*"\s*uselimit\s*"\s*(?:/>|>|/)': "[% @layout_constraints %]",
    r'<dyn\s+type\s*=\s*"\s*layout\s*"\s*property\s*=\s*"\s*metadata\s*"\s*attribute\s*=\s*"\s*uselimit\s*"\s*preStr\s*=\s*"(.*?)"\s*newLine\s*=\s*"\s*true\s*"\s*emptyStr\s*=\s*""\s*(?:/>|>|/)': "\\n\\1[% @layout_constraints %]",
    r'<dyn\s+type\s*=\s*"\s*(?:dataFrame|mapFrame)\s*"\s*name\s*=\s*"\s*(.*?)\s*"\s*property\s*=\s*"\s*sr\s*"\s*srProperty\s*=\s*"\s*name\s*"\s*(?:/>|>|/)': "[% item_variables( '\\1')['map_crs_description']%]",
    r'<dyn\s+type\s*=\s*"\s*(?:dataFrame|mapFrame)\s*"\s*name\s*=\s*"\s*(.*?)\s*"\s*property\s*=\s*"\s*sr\s*"\s*srProperty\s*=\s*"\s*name\s*"\s*preStr\s*=\s*"?(.*?)"?\s*newLine\s*=\s*"?true"?\s*emptyStr\s*=\s*"?(.*?)"?(?:/>|>|/)': "\\n\\2[% item_variables('\\1')['map_crs_description']%]",
    r'<dyn\s+type\s*=\s*"\s*(?:dataFrame|mapFrame)\s*"\s*name\s*=\s*"\s*(.*?)\s*"\s*property\s*=\s*"\s*sr\s*"\s*srProperty\s*=\s*"\s*projection\s*"\s*preStr\s*=\s*"?(.*?)"?\s*newLine\s*=\s*"?true"?\s*emptyStr\s*=\s*"?(.*?)"?(?:/>|>|/)': "\\n\\2[% item_variables('\\1')['map_crs_acronym']%]",
    r'<dyn\s+type\s*=\s*"\s*(?:dataFrame|mapFrame)\s*"\s*name\s*=\s*"\s*(.*?)\s*"\s*property\s*=\s*"\s*sr\s*"\s*srProperty\s*=\s*"\s*projection\s*"\s*preStr\s*=\s*"?(.*?)"?\s*newLine\s*=\s*"?false"?\s*emptyStr\s*=\s*"?(.*?)"?(?:/>|>|/)': "\\2[% item_variables('\\1')['map_crs_acronym']%]",
    r'<dyn\s+type\s*=\s*"\s*(?:dataFrame|mapFrame)\s*"\s*name\s*=\s*"\s*(.*?)\s*"\s*property\s*=\s*"\s*sr\s*"\s*srProperty\s*=\s*"\s*datum\s*"\s*preStr\s*=\s*"?(.*?)"?\s*newLine\s*=\s*"?true"?\s*emptyStr\s*=\s*"?(.*?)"?(?:/>|>|/)': "\\n\\2[% item_variables('\\1')['map_crs_ellipsoid']%]",
    r'<dyn\s+type\s*=\s*"\s*(?:dataFrame|mapFrame)\s*"\s*name\s*=\s*"\s*(.*?)\s*"\s*property\s*=\s*"\s*sr\s*"\s*srProperty\s*=\s*"\s*datum\s*"\s*preStr\s*=\s*"?(.*?)"?\s*newLine\s*=\s*"?false"?\s*emptyStr\s*=\s*"?(.*?)"?(?:/>|>|/)': "\\2[% item_variables('\\1')['map_crs_ellipsoid']%]",
    r'<dyn\s+type\s*=\s*"\s*(?:dataFrame|mapFrame)\s*"\s*name\s*=\s*"\s*(.*?)\s*"\s*property\s*=\s*"\s*sr\s*"\s*srProperty\s*=\s*"\s*datum\s*"\s*(?:/>|>|/)': "[% item_variables('\\1')['map_crs_ellipsoid']%]",
    r'<dyn\s+type\s*=\s*"\s*(?:dataFrame|mapFrame)\s*"\s*name\s*=\s*"\s*(.*?)\s*"\s*property\s*=\s*"\s*scale\s*"\s*pageUnits\s*=\s*".*"\s*mapUnits\s*=\s*".*?"\s*pageValue\s*=\s*".*?"\s*decimalPlaces\s*=\s*"?(.*?)"?(?:/>|>|/)': "[% format_number(item_variables('\\1')['map_scale'], places:=\\2, omit_group_separators:=true, trim_trailing_zeroes:=true) %]",
    r'<dyn\s+type\s*=\s*"\s*page\s*"\s*property\s*=\s*"\s*attribute\s*"\s*field\s*=\s*"\s*(.*?)\s*"\s*domainlookup\s*=\s*"\s*true\s*"\s*(?:/>|>|/)': '[% "\\1" %]',
    r'<dyn\s+type\s*=\s*"\s*page\s*"\s*property\s*=\s*"\s*attribute\s*"\s*field\s*=\s*"\s*(.*?)\s*"\s*domainlookup\s*=\s*"\s*true\s*"\s*emptyStr\s*=\s*"(.*?)"\s*(?:/>|>|/)': '[% case when length("\\1") > 0 then "\\1" else \'\\2\' end %]',
    r'<dyn\s+type\s*=\s*"\s*time\s*"\s*format\s*=\s*"\s*(.*?)\s*"\s*(?:/>|>|/)': "[% format_date(now(), '\\1') %]",
}

if Qgis.QGIS_VERSION_INT >= 32900:
    DYNAMIC_TEXT_REPLACEMENTS[
        r'<dyn\s+type\s*=\s*"\s*(?:dataFrame|mapFrame)\s*"\s+name\s*=\s*"\s*(.+?)\s*"\s+property\s*=\s*"\s*scale\s*"\s*(?:/>|>|/)'
    ] = "[%format_number(item_variables('\\1')['map_scale'], trim_trailing_zeroes:=true)%]"
    DYNAMIC_TEXT_REPLACEMENTS[
        r'<dyn\s+type\s*=\s*"\s*(?:dataFrame|mapFrame)\s*"\s*name\s*=\s*"\s*(.*?)\s*"\s*property\s*=\s*"\s*scale\s*"\s*preStr\s*=\s*"?\s*(.*?)\s*"?\s*(?:/>|>|/)'
    ] = "\\2[% format_number(item_variables( '\\1')['map_scale'], 3, trim_trailing_zeroes:=true)%]"
else:
    DYNAMIC_TEXT_REPLACEMENTS[
        r'<dyn\s+type\s*=\s*"\s*(?:dataFrame|mapFrame)\s*"\s+name\s*=\s*"\s*(.+?)\s*"\s+property\s*=\s*"\s*scale\s*"\s*(?:/>|>|/)'
    ] = "[%round(item_variables('\\1')['map_scale'])%]"
    DYNAMIC_TEXT_REPLACEMENTS[
        r'<dyn\s+type\s*=\s*"\s*(?:dataFrame|mapFrame)\s*"\s*name\s*=\s*"\s*(.*?)\s*"\s*property\s*=\s*"\s*scale\s*"\s*preStr\s*=\s*"?\s*(.*?)\s*"?\s*(?:/>|>|/)'
    ] = "\\2[% round(item_variables( '\\1')['map_scale'], 3)%]"

if Qgis.QGIS_VERSION_INT >= 33100:
    DYNAMIC_TEXT_REPLACEMENTS[
        r'<dyn\s+type\s*=\s*"\s*layout\s*"\s+property\s*=\s*"\s*metadata\s*"\s+attribute\s*=\s*"\s*credits\s*"\s* emptyStr\s*=\s*"(.*?)"\s*(?:/>|>|/)'
    ] = "[% coalesce(array_to_string(map_credits()), '\\1') %]"
    DYNAMIC_TEXT_REPLACEMENTS[
        r'<dyn\s+type\s*=\s*"\s*layout\s*"\s+name\s*=\s*".*?"\s*property\s*=\s*"\s*serviceLayerCredits\s*"\s*(?:/>|>|/)'
    ] = "[% array_to_string(map_credits()) %]"
    DYNAMIC_TEXT_REPLACEMENTS[
        r'<dyn\s+type\s*=\s*"\s*layout\s*"\s*property\s*=\s*"\s*serviceLayerCredits\s*"\s*separator="(.*?)"\s*showLayerNames\s*=\s*"\s*false\s*"\s*layerNameSeparator\s*=\s*".*?"\s*(?:/>|>|/)'
    ] = "[% array_to_string(map_credits(), delimiter:='\\1') %]"


# if Qgis.QGIS_VERSION_INT >= 31800:
#    DYNAMIC_TEXT_REPLACEMENTS[r'<dyn\s+type\s*=\s*"\s*document\s*"\s*property\s*=\s*"\s*service\s+layer\s+credits\s*"\s*separator\s*=\s*"\\n"\s*showLayerNames\s*=\s*"\s*false\s*"\s*layerNameSeparator\s*=\s*": "/>'] = '[% array_to_string(map_credits(\'Main Map\',include_layer_names:=true), delimiter:=\'\\n\') %]'

HTML_REPLACEMENTS = {
    "<bol>": "<b>",
    "</bol>": "</b>",
    "<ita>": "<i>",
    "<sub>": "<sub>",
    "<sup>": "<sup>",
    "</ita>": "</i>",
    "<und>": "<u>",
    "</und>": "</u>",
    "<clr\\s+red\\s*=\\s*[\"'](\\d+)[\"']\\s+green\\s*=\\s*[\"'](\\d+)[\"']\\s+blue\\s*=\\s*\\s*[\"'](\\d+)[\"']\\s*>": '<span style="color: rgb(\\1, \\2, \\3)">',
    "<clr\\s+red\\s*=\\s*[\"'](\\d+)[\"']\\s+blue\\s*=\\s*[\"'](\\d+)[\"']\\s+green\\s*=\\s*\\s*[\"'](\\d+)[\"']\\s*>": '<span style="color: rgb(\\1, \\3, \\2)">',
    "<clr\\s+green\\s*=\\s*[\"'](\\d+)[\"']\\s+red\\s*=\\s*[\"'](\\d+)[\"']\\s+blue\\s*=\\s*\\s*[\"'](\\d+)[\"']\\s*>": '<span style="color: rgb(\\2, \\1, \\3)">',
    "<clr\\s+blue\\s*=\\s*[\"'](\\d+)[\"']\\s+red\\s*=\\s*[\"'](\\d+)[\"']\\s+green\\s*=\\s*\\s*[\"'](\\d+)[\"']\\s*>": '<span style="color: rgb(\\2, \\3, \\1)">',
    "<clr\\s+green\\s*=\\s*[\"'](\\d+)[\"']\\s+blue\\s*=\\s*[\"'](\\d+)[\"']\\s+red\\s*=\\s*\\s*[\"'](\\d+)[\"']\\s*>": '<span style="color: rgb(\\3, \\1, \\2)">',
    "<clr\\s+blue\\s*=\\s*[\"'](\\d+)[\"']\\s+green\\s*=\\s*[\"'](\\d+)[\"']\\s+red\\s*=\\s*\\s*[\"'](\\d+)[\"']\\s*>": '<span style="color: rgb(\\3, \\2, \\1)">',
    "<fnt\\s+name\\s*=\\s*[\"'](.*?)[\"']\\s+size\\s*=\\s*[\"'](\\d+)[\"']\\s*>": '<span style="font-family: \\1; font-size: \\2pt">',
    "<fnt\\s+style\\s*=\\s*[\"']bold[\"']\\s+size\\s*=\\s*[\"'](\\d+)[\"']\\s*>": '<span style="font-weight: bold; font-size: \\1pt">',
    "<fnt\\s+size\\s*=\\s*[\"'](\\d+)[\"']\\s*>": '<span style="font-size: \\1pt">',
    "<fnt\\s+name\\s*=\\s*[\"'](.*?)[\"']\\s*>": '<span style="font-family: \\1;">',
    "<fnt\\s+style\\s*=\\s*[\"']bold[\"']\\s*>": '<span style="font-weight: bold">',
    "<fnt\\s+style\\s*=\\s*[\"']italic[\"']\\s*>": '<span style="font-style: italic">',
    "</clr>": "</span>",
    "<acp>": '<span style="text-transform: uppercase;">',
    "</acp>": "</span>",
    "</fnt>": "</span>",
}

POINTS_TO_MM = 0.3527777778


class LayoutConverter:
    @staticmethod
    def units_to_layout_units(units):
        if units == Units.DISTANCE_UNKNOWN:
            return QgsUnitTypes.LayoutUnit.LayoutCentimeters, 1
        elif units == Units.DISTANCE_INCHES:
            return QgsUnitTypes.LayoutUnit.LayoutInches, 1
        elif units == Units.DISTANCE_POINTS:
            return QgsUnitTypes.LayoutUnit.LayoutPoints, 1
        elif units == Units.DISTANCE_FEET:
            return QgsUnitTypes.LayoutUnit.LayoutFeet, 1
        elif units == Units.DISTANCE_YARDS:
            return QgsUnitTypes.LayoutUnit.LayoutFeet, 3
        elif units == Units.DISTANCE_MILES:
            return QgsUnitTypes.LayoutUnit.LayoutFeet, 5280
        elif units == Units.DISTANCE_NAUTICAL_MILES:
            return QgsUnitTypes.LayoutUnit.LayoutFeet, 6076.12
        elif units == Units.DISTANCE_MILLIMETERS:
            return QgsUnitTypes.LayoutUnit.LayoutMillimeters, 1
        elif units == Units.DISTANCE_CENTIMETERS:
            return QgsUnitTypes.LayoutUnit.LayoutCentimeters, 1
        elif units == Units.DISTANCE_METERS:
            return QgsUnitTypes.LayoutUnit.LayoutMeters, 1
        elif units == Units.DISTANCE_KILOMETERS:
            return QgsUnitTypes.LayoutUnit.LayoutMeters, 1000
        elif units == Units.DISTANCE_DECIMAL_DEGREES:
            return QgsUnitTypes.LayoutUnit.LayoutCentimeters, 1
        elif units == Units.DISTANCE_DECIMETERS:
            return QgsUnitTypes.LayoutUnit.LayoutCentimeters, 1

    @staticmethod
    def units_to_distance_units(units):
        if units == Units.DISTANCE_UNKNOWN:
            return QgsUnitTypes.DistanceUnit.DistanceUnknownUnit, 1
        elif units == Units.DISTANCE_INCHES:
            return QgsUnitTypes.DistanceUnit.DistanceFeet, 0.0833333
        elif units == Units.DISTANCE_POINTS:
            return QgsUnitTypes.DistanceUnit.DistanceFeet, 0.00115741
        elif units == Units.DISTANCE_FEET:
            return QgsUnitTypes.DistanceUnit.DistanceFeet, 1
        elif units == Units.DISTANCE_YARDS:
            return QgsUnitTypes.DistanceUnit.DistanceYards, 1
        elif units == Units.DISTANCE_MILES:
            return QgsUnitTypes.DistanceUnit.DistanceMiles, 1
        elif units == Units.DISTANCE_NAUTICAL_MILES:
            return QgsUnitTypes.DistanceUnit.DistanceNauticalMiles, 1
        elif units == Units.DISTANCE_MILLIMETERS:
            return QgsUnitTypes.DistanceUnit.DistanceMillimeters, 1
        elif units == Units.DISTANCE_CENTIMETERS:
            return QgsUnitTypes.DistanceUnit.DistanceCentimeters, 1
        elif units == Units.DISTANCE_METERS:
            return QgsUnitTypes.DistanceUnit.DistanceMeters, 1
        elif units == Units.DISTANCE_KILOMETERS:
            return QgsUnitTypes.DistanceUnit.DistanceKilometers, 1
        elif units == Units.DISTANCE_DECIMAL_DEGREES:
            return QgsUnitTypes.DistanceUnit.DistanceDegrees, 1
        elif units == Units.DISTANCE_DECIMETERS:
            return QgsUnitTypes.DistanceUnit.DistanceCentimeters, 10

    @staticmethod
    def generate_unique_layout_name(base_name: str, project: QgsProject) -> str:
        """
        Generates a unique name to use for a layout for a project
        """
        layout_name = base_name
        counter = 1
        while project.layoutManager().layoutByName(layout_name):
            counter += 1
            layout_name = "{} ({})".format(base_name, counter)
        return layout_name

    @staticmethod
    def convert_layout_metadata(layout: QgsLayout, metadata: str):
        content = ET.fromstring(metadata)

        res_title = content.find("./dataIdInfo/idCitation/resTitle")
        if res_title is not None:
            title = res_title.text
            QgsExpressionContextUtils.setLayoutVariable(layout, "layout_title", title)
        keywords = []
        for keyword in content.findall("./dataIdInfo/searchKeys/keyword"):
            keywords.append(keyword.text)
        if keywords:
            QgsExpressionContextUtils.setLayoutVariable(
                layout, "layout_tags", ",".join(keywords)
            )

        id_purp = content.find("./dataIdInfo/idPurp")
        if id_purp is not None:
            purpose = id_purp.text
            QgsExpressionContextUtils.setLayoutVariable(
                layout, "layout_summary", purpose
            )

        id_abs = content.find("./dataIdInfo/idAbs")
        if id_abs is not None:
            abstract = id_abs.text
            doc = QTextDocument()
            doc.setHtml(abstract)
            abstract = doc.toPlainText()
            QgsExpressionContextUtils.setLayoutVariable(
                layout, "layout_description", abstract
            )

        id_credit = content.find("./dataIdInfo/idCredit")
        if id_credit is not None:
            credit = id_credit.text
            QgsExpressionContextUtils.setLayoutVariable(
                layout, "layout_credits", credit
            )

        use_limit = content.find("./dataIdInfo/resConst/Consts/useLimit")
        if use_limit is not None:
            constraints = use_limit.text
            doc = QTextDocument()
            doc.setHtml(constraints)
            constraints = doc.toPlainText()
            QgsExpressionContextUtils.setLayoutVariable(
                layout, "layout_constraints", constraints
            )

    @staticmethod
    def convert_layout(
        obj: Union[PageLayout],
        project: QgsProject,
        input_file,
        context: Context,
        layer_to_layer_map=None,
    ):
        layout = QgsPrintLayout(project)
        context.layer_name = None
        context.symbol_name = None
        context.element_name = None
        layout.setName("Page Layout")
        context.layout_name = "Page Layout"

        if layer_to_layer_map is None:
            layer_to_layer_map = {}

        base_units, conversion_factor = LayoutConverter.units_to_layout_units(
            obj.page.units
        )

        page = QgsLayoutItemPage(layout)
        # some MXDs have 0 width/height pages -- this makes for confusing layouts!
        if obj.page.width and obj.page.height:
            page.setPageSize(
                QgsLayoutSize(
                    obj.page.width * conversion_factor,
                    obj.page.height * conversion_factor,
                    base_units,
                )
            )
        else:
            page.setPageSize("A4")

        c = ColorConverter.color_to_qcolor(obj.page.background_color)
        layout.pageCollection().setPageStyleSymbol(
            QgsFillSymbol.createSimple({"color": c.name(), "outline_style": "no"})
        )
        layout.pageCollection().addPage(page)

        if obj.page_index is not None:
            if obj.page_index.feature_layer not in layer_to_layer_map:
                context.push_warning(
                    "Could not restore atlas: layer {} was not found".format(
                        obj.page_index.feature_layer.name
                    ),
                    level=Context.CRITICAL,
                )
            else:
                layout.atlas().setEnabled(True)
                coverage_layer = layer_to_layer_map[obj.page_index.feature_layer]
                layout.atlas().setCoverageLayer(coverage_layer)
                layout.atlas().setPageNameExpression(obj.page_index.name_field)
                layout.atlas().setSortFeatures(True)
                layout.atlas().setSortAscending(obj.page_index.sort_ascending)
                layout.atlas().setSortExpression(obj.page_index.sort_field)

        added_items = {}

        source_elements = reversed(obj.elements)

        for e in source_elements:
            items = LayoutConverter.convert_element(
                e,
                layout,
                obj.page.height,
                context,
                base_units,
                conversion_factor,
                layer_to_layer_map,
            )
            layout.updateZValues(False)
            if items is not None:
                for e, i in items.items():
                    added_items[e] = i

        # reconnect to maps, etc
        for e in obj.elements:
            LayoutConverter.reconnect_element(e, layout, added_items, context)

        layout.updateZValues(False)
        if obj.page_index is not None:
            added_items[obj.page_index.map_frame].setAtlasDriven(True)

            if obj.page_index.scale_type == 0:
                added_items[obj.page_index.map_frame].setAtlasScalingMode(
                    QgsLayoutItemMap.AtlasScalingMode.Auto
                )
                if obj.page_index.best_fit_units != 0:
                    context.push_warning(
                        "Data driven pages currently only support margin based sizes",
                        level=Context.CRITICAL,
                    )
                else:
                    added_items[obj.page_index.map_frame].setAtlasMargin(
                        obj.page_index.best_fit_size - 1
                    )
            elif obj.page_index.scale_type == 1:
                # maintain scale
                added_items[obj.page_index.map_frame].setAtlasScalingMode(
                    QgsLayoutItemMap.AtlasScalingMode.Fixed
                )
            elif obj.page_index.scale_type == 2:
                # data defined scale
                added_items[obj.page_index.map_frame].setAtlasScalingMode(
                    QgsLayoutItemMap.AtlasScalingMode.Auto
                )
                added_items[
                    obj.page_index.map_frame
                ].dataDefinedProperties().setProperty(
                    QgsLayoutObject.DataDefinedProperty.MapScale,
                    QgsProperty.fromField(obj.page_index.scale_field),
                )

            if obj.page_index.rotation_field:
                added_items[
                    obj.page_index.map_frame
                ].dataDefinedProperties().setProperty(
                    QgsLayoutObject.DataDefinedProperty.MapRotation,
                    QgsProperty.fromField(obj.page_index.rotation_field),
                )
            if obj.page_index.crs_field:
                # todo -- will need a custom function to map these!
                context.push_warning(
                    "Data driven pages using field based spatial reference are not supported",
                    level=Context.CRITICAL,
                )

        if True:
            for g in obj.horizontal_snap_guides.guides:
                layout.guides().addGuide(
                    QgsLayoutGuide(
                        Qt.Orientation.Horizontal,
                        QgsLayoutMeasurement(
                            obj.page.height - g * conversion_factor, base_units
                        ),
                        page,
                    )
                )
            for g in obj.vertical_snap_guides.guides:
                layout.guides().addGuide(
                    QgsLayoutGuide(
                        Qt.Orientation.Vertical,
                        QgsLayoutMeasurement(g * conversion_factor, base_units),
                        page,
                    )
                )

        context.layout_name = None
        return layout

    ANCHOR_MAP = {
        Element.ANCHOR_BOTTOM_LEFT: QgsLayoutItem.ReferencePoint.LowerLeft,
        Element.ANCHOR_BOTTOM_MIDDLE: QgsLayoutItem.ReferencePoint.LowerMiddle,
        Element.ANCHOR_BOTTOM_RIGHT: QgsLayoutItem.ReferencePoint.LowerRight,
        Element.ANCHOR_LEFT: QgsLayoutItem.ReferencePoint.MiddleLeft,
        Element.ANCHOR_MIDDLE: QgsLayoutItem.ReferencePoint.Middle,
        Element.ANCHOR_RIGHT: QgsLayoutItem.ReferencePoint.MiddleRight,
        Element.ANCHOR_TOP_LEFT: QgsLayoutItem.ReferencePoint.UpperLeft,
        Element.ANCHOR_TOP_MIDDLE: QgsLayoutItem.ReferencePoint.UpperMiddle,
        Element.ANCHOR_TOP_RIGHT: QgsLayoutItem.ReferencePoint.UpperRight,
    }

    @staticmethod
    def set_common_properties(
        layout, element, item, page_height, context, base_units, conversion_factor
    ):
        if isinstance(element.shape, Point):
            if isinstance(element, MarkerElement):
                # these always store center points
                item.setReferencePoint(QgsLayoutItem.ReferencePoint.Middle)
                item.attemptMove(
                    QgsLayoutPoint(
                        element.shape.x * conversion_factor,
                        page_height - element.shape.y * conversion_factor,
                        base_units,
                    ),
                    useReferencePoint=True,
                )
                item.setReferencePoint(LayoutConverter.ANCHOR_MAP[element.anchor])
            else:
                # is this reachable??
                item.setReferencePoint(LayoutConverter.ANCHOR_MAP[element.anchor])
                item.attemptMove(
                    QgsLayoutPoint(
                        element.shape.x * conversion_factor,
                        page_height - element.shape.y * conversion_factor,
                        base_units,
                    ),
                    useReferencePoint=True,
                )
        else:
            if (
                not math.isnan(element.shape.x_max)
                and not math.isnan(element.shape.y_max)
                and not math.isnan(element.shape.x_min)
                and not math.isnan(element.shape.y_min)
            ):
                item.attemptResize(
                    QgsLayoutSize(
                        element.shape.x_max * conversion_factor
                        - element.shape.x_min * conversion_factor,
                        element.shape.y_max * conversion_factor
                        - element.shape.y_min * conversion_factor,
                        base_units,
                    )
                )
            item.setReferencePoint(LayoutConverter.ANCHOR_MAP[element.anchor])
            if not math.isnan(element.shape.x_min) and not math.isnan(
                element.shape.y_max
            ):
                item.attemptMove(
                    QgsLayoutPoint(
                        element.shape.x_min * conversion_factor,
                        page_height - element.shape.y_max * conversion_factor,
                        base_units,
                    ),
                    useReferencePoint=False,
                )

        LayoutConverter.process_element_border_background_shadow(
            layout, element, item, page_height, context, base_units, conversion_factor
        )

        if element.locked:
            item.setLocked(True)

    @staticmethod
    def process_element_border_background_shadow(
        layout,
        element: Element,
        item,
        page_height,
        context,
        base_units,
        conversion_factor,
    ):
        use_simple_background = False
        use_complex_background = False
        use_simple_border = False
        use_complex_border = False

        if isinstance(element, Element):
            has_border = bool(element.border)
            border_gap_x = element.border.gap_x if has_border else 0
            border_gap_y = element.border.gap_y if has_border else 0
            border_rounding = element.border.rounding if has_border else 0
            border_symbol = element.border.symbol if has_border else None

            has_background = bool(element.background)
            background_gap_x = element.background.gap_x if has_background else 0
            background_gap_y = element.background.gap_y if has_background else 0
            background_rounding = element.background.rounding if has_background else 0
            background_symbol = element.background.symbol if has_background else None

            has_shadow = bool(element.shadow)
            shadow_symbol = element.shadow.symbol if has_shadow else None
            shadow_x_offset = element.shadow.x_offset if has_shadow else 0
            shadow_y_offset = element.shadow.y_offset if has_shadow else 0
            x_max = (
                element.shape.x_max if not isinstance(element.shape, Point) else None
            )
            x_min = (
                element.shape.x_min if not isinstance(element.shape, Point) else None
            )
            y_max = (
                element.shape.y_max if not isinstance(element.shape, Point) else None
            )
            y_min = (
                element.shape.y_min if not isinstance(element.shape, Point) else None
            )
        if has_border:
            if border_gap_x == 0 and border_gap_y == 0 and border_rounding == 0:
                use_simple_border = True
            else:
                use_complex_border = True
        if has_background:
            if (
                background_gap_x == 0
                and background_gap_y == 0
                and background_rounding == 0
            ):
                use_simple_background = True
            else:
                use_complex_background = True
        if has_shadow:
            use_complex_background = True
            use_simple_background = False

        merge_complex_border_background = False
        if use_complex_border and use_complex_background:
            if not has_background:
                merge_complex_border_background = True
            else:
                merge_complex_border_background = (
                    border_gap_x == background_gap_x
                    and border_gap_y == background_gap_y
                    and border_rounding == background_rounding
                )

        if use_simple_border and item is not None:
            color = SymbolConverter.symbol_to_color(border_symbol, context)
            if color.alpha() != 0:
                item.setFrameEnabled(True)
                item.setFrameStrokeColor(color)
            else:
                item.setFrameEnabled(False)

            stroke_width = SymbolConverter.symbol_to_line_width(border_symbol, context)
            if context.units == QgsUnitTypes.RenderUnit.RenderMillimeters:
                stroke_width /= POINTS_TO_MM

            item.setFrameStrokeWidth(
                QgsLayoutMeasurement(stroke_width, QgsUnitTypes.LayoutUnit.LayoutPoints)
            )
        elif item is not None:
            item.setFrameEnabled(False)

        if use_simple_background and item is not None:
            item.setBackgroundEnabled(True)
            item.setBackgroundColor(
                SymbolConverter.symbol_to_color(background_symbol, context)
            )
        elif item is not None:
            item.setBackgroundEnabled(False)

        created_items = []
        if use_complex_background or use_complex_border or item is None:
            pts_to_layout = (
                layout.renderContext()
                .measurementConverter()
                .convert(
                    QgsLayoutMeasurement(1, QgsUnitTypes.LayoutUnit.LayoutPoints),
                    base_units,
                )
                .length()
            )

            if use_complex_background:
                shape = QgsLayoutItemShape(layout)
                shape.setShapeType(QgsLayoutItemShape.Shape.Rectangle)
                created_items.append(shape)

                symbol = None
                if has_shadow:
                    symbol = SymbolConverter.Symbol_to_QgsSymbol(shadow_symbol, context)
                    for l in range(symbol.symbolLayerCount()):
                        layer = symbol.symbolLayer(l)
                        if isinstance(layer, QgsSimpleFillSymbolLayer):
                            layer.setOffset(QPointF(shadow_x_offset, -shadow_y_offset))
                            layer.setOffsetUnit(QgsUnitTypes.RenderUnit.RenderPoints)

                if has_background:
                    symbol_background = SymbolConverter.Symbol_to_QgsSymbol(
                        background_symbol, context
                    )
                    if not symbol:
                        symbol = symbol_background
                    else:
                        for symbol_layer in range(symbol_background.symbolLayerCount()):
                            symbol.appendSymbolLayer(
                                symbol_background.symbolLayer(symbol_layer).clone()
                            )

                if merge_complex_border_background:
                    symbol2 = SymbolConverter.Symbol_to_QgsSymbol(
                        border_symbol, context
                    )
                    for symbol_layer in range(symbol2.symbolLayerCount()):
                        symbol.appendSymbolLayer(
                            symbol2.symbolLayer(symbol_layer).clone()
                        )

                shape.setSymbol(symbol)

                if (
                    x_max is not None
                    and not math.isnan(x_max)
                    and y_max is not None
                    and not math.isnan(y_max)
                    and x_min is not None
                    and not math.isnan(x_min)
                    and y_min is not None
                    and not math.isnan(y_min)
                ):
                    shape.attemptResize(
                        QgsLayoutSize(
                            x_max * conversion_factor
                            - x_min * conversion_factor
                            + 2
                            * pts_to_layout
                            * (background_gap_x if has_background else 0),
                            y_max * conversion_factor
                            - y_min * conversion_factor
                            + 2
                            * pts_to_layout
                            * (background_gap_y if has_background else 0),
                            base_units,
                        )
                    )
                else:
                    shape.setCustomProperty(
                        "deferred_size_adjust_x",
                        2 * pts_to_layout * (background_gap_x if has_background else 0),
                    )
                    shape.setCustomProperty(
                        "deferred_size_adjust_y",
                        2 * pts_to_layout * (background_gap_y if has_background else 0),
                    )

                shape.setReferencePoint(LayoutConverter.ANCHOR_MAP[element.anchor])
                if (
                    x_min is not None
                    and not math.isnan(x_min)
                    and y_max is not None
                    and not math.isnan(y_max)
                ):
                    shape.attemptMove(
                        QgsLayoutPoint(
                            x_min * conversion_factor
                            - pts_to_layout
                            * (background_gap_x if has_background else 0),
                            page_height
                            - y_max * conversion_factor
                            - pts_to_layout
                            * (background_gap_y if has_background else 0),
                            base_units,
                        ),
                        useReferencePoint=False,
                    )
                else:
                    shape.setCustomProperty(
                        "deferred_pos_adjust_x",
                        -pts_to_layout * (background_gap_x if has_background else 0),
                    )
                    shape.setCustomProperty(
                        "deferred_pos_adjust_y",
                        -pts_to_layout * (background_gap_y if has_background else 0),
                    )

                if has_background and background_rounding > 0:
                    size_in_mm = (
                        layout.renderContext()
                        .measurementConverter()
                        .convert(
                            shape.sizeWithUnits(),
                            QgsUnitTypes.LayoutUnit.LayoutMillimeters,
                        )
                    )
                    size_smallest = min(size_in_mm.width(), size_in_mm.height())
                    rounding_in_mm = size_smallest / 2 * background_rounding / 100
                    shape.setCornerRadius(
                        QgsLayoutMeasurement(
                            rounding_in_mm, QgsUnitTypes.LayoutUnit.LayoutMillimeters
                        )
                    )

                layout.addLayoutItem(shape)
                layout.updateZValues(False)

            if use_complex_border and not merge_complex_border_background:
                shape = QgsLayoutItemShape(layout)
                shape.setShapeType(QgsLayoutItemShape.Shape.Rectangle)
                created_items.append(shape)

                symbol_source = SymbolConverter.Symbol_to_QgsSymbol(
                    border_symbol, context
                )
                symbol = QgsFillSymbol()
                symbol.deleteSymbolLayer(0)
                for symbol_layer in range(symbol_source.symbolLayerCount()):
                    symbol.appendSymbolLayer(
                        symbol_source.symbolLayer(symbol_layer).clone()
                    )

                shape.setSymbol(symbol)

                if (
                    not math.isnan(x_max)
                    and not math.isnan(y_max)
                    and not math.isnan(x_min)
                    and not math.isnan(y_min)
                ):
                    shape.attemptResize(
                        QgsLayoutSize(
                            x_max * conversion_factor
                            - x_min * conversion_factor
                            + 2 * pts_to_layout * border_gap_x,
                            y_max * conversion_factor
                            - y_min * conversion_factor
                            + 2 * pts_to_layout * border_gap_y,
                            base_units,
                        )
                    )
                else:
                    shape.setCustomProperty(
                        "deferred_size_adjust_x", 2 * pts_to_layout * border_gap_x
                    )
                    shape.setCustomProperty(
                        "deferred_size_adjust_y", 2 * pts_to_layout * border_gap_y
                    )

                shape.setReferencePoint(LayoutConverter.ANCHOR_MAP[element.anchor])
                if not math.isnan(x_min) and not math.isnan(y_max):
                    shape.attemptMove(
                        QgsLayoutPoint(
                            x_min * conversion_factor - pts_to_layout * border_gap_x,
                            page_height
                            - y_max * conversion_factor
                            - pts_to_layout * border_gap_y,
                            base_units,
                        ),
                        useReferencePoint=False,
                    )
                else:
                    shape.setCustomProperty(
                        "deferred_pos_adjust_x", -pts_to_layout * border_gap_x
                    )
                    shape.setCustomProperty(
                        "deferred_pos_adjust_y", -pts_to_layout * border_gap_y
                    )

                if border_rounding > 0:
                    size_in_mm = (
                        layout.renderContext()
                        .measurementConverter()
                        .convert(
                            shape.sizeWithUnits(),
                            QgsUnitTypes.LayoutUnit.LayoutMillimeters,
                        )
                    )
                    size_smallest = min(size_in_mm.width(), size_in_mm.height())
                    rounding_in_mm = size_smallest / 2 * border_rounding / 100
                    shape.setCornerRadius(
                        QgsLayoutMeasurement(
                            rounding_in_mm, QgsUnitTypes.LayoutUnit.LayoutMillimeters
                        )
                    )

                layout.addLayoutItem(shape)
                layout.updateZValues(False)

        return created_items

    @staticmethod
    def get_layer(layer, layer_to_layer_map) -> Tuple[object, Optional[QgsMapLayer]]:
        if isinstance(layer, str):
            return None, None
        else:
            return layer, layer_to_layer_map.get(layer)

    @staticmethod
    def convert_element(
        element,
        layout: QgsPrintLayout,
        page_height,
        context: Context,
        base_units,
        conversion_factor,
        layer_to_layer_map,
    ):
        context.element_name = None

        if isinstance(element, (GroupElement,)):
            children = {}
            background_shape_items = []

            if isinstance(element, GroupElement) and (
                element.background or element.border or element.shadow
            ):
                background_shape_items = (
                    LayoutConverter.process_element_border_background_shadow(
                        layout,
                        element,
                        None,
                        page_height,
                        context,
                        base_units,
                        conversion_factor,
                    )
                )
                for c in background_shape_items:
                    c.setId("background shape for group")

            for e in element.elements:
                res = LayoutConverter.convert_element(
                    e,
                    layout,
                    page_height,
                    context,
                    base_units,
                    conversion_factor,
                    layer_to_layer_map,
                )
                if res is not None:
                    for child_e, child_i in res.items():
                        children[child_e] = child_i
            if children:
                group_children = [i for i in children.values() if not i.isGroupMember()]
                group = layout.groupItems(group_children)

                if group:
                    for background_shape_item in background_shape_items:
                        background_shape_item.attemptSetSceneRect(
                            QRectF(
                                group.pos().x(),
                                group.pos().y(),
                                group.rect().width(),
                                group.rect().height(),
                            )
                        )

                        base_units_to_layout = layout.convertToLayoutUnits(
                            QgsLayoutMeasurement(1, base_units)
                        )

                        size_adjust_x = (
                            background_shape_item.customProperty(
                                "deferred_size_adjust_x"
                            )
                            or 0
                        )
                        size_adjust_y = (
                            background_shape_item.customProperty(
                                "deferred_size_adjust_y"
                            )
                            or 0
                        )
                        pos_adjust_x = (
                            background_shape_item.customProperty(
                                "deferred_pos_adjust_x"
                            )
                            or 0
                        )
                        pos_adjust_y = (
                            background_shape_item.customProperty(
                                "deferred_pos_adjust_y"
                            )
                            or 0
                        )

                        if (
                            size_adjust_x
                            or size_adjust_y
                            or pos_adjust_x
                            or pos_adjust_y
                        ):
                            background_shape_item.attemptSetSceneRect(
                                QRectF(
                                    background_shape_item.pos().x()
                                    + base_units_to_layout * pos_adjust_x,
                                    background_shape_item.pos().y()
                                    + base_units_to_layout * pos_adjust_y,
                                    background_shape_item.rect().width()
                                    + base_units_to_layout * size_adjust_x,
                                    background_shape_item.rect().height()
                                    + base_units_to_layout * size_adjust_y,
                                )
                            )

                    children[element] = group
                return children
            else:
                return None

        elif isinstance(element, (MapFrame,)):
            map = QgsLayoutItemMap(layout)

            if element.map.crs:
                map.setCrs(CrsConverter.convert_crs(element.map.crs, context))

            LayoutConverter.set_common_properties(
                layout,
                element,
                map,
                page_height,
                context,
                base_units,
                conversion_factor,
            )

            rect = QgsRectangle(
                element.map.full_extent_x_min,
                element.map.full_extent_y_min,
                element.map.full_extent_x_max,
                element.map.full_extent_y_max,
            )
            map.zoomToExtent(rect)
            map.setMapRotation(ConversionUtils.convert_angle(element.map.rotation))

            if len(layout.project().mapThemeCollection().mapThemes()) > 1:
                map.setFollowVisibilityPreset(True)
                map.setFollowVisibilityPresetName(layer_to_layer_map[element.map])

            if True:
                map.setId(element.map.name)

            # grids
            for g in element.grids:
                if isinstance(g, (MeasuredGrid, Graticule)):
                    if (
                        g.border
                        and isinstance(g.border, SimpleMapGridBorder)
                        and g.border.line_symbol
                    ):
                        border = QgsLayoutItemMapGrid(g.name + " border", map)
                        border.setStyle(
                            QgsLayoutItemMapGrid.GridStyle.FrameAnnotationsOnly
                        )
                        border.setFrameStyle(QgsLayoutItemMapGrid.FrameStyle.LineBorder)

                        stroke_width = SymbolConverter.symbol_to_line_width(
                            g.border.line_symbol, context
                        )
                        if context.units == QgsUnitTypes.RenderUnit.RenderPoints:
                            stroke_width *= POINTS_TO_MM
                        border.setFramePenSize(stroke_width)
                        border.setFramePenColor(
                            SymbolConverter.symbol_to_color(
                                g.border.line_symbol, context
                            )
                        )
                        map.grids().addGrid(border)

                    grid = QgsLayoutItemMapGrid(g.name, map)
                    if isinstance(g, MeasuredGrid) and g.crs:
                        grid.setCrs(CrsConverter.convert_crs(g.crs, context))
                    elif isinstance(g, Graticule):
                        grid.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))

                    grid_units, scale_factor = LayoutConverter.units_to_distance_units(
                        g.units
                    )
                    crs_units = (
                        grid.crs() if grid.crs().isValid() else map.crs()
                    ).mapUnits()
                    scale_factor *= QgsUnitTypes.fromUnitToUnitFactor(
                        grid_units, crs_units
                    )

                    grid.setIntervalX(g.x_interval_size * scale_factor)
                    grid.setIntervalY(g.y_interval_size * scale_factor)
                    # unknown if scale_factor should be considered here!!
                    grid.setOffsetX(g.x_origin * scale_factor)
                    grid.setOffsetY(g.y_origin * scale_factor)
                    grid.setEnabled(g.visible)

                    if g.line_symbol:
                        grid.setLineSymbol(
                            SymbolConverter.Symbol_to_QgsSymbol(g.line_symbol, context)
                        )
                    elif g.tick_mark_symbol:
                        grid.setStyle(QgsLayoutItemMapGrid.GridStyle.Markers)
                        grid.setMarkerSymbol(
                            SymbolConverter.Symbol_to_QgsSymbol(
                                g.tick_mark_symbol, context
                            )
                        )
                    else:
                        grid.setStyle(
                            QgsLayoutItemMapGrid.GridStyle.FrameAnnotationsOnly
                        )

                    grid.setFrameSideFlag(
                        QgsLayoutItemMapGrid.FrameSideFlag.FrameBottom,
                        g.major_ticks_bottom,
                    )
                    grid.setFrameSideFlag(
                        QgsLayoutItemMapGrid.FrameSideFlag.FrameTop, g.major_ticks_top
                    )
                    grid.setFrameSideFlag(
                        QgsLayoutItemMapGrid.FrameSideFlag.FrameLeft, g.major_ticks_left
                    )
                    grid.setFrameSideFlag(
                        QgsLayoutItemMapGrid.FrameSideFlag.FrameRight,
                        g.major_ticks_right,
                    )

                    if g.label_format:
                        grid.setAnnotationEnabled(True)
                        if isinstance(g.label_format, CornerGridLabel):
                            text_symbol = g.label_format.grid_label_text_symbol
                        else:
                            text_symbol = g.label_format.text_symbol
                        number_format = g.label_format.number_format

                        text_format = TextSymbolConverter.text_symbol_to_qgstextformat(
                            text_symbol, context
                        )
                        grid.setAnnotationFont(text_format.toQFont())
                        grid.setAnnotationFontColor(text_format.color())
                        grid.setAnnotationDisplay(
                            QgsLayoutItemMapGrid.DisplayMode.ShowAll
                            if g.annotations_left
                            else QgsLayoutItemMapGrid.DisplayMode.HideAll,
                            QgsLayoutItemMapGrid.BorderSide.Left,
                        )
                        grid.setAnnotationDisplay(
                            QgsLayoutItemMapGrid.DisplayMode.ShowAll
                            if g.annotations_right
                            else QgsLayoutItemMapGrid.DisplayMode.HideAll,
                            QgsLayoutItemMapGrid.BorderSide.Right,
                        )
                        grid.setAnnotationDisplay(
                            QgsLayoutItemMapGrid.DisplayMode.ShowAll
                            if g.annotations_bottom
                            else QgsLayoutItemMapGrid.DisplayMode.HideAll,
                            QgsLayoutItemMapGrid.BorderSide.Bottom,
                        )
                        grid.setAnnotationDisplay(
                            QgsLayoutItemMapGrid.DisplayMode.ShowAll
                            if g.annotations_top
                            else QgsLayoutItemMapGrid.DisplayMode.HideAll,
                            QgsLayoutItemMapGrid.BorderSide.Top,
                        )

                        annotation_precision = (
                            NumericFormatConverter.decimal_precision_from_format(
                                number_format
                            )
                            if number_format
                            else None
                        )
                        show_directions = True
                        if isinstance(number_format, LatLonFormat):
                            show_directions = number_format.show_directions

                        if annotation_precision is not None:
                            grid.setAnnotationPrecision(annotation_precision)

                        grid.setAnnotationFrameDistance(
                            g.label_format.label_offset * POINTS_TO_MM
                            - abs(g.tick_length) * POINTS_TO_MM
                        )

                        grid.setAnnotationDirection(
                            QgsLayoutItemMapGrid.AnnotationDirection.Horizontal
                            if g.label_format.left_align_hoz
                            else QgsLayoutItemMapGrid.AnnotationDirection.Vertical,
                            QgsLayoutItemMapGrid.BorderSide.Left,
                        )
                        grid.setAnnotationDirection(
                            QgsLayoutItemMapGrid.AnnotationDirection.Horizontal
                            if g.label_format.bottom_align_hoz
                            else QgsLayoutItemMapGrid.AnnotationDirection.VerticalDescending,
                            QgsLayoutItemMapGrid.BorderSide.Bottom,
                        )
                        grid.setAnnotationDirection(
                            QgsLayoutItemMapGrid.AnnotationDirection.Horizontal
                            if g.label_format.top_align_hoz
                            else QgsLayoutItemMapGrid.AnnotationDirection.Vertical,
                            QgsLayoutItemMapGrid.BorderSide.Top,
                        )
                        grid.setAnnotationDirection(
                            QgsLayoutItemMapGrid.AnnotationDirection.Horizontal
                            if g.label_format.right_align_hoz
                            else QgsLayoutItemMapGrid.AnnotationDirection.Vertical,
                            QgsLayoutItemMapGrid.BorderSide.Right,
                        )

                        if isinstance(g.label_format, DMSGridLabel):
                            if g.label_format.label_type in (
                                DMSGridLabelType.Standard,
                                DMSGridLabelType.DecimalSeconds,
                                DMSGridLabelType.MinutesStackedOverSeconds,
                            ):
                                if show_directions:
                                    grid.setAnnotationFormat(
                                        QgsLayoutItemMapGrid.AnnotationFormat.DegreeMinuteSecond
                                    )
                                else:
                                    grid.setAnnotationFormat(
                                        QgsLayoutItemMapGrid.AnnotationFormat.DegreeMinuteSecondNoSuffix
                                    )
                            elif (
                                g.label_format.label_type
                                == DMSGridLabelType.DecimalDegrees
                            ):
                                if show_directions:
                                    grid.setAnnotationFormat(
                                        QgsLayoutItemMapGrid.AnnotationFormat.DecimalWithSuffix
                                    )
                                else:
                                    grid.setAnnotationFormat(
                                        QgsLayoutItemMapGrid.AnnotationFormat.Decimal
                                    )
                            elif (
                                g.label_format.label_type
                                == DMSGridLabelType.DecimalMinutes
                            ):
                                if show_directions:
                                    grid.setAnnotationFormat(
                                        QgsLayoutItemMapGrid.AnnotationFormat.DegreeMinute
                                    )
                                else:
                                    grid.setAnnotationFormat(
                                        QgsLayoutItemMapGrid.AnnotationFormat.DegreeMinuteNoSuffix
                                    )

                    if g.tick_line_symbol:
                        grid.setFrameWidth(abs(g.tick_length) * POINTS_TO_MM)
                        stroke_width = SymbolConverter.symbol_to_line_width(
                            g.tick_line_symbol, context
                        )
                        if context.units == QgsUnitTypes.RenderUnit.RenderPoints:
                            stroke_width *= POINTS_TO_MM
                        grid.setFramePenSize(stroke_width)
                        grid.setFramePenColor(
                            SymbolConverter.symbol_to_color(g.tick_line_symbol, context)
                        )

                        grid.setFrameStyle(
                            QgsLayoutItemMapGrid.FrameStyle.ExteriorTicks
                            if g.tick_length > 0
                            else QgsLayoutItemMapGrid.FrameStyle.InteriorTicks
                        )
                    else:
                        grid.setFrameStyle(QgsLayoutItemMapGrid.FrameStyle.NoFrame)

                    map.grids().addGrid(grid)
                else:
                    context.push_warning(
                        "{} grid conversion is not yet supported".format(
                            g.__class__.__name__
                        ),
                        level=Context.CRITICAL,
                    )

            layout.addLayoutItem(map)
            return {element: map}

        elif isinstance(element, TableFrame):
            table = QgsLayoutItemAttributeTable(layout)

            original_linked_layer, converted_linked_layer = LayoutConverter.get_layer(
                element.table, layer_to_layer_map
            )
            if not converted_linked_layer:
                # this is probably fixable -- we'd need to load the layer here now. But that's a lot of code juggling
                context.push_warning(
                    "Could not restore table item: layer {} was not found".format(
                        element.table.name
                    ),
                    level=Context.CRITICAL,
                )
            else:
                table.setVectorLayer(converted_linked_layer)

            table_width = QgsLayoutMeasurement(
                element.shape.x_max * conversion_factor
                - element.shape.x_min * conversion_factor,
                base_units,
            )
            table_width_in_mm = (
                layout.renderContext()
                .measurementConverter()
                .convert(table_width, QgsUnitTypes.LayoutUnit.LayoutMillimeters)
                .length()
            )

            columns = []
            total_width = 0
            for idx, info in enumerate(element.fields.field_info):
                field = element.fields.fields[idx]
                if info.visible:
                    col = QgsLayoutTableColumn()
                    col.setAttribute(field.name)
                    col.setHeading(info.alias)
                    col.setWidth(
                        0.26 * element.fields.field_widths[field.name]
                    )  # based on 96 dpi
                    total_width += col.width()
                    if total_width > table_width_in_mm:
                        break

                    columns.append(col)

            cell_font, _, _ = TextSymbolConverter.std_font_to_qfont(
                element.table_property.cell_font
            )
            table.setContentFont(cell_font)
            cell_color = ColorConverter.color_to_qcolor(
                element.table_property.cell_text_color
            )
            table.setContentFontColor(cell_color)

            font = element.table_property.heading_font
            # seems to force this at render time only..
            font.weight = 800

            header_font, _, _ = TextSymbolConverter.std_font_to_qfont(font)
            table.setHeaderFont(header_font)
            header_color = ColorConverter.color_to_qcolor(
                element.table_property.heading_text_color
            )
            table.setHeaderFontColor(header_color)
            table.setHeaderHAlignment(QgsLayoutTable.HeaderHAlignment.HeaderCenter)

            table.setColumns(columns)

            layout.addMultiFrame(table)

            frame = QgsLayoutFrame(layout, table)
            LayoutConverter.set_common_properties(
                layout,
                element,
                frame,
                page_height,
                context,
                base_units,
                conversion_factor,
            )
            table.addFrame(frame)

            table.refresh()

            return {element: frame}
        elif isinstance(
            element,
            (
                PictureElement,
                BmpPictureElement,
                PngPictureElement,
                JpgPictureElement,
                Jp2PictureElement,
                EmfPictureElement,
                GifPictureElement,
                TifPictureElement,
            ),
        ):
            picture = QgsLayoutItemPicture(layout)
            picture.setResizeMode(QgsLayoutItemPicture.ResizeMode.Stretch)
            LayoutConverter.set_common_properties(
                layout,
                element,
                picture,
                page_height,
                context,
                base_units,
                conversion_factor,
            )

            picture_path, is_svg = AnnotationConverter.picture_element_to_path(
                element, context
            )

            if is_svg is not None:
                picture.setPicturePath(
                    picture_path,
                    QgsLayoutItemPicture.Format.FormatSVG
                    if is_svg
                    else QgsLayoutItemPicture.Format.FormatRaster,
                )
            else:
                picture.setPicturePath(picture_path)

            layout.addLayoutItem(picture)
            return {element: picture}

        elif isinstance(element, RectangleElement):
            shape = QgsLayoutItemShape(layout)
            shape.setShapeType(QgsLayoutItemShape.Shape.Rectangle)
            shape.setSymbol(
                SymbolConverter.Symbol_to_QgsSymbol(element.symbol, context)
            )
            LayoutConverter.set_common_properties(
                layout,
                element,
                shape,
                page_height,
                context,
                base_units,
                conversion_factor,
            )
            layout.addLayoutItem(shape)
            return {element: shape}

        elif isinstance(element, FrameElement):
            shape = QgsLayoutItemShape(layout)
            shape.setShapeType(QgsLayoutItemShape.Shape.Rectangle)

            fill_symbol = SymbolConverter.convert_border_background_shadow(
                border=element.border,
                background=element.background,
                shadow=element.shadow,
                context=context,
            )

            shape.setSymbol(fill_symbol)
            LayoutConverter.set_common_properties(
                layout,
                element,
                shape,
                page_height,
                context,
                base_units,
                conversion_factor,
            )
            layout.addLayoutItem(shape)
            return {element: shape}

        elif isinstance(element, PolygonElement):
            shape = QgsLayoutItemPolygon(layout)
            try:
                shape.setSymbol(
                    SymbolConverter.Symbol_to_QgsSymbol(element.symbol, context)
                )
            except NotImplementedException as e:
                context.push_warning(
                    "{}: Cannot convert polygon fill symbol of type {}".format(
                        element.element_name or layout.name(),
                        e.original_object.__class__.__name__,
                    ),
                    level=Context.CRITICAL,
                )
                return {}

            points = element.shape.parts[0]
            shape.setNodes(
                QPolygonF([QPointF(p[0], page_height - p[1]) for p in points])
            )

            LayoutConverter.set_common_properties(
                layout,
                element,
                shape,
                page_height,
                context,
                base_units,
                conversion_factor,
            )
            layout.addLayoutItem(shape)
            return {element: shape}

        elif isinstance(element, (CircleElement, EllipseElement)):
            shape = QgsLayoutItemShape(layout)
            shape.setShapeType(QgsLayoutItemShape.Shape.Ellipse)
            shape.setSymbol(
                SymbolConverter.Symbol_to_QgsSymbol(element.symbol, context)
            )
            LayoutConverter.set_common_properties(
                layout,
                element,
                shape,
                page_height,
                context,
                base_units,
                conversion_factor,
            )
            layout.addLayoutItem(shape)
            return {element: shape}

        elif isinstance(element, LineElement):
            shape = QgsLayoutItemPolyline(layout)
            shape.setSymbol(
                SymbolConverter.Symbol_to_QgsSymbol(element.symbol, context)
            )

            points = element.shape.parts[0]
            shape.setNodes(
                QPolygonF([QPointF(p[0], page_height - p[1]) for p in points])
            )

            LayoutConverter.set_common_properties(
                layout,
                element,
                shape,
                page_height,
                context,
                base_units,
                conversion_factor,
            )
            layout.addLayoutItem(shape)
            return {element: shape}

        elif isinstance(element, MarkerElement):
            if USE_LAYOUT_MARKER:
                if isinstance(element.symbol, PieChartSymbol):
                    context.push_warning(
                        "Cannot convert pie chart symbol to marker element: QGIS does not support pie charts as layout items",
                        level=Context.CRITICAL,
                    )
                    return None

                if isinstance(element.shape, Point) and (
                    element.shape.x < -214740 or element.shape.y < -214740
                ):
                    # seen on some corrupted documents??
                    return {}

                shape = QgsLayoutItemMarker(layout)

                try:
                    marker = SymbolConverter.Symbol_to_QgsSymbol(
                        element.symbol, context
                    )
                except NotImplementedException as e:
                    context.push_warning(
                        "Cannot convert marker element: {}".format(str(e)),
                        level=Context.CRITICAL,
                    )
                    return None

                shape.setSymbol(marker)
                LayoutConverter.set_common_properties(
                    layout,
                    element,
                    shape,
                    page_height,
                    context,
                    base_units,
                    conversion_factor,
                )
                layout.addLayoutItem(shape)
                return {element: shape}
            else:
                # have to convert to rectangles with a centroid fill, that's the closest we can get
                shape = QgsLayoutItemShape(layout)
                shape.setShapeType(QgsLayoutItemShape.Shape.Rectangle)

                render_context = QgsLayoutUtils.createRenderContextForLayout(
                    layout, None
                )
                centroid_marker = SymbolConverter.Symbol_to_QgsSymbol(
                    element.symbol, context
                )
                centroid_marker.startRender(render_context)
                bounds = centroid_marker.bounds(QPointF(0, 0), render_context)
                centroid_marker.stopRender(render_context)

                fill_symbol = QgsFillSymbol()
                layer = QgsCentroidFillSymbolLayer()
                layer.setSubSymbol(centroid_marker)
                fill_symbol.changeSymbolLayer(0, layer)

                shape.setSymbol(fill_symbol)
                LayoutConverter.set_common_properties(
                    layout,
                    element,
                    shape,
                    page_height,
                    context,
                    base_units,
                    conversion_factor,
                )

                layout_bounds = layout.convertFromLayoutUnits(
                    bounds.size(), layout.units()
                )
                shape.setReferencePoint(QgsLayoutItem.ReferencePoint.Middle)
                shape.attemptResize(
                    QgsLayoutSize(
                        layout_bounds.width() * 1.1,
                        layout_bounds.height() * 1.1,
                        layout_bounds.units(),
                    )
                )
                layout.addLayoutItem(shape)
                return {element: shape}

        elif isinstance(element, (TextElement, ParagraphTextElement)) or (False):
            if (
                isinstance(element, Element)
                and isinstance(element.shape, Point)
                and (element.shape.x < -214740 or element.shape.y < -214740)
            ):
                # seen on some corrupted documents??
                return {}

            label = QgsLayoutItemLabel(layout)
            LayoutConverter.set_common_properties(
                layout,
                element,
                label,
                page_height,
                context,
                base_units,
                conversion_factor,
            )

            if isinstance(element, Element):
                text_symbol = element.text_symbol
            else:
                text_symbol = element.graphic.symbol.symbol

            halign = TextSymbolConverter.convert_horizontal_alignment(text_symbol)

            if isinstance(element, Element):
                text = element.text or ""
            else:
                text = element.graphic.text or ""

            # justify alignment looks different in QGIS if we aren't
            # rendering as HTML
            force_html = halign == Qt.AlignmentFlag.AlignJustify

            text = LayoutConverter.convert_dynamic_text(text, context)
            text, is_html = LayoutConverter.convert_html(text, context, force_html)
            text_format = TextSymbolConverter.text_symbol_to_qgstextformat(
                text_symbol, context
            )
            font = text_format.toQFont()

            vertical_alignment, is_baseline = (
                TextSymbolConverter.convert_vertical_alignment(text_symbol)
            )

            if is_html:
                # maybe it's html, but it's just a single character format?
                if not force_html and Qgis.QGIS_VERSION_INT >= 32800:
                    from qgis.core import QgsTextDocument, QgsTextCharacterFormat

                    doc = QgsTextDocument.fromHtml([text])
                    if len(doc) == 1 and len(doc[0]) == 1:
                        text = doc[0][0].text()
                        char_format = doc[0][0].characterFormat()

                        context = QgsLayoutUtils.createRenderContextForLayout(
                            layout, None
                        )
                        context.setFlag(
                            QgsRenderContext.Flag.ApplyScalingWorkaroundForTextRendering
                        )

                        char_format.updateFontForFormat(font, context)

                        text_format.setFont(font)
                        if char_format.fontPointSize() > 0:
                            text_format.setSize(char_format.fontPointSize())
                            text_format.setSizeUnit(
                                QgsUnitTypes.RenderUnit.RenderPoints
                            )

                        text_format.setNamedStyle(font.styleName())
                        if (
                            char_format.italic()
                            == QgsTextCharacterFormat.BooleanValue.SetTrue
                        ):
                            text_format.setForcedItalic(True)
                        elif (
                            char_format.italic()
                            == QgsTextCharacterFormat.BooleanValue.SetFalse
                        ):
                            text_format.setForcedItalic(False)
                        is_html = False
                    else:
                        label.setMode(QgsLayoutItemLabel.Mode.ModeHtml)
                else:
                    label.setMode(QgsLayoutItemLabel.Mode.ModeHtml)

                if is_html:
                    # in some circumstances we want to force the QGIS text renderer:
                    if (
                        (
                            Qgis.QGIS_VERSION_INT >= 32400
                            and (
                                text_format.buffer().enabled()
                                or text_format.shadow().enabled()
                                or text_format.background().enabled()
                            )
                        )
                        or (
                            Qgis.QGIS_VERSION_INT >= 34200
                            and '<div style="margin-top:' in text
                        )
                    ) or (False):
                        is_html = False
                        label.setMode(QgsLayoutItemLabel.Mode.ModeFont)
                        text_format.setAllowHtmlFormatting(True)

            else:
                text = text.replace("\r", "")
                if Qgis.QGIS_VERSION_INT < 32400 and text[-1:] == "\n":
                    # UNSURE: If there's a trailing newline on this trimming messes
                    # up the conversion code which handles anchor points and eg bottom aligned
                    # text...! So we just leave it in now. Maybe this also should be skipped for
                    # older QGIS too?
                    text = text[:-1]

            label.setText(text)

            if Qgis.QGIS_VERSION_INT >= 32400:
                label.setTextFormat(text_format)
            else:
                context.push_warning(
                    "Conversion of layout labels is much improved in QGIS 3.24 or later",
                    level=Context.WARNING,
                )
                label.setFont(font)
            label.setFontColor(text_format.color())

            label.setMargin(0)
            is_left_align = halign in (
                Qt.AlignmentFlag.AlignLeft,
                Qt.AlignmentFlag.AlignJustify,
            )
            is_middle_align = halign == Qt.AlignmentFlag.AlignHCenter
            is_right_align = halign == Qt.AlignmentFlag.AlignRight

            if isinstance(element, TextElement) or (False):
                label_size = LayoutConverter.label_size_for_text(label)

                if label.font().italic():
                    # grow label a little wider to account for
                    # italic characters
                    try:
                        label_size.setWidth(
                            label_size.width()
                            + QFontMetricsF(label.font()).horizontalAdvance("x")
                            * 0.2
                            * POINTS_TO_MM
                        )
                    except AttributeError:
                        label_size.setWidth(
                            label_size.width()
                            + QFontMetricsF(label.font()).width("x")
                            * 0.2
                            * POINTS_TO_MM
                        )
                x = label.scenePos().x()
                y = label.scenePos().y()

                if isinstance(element, (TextElement,)) or (False):
                    # for labels matching alignment with anchor point,
                    # increase the label width a bit to avoid
                    # unwanted word wrap
                    if (
                        (
                            is_left_align
                            and label.referencePoint()
                            in (
                                QgsLayoutItem.ReferencePoint.UpperLeft,
                                QgsLayoutItem.ReferencePoint.MiddleLeft,
                                QgsLayoutItem.ReferencePoint.LowerLeft,
                            )
                        )
                        or (
                            is_middle_align
                            and label.referencePoint()
                            in (
                                QgsLayoutItem.ReferencePoint.UpperMiddle,
                                QgsLayoutItem.ReferencePoint.Middle,
                                QgsLayoutItem.ReferencePoint.LowerMiddle,
                            )
                        )
                        or (
                            is_right_align
                            and label.referencePoint()
                            in (
                                QgsLayoutItem.ReferencePoint.UpperRight,
                                QgsLayoutItem.ReferencePoint.MiddleRight,
                                QgsLayoutItem.ReferencePoint.LowerRight,
                            )
                        )
                    ):
                        if "[%" in label.text():
                            # as we don't know the actual label text (we
                            # aren't evaluating it against anything),
                            # increasing the width a fair bit...

                            # We need to fix this in QGIS!
                            label_size.setWidth(label_size.width() * 1.5)

                if is_right_align:
                    x -= label_size.width()
                elif is_middle_align:
                    x -= label_size.width() / 2

                if vertical_alignment == Qt.AlignmentFlag.AlignTop:
                    # nothing to do, everything is perfect already
                    pass
                elif vertical_alignment == Qt.AlignmentFlag.AlignVCenter:
                    if not is_html:
                        label.setVAlign(Qt.AlignmentFlag.AlignVCenter)
                    y -= label_size.height() / 2
                elif (
                    vertical_alignment == Qt.AlignmentFlag.AlignBottom
                    and not is_baseline
                ):
                    if not is_html:
                        label.setVAlign(Qt.AlignmentFlag.AlignBottom)
                    y -= label_size.height()
                elif vertical_alignment == Qt.AlignmentFlag.AlignBottom and is_baseline:
                    if not is_html:
                        label.setVAlign(Qt.AlignmentFlag.AlignBottom)
                        f = label.font()
                    else:
                        # get font for last line in document
                        doc = QTextDocument()
                        doc.setDefaultStyleSheet(
                            LayoutConverter.create_stylesheet_for_label(label)
                        )
                        doc.setDefaultFont(LayoutConverter.create_font_for_label(label))
                        doc.setHtml("<body>{}</body>".format(label.currentText()))

                        block = doc.findBlockByNumber(doc.blockCount() - 1)
                        it = block.begin()
                        char_format = None
                        while not it.atEnd():
                            fragment = it.fragment()
                            if fragment.isValid():
                                char_format = it.fragment().charFormat()
                            it += 1

                        f = char_format.font()

                    pixel_size = POINTS_TO_MM * f.pointSizeF() * 10
                    f.setPixelSize(int(pixel_size + 0.5))
                    fm = QFontMetricsF(f)
                    descent = fm.descent() / 10

                    y -= label_size.height() - descent
                else:
                    assert False

                if (
                    text_format.background().enabled()
                    and text_format.background().sizeType()
                    == QgsTextBackgroundSettings.SizeType.SizeFixed
                ):
                    # a big hack to ensure that labels with a background symbol are sufficiently large
                    # to fit the background symbol!
                    render_context = QgsLayoutUtils.createRenderContextForLayout(
                        layout, None
                    )
                    render_context.setFlag(
                        QgsRenderContext.Flag.ApplyScalingWorkaroundForTextRendering
                    )

                    background_size = text_format.background().size()
                    if (
                        text_format.background().type()
                        == QgsTextBackgroundSettings.ShapeType.ShapeMarkerSymbol
                    ):
                        marker_symbol = text_format.background().markerSymbol().clone()
                        background_bounds = marker_symbol.bounds(
                            QPointF(0, 0), render_context
                        )
                        width_painter_units = background_bounds.width()
                        height_painter_units = background_bounds.height()
                    else:
                        width_painter_units = render_context.convertToPainterUnits(
                            background_size.width(), text_format.background().sizeUnit()
                        )
                        height_painter_units = render_context.convertToPainterUnits(
                            background_size.height(),
                            text_format.background().sizeUnit(),
                        )
                    width_mm = (
                        width_painter_units
                        / render_context.convertToPainterUnits(
                            1, QgsUnitTypes.RenderUnit.RenderMillimeters
                        )
                    )
                    height_mm = (
                        height_painter_units
                        / render_context.convertToPainterUnits(
                            1, QgsUnitTypes.RenderUnit.RenderMillimeters
                        )
                    )
                    background_size_layout_units = layout.convertToLayoutUnits(
                        QgsLayoutSize(
                            width_mm,
                            height_mm,
                            QgsUnitTypes.LayoutUnit.LayoutMillimeters,
                        )
                    )
                    if background_size_layout_units.height() > label_size.height():
                        delta_y = (
                            background_size_layout_units.height() - label_size.height()
                        )
                        label.setMarginY(delta_y)
                        label_size.setHeight(label_size.height() + 2 * delta_y)
                        y -= delta_y

                    if background_size_layout_units.width() > label_size.width():
                        delta_x = (
                            background_size_layout_units.width() - label_size.width()
                        )
                        label.setMarginX(delta_x)
                        label_size.setWidth(label_size.width() + 2 * delta_x)
                        x -= delta_x

                label.attemptSetSceneRect(
                    QRectF(x, y, label_size.width(), label_size.height())
                )

            label.setHAlign(halign)

            if text_symbol.angle:
                old_ref = label.referencePoint()

                if is_left_align:
                    label.setReferencePoint(QgsLayoutItem.ReferencePoint.LowerLeft)
                elif is_right_align:
                    label.setReferencePoint(QgsLayoutItem.ReferencePoint.LowerRight)
                elif is_middle_align:
                    label.setReferencePoint(QgsLayoutItem.ReferencePoint.LowerMiddle)
                old_pos = label.positionWithUnits()
                label.setItemRotation(-text_symbol.angle)
                label.attemptMove(old_pos, True)
                label.setReferencePoint(old_ref)

            layout.addLayoutItem(label)
            return {element: label}

        elif isinstance(element, (MapSurroundFrame,)):
            map_surround = element.element

            if isinstance(map_surround, (MarkerNorthArrow,)):
                if USE_LAYOUT_MARKER:
                    shape = QgsLayoutItemMarker(layout)

                    if isinstance(map_surround, MarkerNorthArrow):
                        marker = SymbolConverter.Symbol_to_QgsSymbol(
                            map_surround.marker_element.symbol, context
                        )
                        # unrotate, because calculated angles are stored inside symbol definition in ESRI land
                        marker.setAngle(marker.angle() + map_surround.calculated_angle)
                        shape.setSymbol(marker)
                        LayoutConverter.set_common_properties(
                            layout,
                            map_surround.marker_element,
                            shape,
                            page_height,
                            context,
                            base_units,
                            conversion_factor,
                        )
                    else:
                        marker = SymbolConverter.Symbol_to_QgsSymbol(
                            map_surround.point_symbol, context
                        )
                        # unrotate, because calculated angles are stored inside symbol definition in ESRI land
                        marker.setAngle(marker.angle() + (map_surround.rotation or 0))
                        shape.setSymbol(marker)
                        LayoutConverter.set_common_properties(
                            layout,
                            map_surround,
                            shape,
                            page_height,
                            context,
                            base_units,
                            conversion_factor,
                        )

                    if map_surround.calibration_angle is not None:
                        shape.setNorthOffset(map_surround.calibration_angle)

                    if isinstance(map_surround, MarkerNorthArrow):
                        if (
                            map_surround.orientation_type
                            == MarkerNorthArrow.ANGLE_DATA_FRAME
                        ):
                            shape.setNorthMode(
                                QgsLayoutNorthArrowHandler.NorthMode.GridNorth
                            )
                        elif (
                            map_surround.orientation_type
                            == MarkerNorthArrow.ANGLE_ABSOLUTE
                        ):
                            shape.setNorthMode(
                                QgsLayoutNorthArrowHandler.NorthMode.TrueNorth
                            )

                    layout.addLayoutItem(shape)
                    return {map_surround: shape}
                else:
                    # no background or frame allowed for QgsLayoutItemShape!
                    had_frame_background = False
                    if element.border:
                        had_frame_background = True
                    if element.background:
                        had_frame_background = True
                    if had_frame_background:
                        # need to convert to a separate object
                        background = QgsLayoutItemShape(layout)
                        background.setShapeType(QgsLayoutItemShape.Shape.Rectangle)

                        fill_symbol = SymbolConverter.convert_border_background_shadow(
                            border=element.border,
                            background=element.background,
                            shadow=element.shadow,
                            context=context,
                        )

                        background.setSymbol(fill_symbol)
                        LayoutConverter.set_common_properties(
                            layout,
                            element,
                            background,
                            page_height,
                            context,
                            base_units,
                            conversion_factor,
                        )
                        layout.addLayoutItem(background)

                    # have to convert to rectangles with a centroid fill, that's the closest we can get
                    shape = QgsLayoutItemShape(layout)
                    shape.setShapeType(QgsLayoutItemShape.Shape.Rectangle)

                    centroid_marker = SymbolConverter.Symbol_to_QgsSymbol(
                        map_surround.marker_element.symbol, context
                    )

                    # unrotate, because calculated angles are stored inside symbol definition in ESRI land
                    centroid_marker.setAngle(
                        centroid_marker.angle() + map_surround.calculated_angle
                    )
                    # and then "fake" north arrow behavior via data defined rotation bound to map
                    if element.map_frame:
                        centroid_marker.setDataDefinedAngle(
                            QgsProperty.fromExpression(
                                """item_variables('{}')['map_rotation']""".format(
                                    element.map_frame.map.name
                                )
                            )
                        )

                    fill_symbol = QgsFillSymbol()
                    layer = QgsCentroidFillSymbolLayer()
                    layer.setSubSymbol(centroid_marker)
                    fill_symbol.changeSymbolLayer(0, layer)

                    shape.setSymbol(fill_symbol)
                    LayoutConverter.set_common_properties(
                        layout,
                        element,
                        shape,
                        page_height,
                        context,
                        base_units,
                        conversion_factor,
                    )

                    shape.setFrameEnabled(False)
                    shape.setBackgroundEnabled(False)
                    layout.addLayoutItem(shape)

                    context.push_warning(
                        "Conversion of north arrows is much improved in QGIS 3.14 or later",
                        level=Context.WARNING,
                    )

                    return {map_surround: shape}

            elif isinstance(
                map_surround,
                (
                    ScaleLine,
                    AlternatingScaleBar,
                    DoubleAlternatingScaleBar,
                    SteppedScaleLine,
                    SingleDivisionScaleBar,
                    HollowScaleBar,
                ),
            ):
                item = QgsLayoutItemScaleBar(layout)
                item.setBoxContentSpace(0)

                text_format = TextSymbolConverter.text_symbol_to_qgstextformat(
                    map_surround.number_symbol, context
                )
                item.setTextFormat(text_format)

                units, factor = VectorRendererConverter.convert_distance_unit(
                    map_surround.division_units
                )
                item.setUnits(units)
                if isinstance(
                    map_surround,
                    (
                        AlternatingScaleBar,
                        DoubleAlternatingScaleBar,
                        HollowScaleBar,
                        SteppedScaleLine,
                    ),
                ):
                    item.setNumberOfSegments(max(1, (map_surround.divisions or 0) - 1))
                    item.setNumberOfSegmentsLeft(map_surround.sub_divisions or 0)
                else:
                    item.setNumberOfSegments(map_surround.divisions)
                    item.setNumberOfSegmentsLeft(
                        1 if map_surround.show_one_div_before_zero else 0
                    )
                item.setUnitsPerSegment((map_surround.division_value or 0) * factor)
                item.setUnitLabel(map_surround.division_unit_label)
                item.setLabelBarSpace((map_surround.label_gap or 0) * POINTS_TO_MM)

                if map_surround.label_position in (
                    ScalebarBase.BELOW_BAR,
                    ScalebarBase.ALIGN_TO_BOTTOM_OF_BAR,
                ):
                    item.setLabelVerticalPlacement(
                        QgsScaleBarSettings.LabelVerticalPlacement.LabelBelowSegment
                    )

                if True and map_surround.bar_line_symbol:
                    line_symbol = SymbolConverter.Symbol_to_QgsSymbol(
                        map_surround.bar_line_symbol, context
                    )
                    item.setLineSymbol(line_symbol)

                division_symbol = SymbolConverter.Symbol_to_QgsSymbol(
                    map_surround.division_line_symbol, context
                )
                if division_symbol:
                    item.setDivisionLineSymbol(division_symbol)

                subdivision_symbol = SymbolConverter.Symbol_to_QgsSymbol(
                    map_surround.sub_division_line_symbol, context
                )
                if subdivision_symbol:
                    item.setSubdivisionLineSymbol(subdivision_symbol)

                item.setNumberOfSubdivisions(map_surround.sub_divisions or 0)

                numeric_format = NumericFormatConverter.convert_format(
                    map_surround.number_format, context
                )
                if numeric_format is not None:
                    item.setNumericFormat(numeric_format)

                if isinstance(map_surround, ScaleLine):
                    if map_surround.mark_position == ScalebarBase.ABOVE_BAR:
                        item.setStyle("Line Ticks Up")
                    elif map_surround.mark_position == ScalebarBase.BELOW_BAR:
                        item.setStyle("Line Ticks Down")
                    else:
                        item.setStyle("Line Ticks Middle")

                    item.setHeight(map_surround.division_height * POINTS_TO_MM)

                    item.setSubdivisionsHeight(
                        map_surround.sub_division_height * POINTS_TO_MM
                    )

                    if map_surround.sub_division_height > map_surround.division_height:
                        item.setLabelBarSpace(
                            (
                                map_surround.label_gap
                                + map_surround.sub_division_height
                                - map_surround.division_height
                            )
                            * POINTS_TO_MM
                        )

                elif isinstance(
                    map_surround,
                    (
                        AlternatingScaleBar,
                        DoubleAlternatingScaleBar,
                        SingleDivisionScaleBar,
                        HollowScaleBar,
                    ),
                ):
                    if isinstance(
                        map_surround, (SingleDivisionScaleBar, AlternatingScaleBar)
                    ):
                        item.setStyle("Single Box")
                    elif isinstance(map_surround, HollowScaleBar):
                        item.setStyle("hollow")
                    else:
                        item.setStyle("Single Box")

                    item.setHeight((map_surround.bar_height or 0) * POINTS_TO_MM)

                    symbol = SymbolConverter.Symbol_to_QgsSymbol(
                        map_surround.fill_symbol1, context
                    )
                    if symbol:
                        item.setFillSymbol(symbol)

                    if isinstance(
                        map_surround,
                        (
                            AlternatingScaleBar,
                            DoubleAlternatingScaleBar,
                            HollowScaleBar,
                        ),
                    ):
                        symbol2 = SymbolConverter.Symbol_to_QgsSymbol(
                            map_surround.fill_symbol2, context
                        )
                        if symbol2:
                            item.setAlternateFillSymbol(symbol2)

                    if isinstance(map_surround, SingleDivisionScaleBar):
                        item.setNumberOfSegmentsLeft(0)
                        item.setNumberOfSegments(1)

                elif isinstance(map_surround, SteppedScaleLine):
                    item.setStyle("stepped")
                    # seems hard coded?
                    item.setHeight(3.6)

                if item.numberOfSegmentsLeft() + item.numberOfSegments() == 1:
                    item.setLabelHorizontalPlacement(
                        QgsScaleBarSettings.LabelHorizontalPlacement.LabelCenteredSegment
                    )
                else:
                    item.setLabelHorizontalPlacement(
                        QgsScaleBarSettings.LabelHorizontalPlacement.LabelCenteredEdge
                    )

                LayoutConverter.set_common_properties(
                    layout,
                    element,
                    item,
                    page_height,
                    context,
                    base_units,
                    conversion_factor,
                )
                layout.addLayoutItem(item)
                return {map_surround: item}
            elif isinstance(map_surround, ScaleText):
                item = QgsLayoutItemScaleBar(layout)

                text_format = TextSymbolConverter.text_symbol_to_qgstextformat(
                    map_surround.text_element.text_symbol, context
                )
                item.setTextFormat(text_format)

                item.setBoxContentSpace(0)

                numeric_format = NumericFormatConverter.convert_format(
                    map_surround.number_format, context
                )
                if numeric_format is not None:
                    item.setNumericFormat(numeric_format)

                item.setStyle("Numeric")

                LayoutConverter.set_common_properties(
                    layout,
                    element,
                    item,
                    page_height,
                    context,
                    base_units,
                    conversion_factor,
                )
                layout.addLayoutItem(item)
                return {map_surround: item}
            elif isinstance(map_surround, (Legend,)):
                item = QgsLayoutItemLegend(layout)
                item.setAutoUpdateModel(False)

                if map_surround.label_width:
                    if Qgis.QGIS_VERSION_INT >= 34300:
                        item.setAutoWrapLinesAfter(
                            map_surround.label_width * POINTS_TO_MM
                        )
                    else:
                        context.push_warning(
                            "Wrapping legend text requires QGIS 3.44 or later",
                            level=Context.WARNING,
                        )

                # by default ESRI enables this setting for a legend item, but it's a per-item setting, which
                # QGIS currently doesn't support...
                item.setSplitLayer(True)

                if isinstance(map_surround, Legend):
                    legend_format = map_surround.format
                else:
                    legend_format = map_surround

                if legend_format.show_title:
                    item.setTitle(map_surround.title)
                else:
                    item.setTitle(None)

                item.setBoxSpace(0)

                if legend_format.title_text_symbol:
                    text_format = TextSymbolConverter.text_symbol_to_qgstextformat(
                        legend_format.title_text_symbol, context
                    )
                    item.rstyle(QgsLegendStyle.Style.Title).setFont(
                        text_format.toQFont()
                    )

                item.rstyle(QgsLegendStyle.Style.Title).setMargin(
                    QgsLegendStyle.Side.Bottom,
                    (legend_format.title_gap or 0) * POINTS_TO_MM,
                )

                # ideally bottom only, but not exposed in QGIS, so we HAVE to set top too!
                item.rstyle(QgsLegendStyle.Style.Symbol).setMargin(
                    QgsLegendStyle.Side.Bottom,
                    (legend_format.item_gap or 0) * POINTS_TO_MM,
                )
                item.rstyle(QgsLegendStyle.Style.Symbol).setMargin(
                    QgsLegendStyle.Side.Top,
                    (legend_format.item_gap or 0) * POINTS_TO_MM,
                )

                item.setColumnSpace((legend_format.column_gap or 0) * POINTS_TO_MM)

                item.rstyle(QgsLegendStyle.Style.Subgroup).setMargin(
                    QgsLegendStyle.Side.Bottom,
                    (legend_format.layer_name_gap or 0) * POINTS_TO_MM,
                )
                item.rstyle(QgsLegendStyle.Style.Group).setMargin(
                    QgsLegendStyle.Side.Top,
                    (legend_format.group_gap or 0) * POINTS_TO_MM,
                )
                item.rstyle(QgsLegendStyle.Style.Group).setMargin(
                    QgsLegendStyle.Side.Bottom,
                    (legend_format.heading_gap or 0) * POINTS_TO_MM,
                )

                # patch gap??
                item.rstyle(QgsLegendStyle.Style.SymbolLabel).setMargin(
                    QgsLegendStyle.Side.Left,
                    (legend_format.text_gap or 0) * POINTS_TO_MM,
                )

                default_width = legend_format.default_width or 0
                default_height = legend_format.default_height or 0
                item.setSymbolWidth(default_width * POINTS_TO_MM)
                item.setSymbolHeight(default_height * POINTS_TO_MM)

                if map_surround.right_to_left:
                    item.setSymbolAlignment(Qt.AlignmentFlag.AlignRight)

                item.model().removeRows(0, item.model().rowCount())

                set_class_text_symbol = False

                column_count = 1
                all_have_only_visible_in_map = True
                for item_index, legend_item in enumerate(map_surround.items):
                    if isinstance(legend_item, LegendItemBase):
                        all_have_only_visible_in_map &= (
                            legend_item.only_show_classes_visible_in_map
                        )
                    else:
                        all_have_only_visible_in_map = False
                    if isinstance(legend_item, (HorizontalLegendItem,)):
                        original_linked_layer, project_layer = (
                            LayoutConverter.get_layer(
                                legend_item.layer, layer_to_layer_map
                            )
                        )

                        if not project_layer:
                            continue

                        if map_surround.show_only_layers_checked_in_toc:
                            layer_tree_layer = (
                                layout.project()
                                .layerTreeRoot()
                                .findLayer(project_layer)
                            )
                            # TODO - we need a QGIS equivalent of this setting
                            if not layer_tree_layer.isVisible():
                                continue

                        # layer_name_text_symbol

                        node = item.model().rootGroup().addLayer(project_layer)
                        if not legend_item.show_layer_name:
                            QgsLegendRenderer.setNodeLegendStyle(
                                node, QgsLegendStyle.Style.Hidden
                            )

                        if not set_class_text_symbol:
                            if isinstance(legend_item, HorizontalLegendItem):
                                text_format = (
                                    TextSymbolConverter.text_symbol_to_qgstextformat(
                                        legend_item.legend_class_format.label_symbol,
                                        context,
                                    )
                                )
                            else:
                                text_format = (
                                    TextSymbolConverter.text_symbol_to_qgstextformat(
                                        legend_item.label_symbol, context
                                    )
                                )
                            item.rstyle(QgsLegendStyle.Style.SymbolLabel).setFont(
                                text_format.toQFont()
                            )

                            set_class_text_symbol = True

                        if item_index > 0 and legend_item.place_in_new_column:
                            column_count += 1
                            if USE_LEGEND_PATCHES:
                                node.setCustomProperty("legend/column-break", True)
                            else:
                                context.push_warning(
                                    "Conversion of manual legend column breaks requires QGIS 3.14 or later",
                                    level=Context.WARNING,
                                )

                        if legend_item.prevent_column_split:
                            if USE_LEGEND_PATCHES:
                                node.setLegendSplitBehavior(
                                    QgsLayerTreeLayer.LegendNodesSplitBehavior.PreventSplittingLegendNodesOverMultipleColumns
                                )
                            else:
                                context.push_warning(
                                    "Preventing layer legend column splitting requires QGIS 3.14 or later",
                                    level=Context.WARNING,
                                )

                        if len(item.model().layerLegendNodes(node, True)) > 1:
                            column_count += (legend_item.column_count or 1) - 1

                        if hasattr(original_linked_layer, "renderer"):
                            if isinstance(
                                original_linked_layer.renderer,
                                (SimpleRenderer,),
                            ):
                                label = (
                                    original_linked_layer.renderer.legend_group.classes[
                                        0
                                    ].label
                                )
                                if label:
                                    node.setCustomProperty("legend/title-label", label)
                                    if item.model().legendNodeEmbeddedInParent(node):
                                        item.model().legendNodeEmbeddedInParent(
                                            node
                                        ).setUserLabel("")
                            elif True:
                                if isinstance(
                                    project_layer.renderer(),
                                    QgsCategorizedSymbolRenderer,
                                ):
                                    for original_index, n in enumerate(
                                        item.model().layerLegendNodes(node, True)
                                    ):
                                        label = n.data(Qt.ItemDataRole.DisplayRole)
                                        # find corresponding legend class
                                        description = ""
                                        for (
                                            legend_group
                                        ) in original_linked_layer.renderer.groups:
                                            for legend_class in legend_group.classes:
                                                if legend_class.label == label:
                                                    description = (
                                                        legend_class.description
                                                    )

                                        if legend_item.arrangement in (
                                            LegendItemBase.ARRANGEMENT_SYMBOL_LABEL_DESCRIPTION,
                                            LegendItemBase.ARRANGEMENT_LABEL_SYMBOL_DESCRIPTION,
                                            LegendItemBase.ARRANGEMENT_LABEL_DESCRIPTION_SYMBOL,
                                        ):
                                            legend_text = "{} {}".format(
                                                label, description
                                            )
                                        else:
                                            legend_text = "{} {}".format(
                                                description, label
                                            )

                                        QgsMapLayerLegendUtils.setLegendNodeUserLabel(
                                            node, original_index, legend_text
                                        )

                        nodes_to_remove = []
                        for n in item.model().layerLegendNodes(node, True):
                            if (
                                n.data(Qt.ItemDataRole.DisplayRole)
                                == "Current Atlas Page"
                            ):
                                nodes_to_remove.append(
                                    n.model().layerOriginalLegendNodes(node).index(n)
                                )
                                continue

                            key = n.data(
                                QgsLayerTreeModelLegendNode.LegendNodeRoles.RuleKeyRole
                            )

                            if (
                                project_layer.type()
                                == QgsMapLayer.LayerType.VectorLayer
                                and isinstance(
                                    project_layer.renderer(),
                                    QgsCategorizedSymbolRenderer,
                                )
                            ):
                                if not project_layer.renderer().legendSymbolItemChecked(
                                    key
                                ):
                                    nodes_to_remove.append(
                                        n.model()
                                        .layerOriginalLegendNodes(node)
                                        .index(n)
                                    )
                            if (
                                project_layer.type()
                                == QgsMapLayer.LayerType.RasterLayer
                            ):
                                if isinstance(n, QgsSimpleLegendNode):
                                    # don't show the "Band (1)" titles, to match ArcMap
                                    nodes_to_remove.append(
                                        n.model()
                                        .layerOriginalLegendNodes(node)
                                        .index(n)
                                    )

                        if nodes_to_remove:
                            order = QgsMapLayerLegendUtils.legendNodeOrder(node)
                            order = [o for o in order if o not in nodes_to_remove]
                            QgsMapLayerLegendUtils.setLegendNodeOrder(node, order)

                        if (
                            legend_item.legend_class_format.area_patch_override
                            and project_layer.type()
                            == QgsMapLayer.LayerType.VectorLayer
                            and project_layer.geometryType()
                            == QgsWkbTypes.GeometryType.PolygonGeometry
                        ):
                            if USE_LEGEND_PATCHES:
                                geom = GeometryConverter.convert_geometry(
                                    legend_item.legend_class_format.area_patch_override.polygon
                                )
                                patch_shape = QgsLegendPatchShape(
                                    QgsSymbol.SymbolType.Fill,
                                    geom,
                                    legend_item.legend_class_format.area_patch_override.preserve_aspect,
                                )
                                node.setPatchShape(patch_shape)
                                for n, legend_node in enumerate(
                                    item.model().layerLegendNodes(node, True)
                                ):
                                    if isinstance(legend_node, QgsSymbolLegendNode):
                                        QgsMapLayerLegendUtils.setLegendNodePatchShape(
                                            node, n, patch_shape
                                        )

                            else:
                                context.push_warning(
                                    "Conversion of legend patch shapes requires QGIS 3.14 or later",
                                    level=Context.WARNING,
                                )
                        elif (
                            legend_item.legend_class_format.line_patch_override
                            and project_layer.geometryType()
                            == QgsWkbTypes.GeometryType.LineGeometry
                        ):
                            if USE_LEGEND_PATCHES:
                                geom = GeometryConverter.convert_geometry(
                                    legend_item.legend_class_format.line_patch_override.polyline
                                )
                                patch_shape = QgsLegendPatchShape(
                                    QgsSymbol.SymbolType.Line,
                                    geom,
                                    legend_item.legend_class_format.line_patch_override.preserve_aspect,
                                )
                                node.setPatchShape(patch_shape)
                                for n, legend_node in enumerate(
                                    item.model().layerLegendNodes(node, True)
                                ):
                                    if isinstance(legend_node, QgsSymbolLegendNode):
                                        QgsMapLayerLegendUtils.setLegendNodePatchShape(
                                            node, n, patch_shape
                                        )
                            else:
                                context.push_warning(
                                    "Conversion of legend patch shapes requires QGIS 3.14 or later",
                                    level=Context.WARNING,
                                )

                        legend_patch_width = legend_item.legend_class_format.height
                        legend_patch_height = legend_item.legend_class_format.width

                        if legend_patch_height not in (
                            0,
                            default_height,
                        ) or legend_patch_width not in (0, default_width):
                            if USE_LEGEND_PATCHES:
                                width = (
                                    legend_patch_width * POINTS_TO_MM
                                    if legend_patch_width not in (0, default_width)
                                    else 0
                                )
                                height = (
                                    legend_patch_height * POINTS_TO_MM
                                    if legend_patch_height not in (0, default_height)
                                    else 0
                                )

                                node.setPatchSize(QSizeF(width, height))
                                for n, legend_node in enumerate(
                                    item.model().layerLegendNodes(node, True)
                                ):
                                    QgsMapLayerLegendUtils.setLegendNodeSymbolSize(
                                        node, n, QSizeF(width, height)
                                    )

                            else:
                                context.push_warning(
                                    "Conversion of legend node size overrides requires QGIS 3.14 or later",
                                    level=Context.WARNING,
                                )

                        item.model().refreshLayerLegend(node)
                    else:
                        context.push_warning(
                            "{} legend items are not yet supported".format(
                                legend_item.__class__.__name__
                            ),
                            level=Context.CRITICAL,
                        )

                item.setColumnCount(column_count)
                if all_have_only_visible_in_map:
                    item.setLegendFilterByMapEnabled(True)
                item.updateLegend()

                LayoutConverter.set_common_properties(
                    layout,
                    element,
                    item,
                    page_height,
                    context,
                    base_units,
                    conversion_factor,
                )
                layout.addLayoutItem(item)
                return {map_surround: item}
            else:
                context.push_warning(
                    "{} items are not yet supported".format(
                        map_surround.__class__.__name__
                    ),
                    level=Context.CRITICAL,
                )

                return None
        elif isinstance(element, OleFrame):
            context.push_warning(
                "OLE frames in layouts are not supported by QGIS",
                level=Context.CRITICAL,
            )
            return None
        else:
            context.push_warning(
                "{} items are not yet supported".format(element.__class__.__name__),
                level=Context.CRITICAL,
            )

            return None

    @staticmethod
    def find_referenced_object(added_items: dict, referenced_object):
        """
        Finds the results of a converted item
        """
        if referenced_object is None:
            return None

        if added_items.get(referenced_object):
            return added_items.get(referenced_object)
        elif referenced_object.ref_id is not None:
            matching = [
                v
                for k, v in added_items.items()
                if k.ref_id == referenced_object.ref_id
            ]
            assert len(matching) <= 1
            if matching:
                return matching[0]
        return None

    @staticmethod
    def reconnect_element(element, layout: QgsPrintLayout, added_items, context):
        if isinstance(element, (GroupElement,)):
            for child in element.elements:
                LayoutConverter.reconnect_element(child, layout, added_items, context)
        elif isinstance(element, (MapSurroundFrame,)):
            map_surround = element.element

            map = LayoutConverter.find_referenced_object(added_items, element.map_frame)
            if map and issubclass(
                map_surround.__class__,
                (
                    ScalebarBase,
                    ScaleText,
                ),
            ):
                scale_bar = LayoutConverter.find_referenced_object(
                    added_items, map_surround
                )
                if scale_bar is not None:
                    scale_bar.setLinkedMap(map)
            elif map and issubclass(map_surround.__class__, (Legend,)):
                legend = LayoutConverter.find_referenced_object(
                    added_items, map_surround
                )
                if legend is not None:
                    legend.setLinkedMap(map)
            elif map and issubclass(map_surround.__class__, (MarkerNorthArrow,)):
                north_arrow = LayoutConverter.find_referenced_object(
                    added_items, map_surround
                )
                if north_arrow is not None and USE_LAYOUT_MARKER:
                    north_arrow.setLinkedMap(map)
        elif isinstance(element, (MapFrame,)):
            map = LayoutConverter.find_referenced_object(added_items, element)
            for l in element.locators:
                linked_map = LayoutConverter.find_referenced_object(added_items, l.map)
                if linked_map is None:
                    # look inside all converted map frames for a map frame with the same map!
                    map_frames = [
                        k for k in added_items.keys() if isinstance(k, MapFrame)
                    ]
                    matching_map_frames = [
                        f
                        for f in map_frames
                        if f.map == l.map.map
                        or (
                            f.map.ref_id is not None
                            and f.map.ref_id == l.map.map.ref_id
                        )
                    ]
                    assert len(matching_map_frames) <= 1
                    if matching_map_frames:
                        linked_map = added_items[matching_map_frames[0]]

                if not linked_map:
                    # fallback to looking for matching data frames by name -- this isn't so robust, there can be duplicates!
                    map_frames = [
                        k for k in added_items.keys() if isinstance(k, MapFrame)
                    ]
                    matching_map_frames = [
                        f for f in map_frames if f.map.name == l.map.map.name
                    ]
                    if len(matching_map_frames) == 1:
                        linked_map = added_items[matching_map_frames[0]]

                if not linked_map:
                    context.push_warning(
                        '{}: could not find matching locator map "{}"'.format(
                            element.map.name, l.map.map.name
                        ),
                        level=Context.WARNING,
                    )
                    continue

                fill_symbol = SymbolConverter.convert_border_background_shadow(
                    border=l.border,
                    background=l.background,
                    shadow=l.shadow,
                    context=context,
                )
                map_name = l.map.map.name

                overview = QgsLayoutItemMapOverview(map_name, map)
                overview.setLinkedMap(linked_map)
                if fill_symbol:
                    overview.setFrameSymbol(fill_symbol)
                map.overviews().addOverview(overview)

    @staticmethod
    def convert_dynamic_text(text: str, context: Context) -> str:
        """
        Attempts to convert ESRI dynamic text to QGIS
        """
        for pattern, replacement in DYNAMIC_TEXT_REPLACEMENTS.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE | re.UNICODE)

        for dyn in re.findall("(<dyn\\b.*?>)", text, flags=re.IGNORECASE):
            context.push_warning(
                'Dynamic text "{}" not yet supported'.format(dyn), level=Context.WARNING
            )

        return text

    @staticmethod
    def convert_html(
        text: str, context: Context, force_html: bool = False
    ) -> Tuple[str, bool]:
        """
        Convert ESRI text formatting tags to HTML tags
        """
        is_html = force_html

        plain_text = text
        for pattern, replacement in HTML_REPLACEMENTS.items():
            if re.search(pattern, text, flags=re.IGNORECASE):
                is_html = True

            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        text = re.sub(
            r"<link>(.*?)</link>",
            r'<a href="\1" style="text-decoration: none">\1</a>',
            text,
            flags=re.IGNORECASE,
        )

        if re.search(
            r'<\s*lin\s+leading\s*=\s*"?\s*[\d.]+\s*"?\s*>', text, flags=re.IGNORECASE
        ):
            if Qgis.QGIS_VERSION_INT >= 34200:
                text = re.sub(
                    r'<\s*lin\s+leading\s*=\s*"?\s*([\d.]+)\s*"?\s*>',
                    lambda m: '<div style="margin-top: {}pt">&#8203;</div>'.format(
                        float(m.group(1))
                    ),
                    text,
                    flags=re.IGNORECASE,
                )
                text = re.sub(r"<\s*/\s*lin\s*>", "", text, flags=re.IGNORECASE)
            else:
                context.push_warning(
                    "Line extra leading requires QGIS 3.42 or later",
                    level=Context.WARNING,
                )
                text = re.sub(
                    r'<\s*lin\s+leading\s*=\s*"?\s*[\d.]+\s*"?\s*>',
                    "",
                    text,
                    flags=re.IGNORECASE,
                )
                text = re.sub(r"<\s*/\s*lin\s*>", "", text, flags=re.IGNORECASE)

        if text != plain_text:
            is_html = True

        if is_html:
            multi_space = re.compile(r" {2}")
            text = multi_space.sub("&nbsp;&nbsp;", text)
            text = text.replace("\r", "")
            text = text.replace("\n", "<br>\n")

        if "<FNT" in text:
            context.push_warning(
                'HTML text "{}" not yet supported'.format(plain_text),
                level=Context.WARNING,
            )

        return text, is_html

    @staticmethod
    def html_units_to_layout_units(layout: Optional[QgsLayout]) -> float:
        """
        Returns scale factor to convert html units to layout units.

        Reimplements internal (private) QGIS method
        """
        if not layout:
            return 1

        return layout.convertToLayoutUnits(
            QgsLayoutMeasurement(
                layout.renderContext().dpi() / 72.0,
                QgsUnitTypes.LayoutUnit.LayoutMillimeters,
            )
        )

    @staticmethod
    def create_stylesheet_for_label(label: QgsLayoutItemLabel) -> str:
        """
        Creates a stylesheet for the label.

        Reimplements internal (private) QGIS method
        """
        scale_factor = LayoutConverter.html_units_to_layout_units(label.layout())

        stylesheet = "body {{ margin: {} {};".format(
            max(0.0, label.marginY() * scale_factor),
            max(0.0, label.marginX() * scale_factor),
        )

        point_to_pixel_multiplier = POINTS_TO_MM * scale_factor

        if Qgis.QGIS_VERSION_INT >= 32400:
            stylesheet += QgsFontUtils.asCSS(
                label.textFormat().toQFont(), point_to_pixel_multiplier
            )
        else:
            stylesheet += QgsFontUtils.asCSS(label.font(), point_to_pixel_multiplier)

        if label.hAlign() == Qt.AlignmentFlag.AlignLeft:
            stylesheet += "text-align: left;"
        elif label.hAlign() == Qt.AlignmentFlag.AlignRight:
            stylesheet += "text-align: right;"
        elif label.hAlign() == Qt.AlignmentFlag.AlignHCenter:
            stylesheet += "text-align: center;"
        else:
            stylesheet += "text-align: justify;"
        stylesheet += " }"
        return stylesheet

    @staticmethod
    def create_font_for_label(label: QgsLayoutItemLabel) -> QFont:
        """
        Creates the default font for the label.

        Reimplements internal (private) QGIS method
        """
        if Qgis.QGIS_VERSION_INT >= 32400:
            font = label.textFormat().font()

            if (
                label.textFormat().sizeUnit()
                == QgsUnitTypes.RenderUnit.RenderMillimeters
            ):
                font.setPointSizeF(label.textFormat().size() / POINTS_TO_MM)
            elif label.textFormat().sizeUnit() == QgsUnitTypes.RenderUnit.RenderPixels:
                font.setPixelSize(int(label.textFormat().size()))
            elif label.textFormat().sizeUnit() == QgsUnitTypes.RenderUnit.RenderPoints:
                font.setPointSizeF(label.textFormat().size())
            elif label.textFormat().sizeUnit() == QgsUnitTypes.RenderUnit.RenderInches:
                font.setPointSizeF(label.textFormat().size() * 72)
        else:
            font = label.font()

        return font

    @staticmethod
    def label_size_for_text(label: QgsLayoutItemLabel) -> QSizeF:
        """
        Returns the size required for a label to fit in its text
        """
        layout = label.layout()
        context = QgsLayoutUtils.createRenderContextForLayout(layout, None)
        context.setFlag(QgsRenderContext.Flag.ApplyScalingWorkaroundForTextRendering)

        pen_width = (label.pen().widthF() / 2.0) if label.frameEnabled() else 0

        if (
            label.mode() == QgsLayoutItemLabel.Mode.ModeFont
            and Qgis.QGIS_VERSION_INT >= 32400
        ):
            lines = label.currentText().split("\n")
            text_width = QgsTextRenderer.textWidth(
                context, label.textFormat(), lines
            ) / context.convertToPainterUnits(
                1, QgsUnitTypes.RenderUnit.RenderMillimeters
            )
            font_height = QgsTextRenderer.textHeight(
                context, label.textFormat(), lines
            ) / context.convertToPainterUnits(
                1, QgsUnitTypes.RenderUnit.RenderMillimeters
            )

            width = 2 + text_width + 2 * label.marginX() + 2 * pen_width
            height = 2 + font_height + 2 * label.marginY() + 2 * pen_width

            return layout.convertToLayoutUnits(
                QgsLayoutSize(width, height, QgsUnitTypes.LayoutUnit.LayoutMillimeters)
            )
        else:
            doc = QTextDocument()
            doc.setDocumentMargin(0)
            doc.setDefaultStyleSheet(LayoutConverter.create_stylesheet_for_label(label))
            doc.setDefaultFont(LayoutConverter.create_font_for_label(label))

            option = doc.defaultTextOption()
            option.setAlignment(label.hAlign())
            doc.setDefaultTextOption(option)
            doc.setHtml("<body>{}</body>".format(label.currentText()))

            # SO gross!, but we want a super-accurate bounding rect
            temp_dir = QTemporaryDir()
            temp_svg_path = temp_dir.filePath("temp.svg")
            gen = QSvgGenerator()
            gen.setFileName(temp_svg_path)
            painter = QPainter(gen)
            painter.setBrush(QBrush(QColor(0, 0, 0)))
            painter.setTransform(QTransform.fromScale(10, 10))

            doc.drawContents(painter)
            painter.end()

            ren = QSvgRenderer(temp_svg_path)
            picture = QPicture()
            painter = QPainter(picture)

            ren.render(painter)
            painter.end()

            doc_size_px = QSizeF(
                picture.boundingRect().right() / 10,
                picture.boundingRect().bottom() / 10,
            )
            # x margin is already taken into account
            width_mm = 2 + doc_size_px.width() / 2.5 + 2 * pen_width
            height_mm = (
                2 + doc_size_px.height() / 3.5 + 2 * label.marginY() + 2 * pen_width
            )

            return layout.convertToLayoutUnits(
                QgsLayoutSize(
                    width_mm, height_mm, QgsUnitTypes.LayoutUnit.LayoutMillimeters
                )
            )
