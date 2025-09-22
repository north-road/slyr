#!/usr/bin/env python

# /***************************************************************************
# text_format.py
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

"""
Text symbol conversion
"""

import math
from typing import Union, Tuple

from qgis.PyQt.QtCore import QSizeF, QPointF, Qt
from qgis.PyQt.QtGui import QFont, QPainter, QColor
from qgis.core import (
    Qgis,
    QgsTextFormat,
    QgsUnitTypes,
    QgsTextShadowSettings,
    QgsTextBufferSettings,
    QgsTextBackgroundSettings,
    QgsStringUtils,
)

from .color import ColorConverter

from ..parser.exceptions import NotImplementedException
from ..parser.objects.balloon_callout import BalloonCallout
from ..parser.objects.fill_symbol_layer import SimpleFillSymbol
from ..parser.objects.line_callout import LineCallout
from ..parser.objects.line_symbol_layer import SimpleLineSymbol
from ..parser.objects.marker_text_background import MarkerTextBackground
from ..parser.objects.simple_line_callout import SimpleLineCallout
from ..parser.objects.text_symbol import TextSymbol
from .utils import ConversionUtils


class TextSymbolConverter:
    """
    Converts text symbol to QGIS text formats
    """

    CAPITALIZATION_MAP = {
        TextSymbol.CASE_NORMAL: QFont.Capitalization.MixedCase,
        TextSymbol.CASE_LOWER: QFont.Capitalization.AllLowercase,
        TextSymbol.CASE_ALL_CAPS: QFont.Capitalization.AllUppercase,
        TextSymbol.CASE_SMALL_CAPS: QFont.Capitalization.MixedCase,  # QFont.SmallCaps is broken :(
    }

    TEXT_CAPITALIZATION_MAP = {
        TextSymbol.CASE_NORMAL: QgsStringUtils.Capitalization.MixedCase,
        TextSymbol.CASE_LOWER: QgsStringUtils.Capitalization.AllLowercase,
        TextSymbol.CASE_ALL_CAPS: QgsStringUtils.Capitalization.AllUppercase,
        TextSymbol.CASE_SMALL_CAPS: QgsStringUtils.Capitalization.MixedCase,  # QFont.SmallCaps is broken :(
    }

    @staticmethod
    def std_font_to_qfont(font) -> Tuple[QFont, str, str]:  # pylint: disable=too-many-branches
        """
        Converts STD font to QFont
        """
        name = font.font_name

        style_name = None

        # we need to sometimes strip 'Italic' or 'Bold' suffixes from the font name stored in the ESRI object
        # in order to match against actual font families
        keep_scanning = True
        while name not in ConversionUtils.available_font_families() and keep_scanning:
            keep_scanning = False
            if name.lower().endswith(" italic"):
                name = name[: -len(" italic")]
                keep_scanning = True
            elif name.lower().endswith(" bold"):
                name = name[: -len(" bold")]
                keep_scanning = True
            elif name.lower().endswith(" black"):
                name = name[: -len(" black")]
                style_name = "Black"
            elif name.lower().endswith(" medium"):
                name = name[: -len(" medium")]
                style_name = "Medium"
            elif name.lower().endswith(" regular"):
                name = name[: -len(" regular")]
                style_name = "Regular"

        res = QFont(name)
        res.setWeight(font.weight)
        if font.weight > 400:
            res.setBold(True)

        if font.italic:
            res.setItalic(True)

        # pretty annoying, but because qgis relies on style strings, we need to convert the raw bools to style names if possible...
        if res.italic() and not res.bold():
            styles = ConversionUtils.available_font_styles(res.family())
            for s in styles:
                if s.lower() in ["oblique", "italic"]:
                    res.setStyleName(s)
                    break
        elif res.italic() and res.bold():
            styles = ConversionUtils.available_font_styles(res.family())
            for s in styles:
                if (
                    "oblique" in s.lower() or "italic" in s.lower()
                ) and "bold" in s.lower():
                    res.setStyleName(s)
                    break
        elif res.bold():
            styles = ConversionUtils.available_font_styles(res.family())
            for s in styles:
                if s.lower() == "bold":
                    res.setStyleName(s)
                    break

        if (
            style_name is not None
            and style_name in ConversionUtils.available_font_styles(res.family())
        ):
            res.setStyleName(style_name)

        if font.underline:
            res.setUnderline(True)
        if font.strikethrough:
            res.setStrikeOut(True)

        res.setPointSizeF(font.size)
        return res, name, style_name

    @staticmethod
    def convert_horizontal_alignment(text_symbol: Union[TextSymbol,]):
        """
        Converts the horizontal alignment from a text symbol
        """
        if text_symbol.horizontal_alignment == TextSymbol.HALIGN_LEFT:
            res = Qt.AlignmentFlag.AlignLeft
        elif text_symbol.horizontal_alignment == TextSymbol.HALIGN_RIGHT:
            res = Qt.AlignmentFlag.AlignRight
        elif text_symbol.horizontal_alignment == TextSymbol.HALIGN_CENTER:
            res = Qt.AlignmentFlag.AlignHCenter
        elif text_symbol.horizontal_alignment == TextSymbol.HALIGN_FULL:
            res = Qt.AlignmentFlag.AlignJustify
        else:
            assert False

        return res

    @staticmethod
    def convert_vertical_alignment(text_symbol: Union[TextSymbol,]):
        """
        Converts the vertical alignment from a text symbol
        """
        if text_symbol.vertical_alignment == TextSymbol.VALIGN_TOP:
            res = Qt.AlignmentFlag.AlignTop, False
        elif text_symbol.vertical_alignment == TextSymbol.VALIGN_CENTER:
            res = Qt.AlignmentFlag.AlignVCenter, False
        elif text_symbol.vertical_alignment == TextSymbol.VALIGN_BOTTOM:
            res = Qt.AlignmentFlag.AlignBottom, False
        elif text_symbol.vertical_alignment == TextSymbol.VALIGN_BASELINE:
            res = Qt.AlignmentFlag.AlignBottom, True
        else:
            assert False

        return res

    # pylint: disable=too-many-locals, too-many-branches, too-many-statements
    @staticmethod
    def text_symbol_to_qgstextformat(
        text_symbol: Union[TextSymbol,],
        context,
        reference_scale=None,
    ):
        """
        Converts ESRI text symbol to QGIS text format
        """

        text_format = QgsTextFormat()

        if isinstance(text_symbol, TextSymbol):
            font, font_family, _ = TextSymbolConverter.std_font_to_qfont(
                text_symbol.font
            )

        if font.family() not in ConversionUtils.available_font_families():
            context.push_warning("Font {} not available on system".format(font_family))

        font.setKerning(text_symbol.kerning)

        conversion_factor = (
            reference_scale * 0.000352778 if reference_scale is not None else 1
        )
        # why 0.0052? why not! It's based on rendering match with ArcGIS -- there's no documentation
        # about what the ArcGIS character spacing value actually means!
        font.setLetterSpacing(
            QFont.SpacingType.AbsoluteSpacing,
            conversion_factor
            * 0.0052
            * text_symbol.font_size
            * (text_symbol.character_spacing or 0),
        )

        # may need tweaking
        font.setWordSpacing(conversion_factor * ((text_symbol.word_spacing / 100) - 1))

        if isinstance(text_symbol, TextSymbol):
            font.setCapitalization(
                TextSymbolConverter.CAPITALIZATION_MAP[text_symbol.case]
            )
            text_format.setCapitalization(
                TextSymbolConverter.TEXT_CAPITALIZATION_MAP[text_symbol.case]
            )

        if isinstance(text_symbol, TextSymbol):
            text_format.setLineHeight(1 + text_symbol.leading / text_symbol.font_size)
        else:
            text_format.setLineHeight(
                1 + (text_symbol.line_gap or 0) / text_symbol.font_size
            )

        text_format.setFont(font)
        if reference_scale is None:
            text_format.setSize(text_symbol.font_size)
            text_format.setSizeUnit(QgsUnitTypes.RenderUnit.RenderPoints)
        else:
            text_format.setSize(text_symbol.font_size * reference_scale * 0.000352778)
            # todo - use normal map units
            text_format.setSizeUnit(QgsUnitTypes.RenderUnit.RenderMetersInMapUnits)

        if Qgis.QGIS_VERSION_INT >= 32300 and text_symbol.character_width != 100:
            text_format.setStretchFactor(round(text_symbol.character_width))

        opacity = 1
        if isinstance(text_symbol, TextSymbol):
            color = ColorConverter.color_to_qcolor(text_symbol.color)
            # need to move opacity setting from color to dedicated setter
            opacity = color.alphaF()
            color.setAlpha(255)
            text_format.setColor(color)
            text_format.setOpacity(opacity)
        else:
            from .symbols import SymbolConverter

            color = SymbolConverter.symbol_to_color(text_symbol.symbol, context)
            # need to move opacity setting from color to dedicated setter
            opacity = color.alphaF()
            color.setAlpha(255)
            text_format.setColor(color)
            text_format.setOpacity(opacity)

        # shadow
        if text_symbol.shadow_x_offset or text_symbol.shadow_y_offset:
            shadow = QgsTextShadowSettings()
            shadow.setEnabled(True)

            shadow_color = ColorConverter.color_to_qcolor(text_symbol.shadow_color)
            # need to move opacity setting from color to dedicated setter
            shadow_opacity = shadow_color.alphaF()
            shadow_color.setAlpha(255)
            shadow.setColor(shadow_color)
            shadow.setOpacity(shadow_opacity)

            shadow_angle = math.degrees(
                math.atan2(
                    text_symbol.shadow_y_offset or 0, text_symbol.shadow_x_offset or 0
                )
            )
            shadow_dist = math.sqrt(
                (text_symbol.shadow_x_offset or 0) ** 2
                + (text_symbol.shadow_y_offset or 0) ** 2
            )

            shadow.setOffsetAngle(int(round(90 - shadow_angle)))
            if reference_scale is None:
                shadow.setOffsetDistance(context.convert_size(shadow_dist))
                shadow.setOffsetUnit(context.units)
            else:
                shadow.setOffsetDistance(shadow_dist * reference_scale * 0.000352778)
                shadow.setOffsetUnit(QgsUnitTypes.RenderUnit.RenderMetersInMapUnits)

            shadow.setBlendMode(QPainter.CompositionMode.CompositionMode_SourceOver)

            # arc has no option for blurring shadows - we convert with a slight blur (because it's UGLY if we don't,
            # but use a lower blur then the default to give a somewhat closer match)
            shadow.setBlurRadius(0.2)

            text_format.setShadow(shadow)

        # halo
        buffer = QgsTextBufferSettings()
        if isinstance(text_symbol, TextSymbol):
            buffer.setEnabled(text_symbol.halo_enabled)
        else:
            buffer.setEnabled(bool(text_symbol.halo_symbol))

        if reference_scale is None:
            if isinstance(text_symbol, TextSymbol):
                buffer.setSize(context.convert_size(text_symbol.halo_size))
            else:
                buffer.setSize(2 * context.convert_size(text_symbol.halo_size))
            buffer.setSizeUnit(context.units)
        else:
            buffer.setSize(2 * text_symbol.halo_size * reference_scale * 0.000352778)
            buffer.setSizeUnit(QgsUnitTypes.RenderUnit.RenderMetersInMapUnits)

        # QGIS has no option for halo symbols. Instead, we just get the color from the symbol
        if text_symbol.halo_symbol:
            from .symbols import SymbolConverter  # pylint: disable=import-outside-toplevel, cyclic-import

            halo_symbol = SymbolConverter.Symbol_to_QgsSymbol(
                text_symbol.halo_symbol, context
            )
            if halo_symbol:
                buffer_color = halo_symbol.color()
                # need to move opacity setting from color to dedicated setter
                buffer_opacity = buffer_color.alphaF()
                buffer_color.setAlpha(255)
                buffer.setColor(buffer_color)
                # in ArcMap buffer inherits text opacity, shadow does not
                buffer.setOpacity(buffer_opacity * opacity)

        text_format.setBuffer(buffer)

        if text_symbol.background_symbol:
            background = TextSymbolConverter.convert_background_symbol(
                text_symbol.background_symbol, context, reference_scale
            )
            if background:
                text_format.setBackground(background)

        if isinstance(text_symbol, TextSymbol):
            if text_symbol.cjk_orientation:
                text_format.setOrientation(
                    QgsTextFormat.TextOrientation.VerticalOrientation
                )
        else:
            pass

        return text_format

    # pylint: enable=too-many-locals, too-many-branches, too-many-statements

    # pylint: disable=too-many-return-statements
    @staticmethod
    def convert_background_symbol(background_symbol, context, reference_scale=None):
        """
        Converts a background symbol to QGIS equivalent
        """
        if isinstance(background_symbol, (MarkerTextBackground,)):
            return TextSymbolConverter.convert_marker_text_background(
                background_symbol, context
            )
        elif isinstance(background_symbol, (SimpleLineCallout,)):
            # in QGIS we don't convert this to a background
            return None
        elif isinstance(background_symbol, (BalloonCallout,)):
            # Here we convert the balloon to a solid rectangle background. If we are using this format
            # for labels we'll remove this later and replace with a proper balloon callout
            if background_symbol.fill_symbol:
                return TextSymbolConverter.convert_fill_symbol_background(
                    background_symbol, context
                )
            else:
                return None
        elif isinstance(
            background_symbol,
        ):
            if background_symbol.background_symbol:
                return TextSymbolConverter.convert_fill_symbol_background(
                    background_symbol, context, reference_scale
                )
            else:
                return None
        elif isinstance(background_symbol, LineCallout):
            if background_symbol.border_symbol:
                return TextSymbolConverter.convert_fill_symbol_background(
                    background_symbol, context, reference_scale
                )
            else:
                return None
        else:
            raise NotImplementedException(
                "Converting {} not implemented yet".format(
                    background_symbol.__class__.__name__
                )
            )

        return None

    # pylint: enable=too-many-return-statements

    @staticmethod
    def convert_marker_text_background(
        marker_text_background: Union[MarkerTextBackground,],
        context,
    ) -> QgsTextBackgroundSettings:
        """
        Converts a MarkerTextBackground to QgsTextBackgroundSettings
        """
        from .symbols import SymbolConverter  # pylint: disable=import-outside-toplevel, cyclic-import

        symbol = SymbolConverter.Symbol_to_QgsSymbol(
            marker_text_background.marker_symbol, context
        )

        settings = QgsTextBackgroundSettings()
        settings.setEnabled(True)
        settings.setType(QgsTextBackgroundSettings.ShapeType.ShapeMarkerSymbol)
        settings.setMarkerSymbol(symbol)
        if marker_text_background.scale_to_fit_text:
            settings.setSizeType(QgsTextBackgroundSettings.SizeType.SizeBuffer)
        else:
            settings.setSizeType(QgsTextBackgroundSettings.SizeType.SizeFixed)
            settings.setSize(QSizeF(symbol.size(), symbol.size()))
            settings.setSizeUnit(symbol.sizeUnit())

        return settings

    # pylint: disable=too-many-branches, too-many-statements
    @staticmethod
    def convert_fill_symbol_background(
        background_symbol, context, reference_scale=None
    ):
        """
        Converts a fill symbol background to QgsTextBackgroundSettings
        """
        settings = QgsTextBackgroundSettings()
        settings.setEnabled(True)
        settings.setType(QgsTextBackgroundSettings.ShapeType.ShapeRectangle)
        if isinstance(background_symbol, (BalloonCallout)):
            fill_symbol = background_symbol.fill_symbol
            if background_symbol.style == BalloonCallout.STYLE_ROUNDED_RECTANGLE:
                # TODO - confirm actual size rendering on Arc
                settings.setRadii(QSizeF(1, 1))
            elif background_symbol.style == BalloonCallout.STYLE_OVAL:
                # TODO - verify comparitive rendering
                settings.setType(QgsTextBackgroundSettings.ShapeType.ShapeEllipse)
        else:
            fill_symbol = background_symbol.border_symbol

        from .symbols import SymbolConverter  # pylint: disable=import-outside-toplevel, cyclic-import

        # can't use the fill itself - we can only use the fill color and outline
        if isinstance(fill_symbol, SimpleFillSymbol):
            if not fill_symbol.color.is_null:
                fill_color = ColorConverter.color_to_qcolor(fill_symbol.color)
                settings.setFillColor(fill_color)
            else:
                settings.setFillColor(QColor())

            if isinstance(fill_symbol.outline, SimpleLineSymbol):
                if not fill_symbol.outline.color.is_null:
                    settings.setStrokeColor(
                        ColorConverter.color_to_qcolor(fill_symbol.outline.color)
                    )
                    if reference_scale is None:
                        settings.setStrokeWidth(
                            context.convert_size(fill_symbol.outline.width)
                        )
                        settings.setStrokeWidthUnit(context.units)
                    else:
                        settings.setStrokeWidth(
                            fill_symbol.outline.width * reference_scale * 0.000352778
                        )
                        settings.setStrokeWidthUnit(
                            QgsUnitTypes.RenderUnit.RenderMetersInMapUnits
                        )
            else:
                stroke = SymbolConverter.Symbol_to_QgsSymbol(fill_symbol, context)
                if stroke:
                    settings.setStrokeColor(stroke.color())
                    if reference_scale is None:
                        settings.setStrokeWidth(0.2)
                        settings.setStrokeWidthUnit(
                            QgsUnitTypes.RenderUnit.RenderMillimeters
                        )
                    else:
                        settings.setStrokeWidth(0.2 * reference_scale * 0.001)
                        settings.setStrokeWidthUnit(
                            QgsUnitTypes.RenderUnit.RenderMetersInMapUnits
                        )
        else:
            symbol = SymbolConverter.Symbol_to_QgsSymbol(fill_symbol, context)
            settings.setFillColor(symbol.color())

        settings.setSizeType(QgsTextBackgroundSettings.SizeType.SizeBuffer)
        # TODO: margin
        x_margin = (background_symbol.margin_left + background_symbol.margin_right) / 2
        y_margin = (background_symbol.margin_top + background_symbol.margin_bottom) / 2

        x_delta = (background_symbol.margin_right - background_symbol.margin_left) / 2
        y_delta = (background_symbol.margin_bottom - background_symbol.margin_top) / 2

        if reference_scale is None:
            settings.setSize(
                QSizeF(context.convert_size(x_margin), context.convert_size(y_margin))
            )
            settings.setSizeUnit(context.units)
        else:
            settings.setSize(
                QSizeF(
                    x_margin * reference_scale * 0.000352778,
                    y_margin * reference_scale * 0.000352778,
                )
            )
            settings.setSizeUnit(QgsUnitTypes.RenderUnit.RenderMetersInMapUnits)

        if reference_scale is None:
            settings.setOffset(
                QPointF(context.convert_size(x_delta), context.convert_size(y_delta))
            )
            settings.setOffsetUnit(context.units)
        else:
            settings.setOffset(
                QPointF(
                    x_delta * reference_scale * 0.000352778,
                    y_delta * reference_scale * 0.000352778,
                )
            )
            settings.setOffsetUnit(QgsUnitTypes.RenderUnit.RenderMetersInMapUnits)

        return settings

    # pylint: enable=too-many-branches, too-many-statements
