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

"""
Decoration converter
"""

from qgis.core import QgsMarkerLineSymbolLayer

from .context import Context
from .utils import ConversionUtils
from ..parser.exceptions import NotImplementedException
from ..parser.objects.decoration import LineDecoration, SimpleLineDecorationElement


class DecorationConverter:
    """
    Decoration converter
    """

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
    def append_decoration(symbol,  # pylint: disable=too-many-branches,too-many-statements
                          decoration: SimpleLineDecorationElement,
                          context: Context,
                          enabled: bool,
                          locked: bool):
        """
        Appends decorations to the given symbol
        """
        positions = decoration.marker_positions[:]

        from .symbols import SymbolConverter  # pylint: disable=import-outside-toplevel,cyclic-import

        marker = SymbolConverter.Symbol_to_QgsSymbol(decoration.marker, context)
        if decoration.flip_all:
            for layer_index in range(marker.symbolLayerCount()):
                layer = marker.symbolLayer(layer_index)
                layer.setAngle(layer.angle() + 180)

        if 0 in positions:
            # start marker
            line = QgsMarkerLineSymbolLayer(not decoration.fixed_angle)
            start_marker = marker.clone()
            if decoration.flip_first:
                for layer_index in range(marker.symbolLayerCount()):
                    layer = start_marker.symbolLayer(layer_index)
                    layer.setAngle(layer.angle() + 180)
            for layer_index in range(start_marker.symbolLayerCount()):
                layer = start_marker.symbolLayer(layer_index)
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
            context.symbol_layer_output_to_input_index_map[line] = context.current_symbol_layer

        if 1 in positions:
            # end marker
            line = QgsMarkerLineSymbolLayer(not decoration.fixed_angle)

            end_marker = marker.clone()
            for layer_index in range(end_marker.symbolLayerCount()):
                layer = end_marker.symbolLayer(layer_index)
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
            context.symbol_layer_output_to_input_index_map[line] = context.current_symbol_layer

        if 0.5 in positions:
            # mid marker
            line = QgsMarkerLineSymbolLayer(not decoration.fixed_angle)

            end_marker = marker.clone()
            for layer_index in range(end_marker.symbolLayerCount()):
                layer = end_marker.symbolLayer(layer_index)
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
            context.symbol_layer_output_to_input_index_map[line] = context.current_symbol_layer

        # TODO other positions
        other_positions = [p for p in positions if p not in (0, 0.5, 1)]
        if other_positions:
            # Would need to use data defined marker placement distance, e.g. $length/3
            # and offset first marker by $length/3 to avoid placing a marker at the start
            # of the line
            raise NotImplementedException(
                'Non start/end decoration positions are not implemented (need {})'.format(other_positions))
