#!/usr/bin/env python

# /***************************************************************************
# decorations.py
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

from qgis.core import QgsMarkerLineSymbolLayer
from slyr_community.parser.objects.decoration import LineDecoration, SimpleLineDecorationElement
from slyr_community.converters.context import Context
from slyr_community.converters.utils import ConversionUtils
from slyr_community.parser.exceptions import NotImplementedException


class DecorationConverter:

    @staticmethod
    def append_decorations(symbol, decorations: LineDecoration, context: Context, enabled: bool, locked: bool):
        """
        Appends decorations to the given symbol
        """
        if not decorations.decorations:
            return

        for decoration in decorations.decorations:
            DecorationConverter.append_decoration(symbol, decoration, context, enabled, locked)

    @staticmethod
    def append_decoration(symbol, decoration: SimpleLineDecorationElement, context: Context, enabled: bool, locked: bool):
        """
        Appends decorations to the given symbol
        """
        positions = decoration.marker_positions[:]

        from slyr_community.converters.symbols import SymbolConverter

        marker = SymbolConverter.Symbol_to_QgsSymbol(decoration.marker, context)
        if decoration.flip_all:
            for l in range(marker.symbolLayerCount()):
                layer = marker.symbolLayer(l)
                layer.setAngle(layer.angle() + 180)

        if 0 in positions:
            # start marker
            line = QgsMarkerLineSymbolLayer(not decoration.fixed_angle)
            start_marker = marker.clone()
            if decoration.flip_first:
                for l in range(marker.symbolLayerCount()):
                    layer = start_marker.symbolLayer(l)
                    layer.setAngle(layer.angle() + 180)
            for l in range(start_marker.symbolLayerCount()):
                layer = start_marker.symbolLayer(l)
                if layer.offset().x() or layer.offset().y():
                    # adjust marker offset to account for rotation of line markers
                    offset = ConversionUtils.adjust_offset_for_rotation(layer.offset(), layer.angle())
                    if decoration.flip_first or decoration.flip_all:
                        offset.setY(-offset.y())
                    layer.setOffset(offset)

            line.setSubSymbol(start_marker)

            line.setEnabled(enabled)
            line.setLocked(locked)

            # TODO - maybe need to offset this by marker width / 4? seems a better match to ESRI
            line.setPlacement(QgsMarkerLineSymbolLayer.FirstVertex)
            symbol.appendSymbolLayer(line)

        if 1 in positions:
            # end marker
            line = QgsMarkerLineSymbolLayer(not decoration.fixed_angle)

            end_marker = marker.clone()
            for l in range(end_marker.symbolLayerCount()):
                layer = end_marker.symbolLayer(l)
                if layer.offset().x() or layer.offset().y():
                    # adjust marker offset to account for rotation of line markers
                    offset = ConversionUtils.adjust_offset_for_rotation(layer.offset(), layer.angle())
                    if decoration.flip_all:
                        offset.setY(-offset.y())
                    layer.setOffset(offset)

            line.setSubSymbol(end_marker)
            line.setPlacement(QgsMarkerLineSymbolLayer.LastVertex)
            line.setEnabled(enabled)
            line.setLocked(locked)

            # TODO - maybe need to offset this by marker width / 4? seems a better match to ESRI
            symbol.appendSymbolLayer(line)

        if 0.5 in positions:
            # mid marker
            line = QgsMarkerLineSymbolLayer(not decoration.fixed_angle)

            end_marker = marker.clone()
            for l in range(end_marker.symbolLayerCount()):
                layer = end_marker.symbolLayer(l)
                if layer.offset().x() or layer.offset().y():
                    # adjust marker offset to account for rotation of line markers
                    offset = ConversionUtils.adjust_offset_for_rotation(layer.offset(), layer.angle())
                    if decoration.flip_all:
                        offset.setY(-offset.y())
                    layer.setOffset(offset)

            line.setSubSymbol(end_marker)
            line.setPlacement(QgsMarkerLineSymbolLayer.CentralPoint)
            line.setEnabled(enabled)
            line.setLocked(locked)

            symbol.appendSymbolLayer(line)

        # TODO other positions
        other_positions = [p for p in positions if p not in (0, 0.5, 1)]
        if other_positions:
            # Would need to use data defined marker placement distance, e.g. $length/3
            # and offset first marker by $length/3 to avoid placing a marker at the start
            # of the line
            raise NotImplementedException(
                'Non start/end decoration positions are not implemented (need {})'.format(other_positions))
