from qgis.core import (QgsSimpleLineSymbolLayer,
                       QgsSimpleFillSymbolLayer,
                       QgsFillSymbol,
                       QgsSymbolLayerUtils,
                       QgsReadWriteContext,
                       QgsStyle)
from qgis.PyQt.QtCore import (Qt)
from qgis.PyQt.QtGui import (QColor)
from qgis.PyQt.QtXml import QDomDocument

from parser.symbol_parser import *
import argparse
import glob
import os

parser = argparse.ArgumentParser()
parser.add_argument("input", help="glob pattern for bin files to convert")
parser.add_argument("destination", help="QGIS symbol XML file destination")
args = parser.parse_args()

out_file = args.destination


def symbol_color_to_qcolor(color):
    return QColor(color['R'], color['G'], color['B'])


def points_to_mm(points):
    return points * 0.352778


def symbol_pen_to_qpenstyle(style):
    types = {'solid': Qt.SolidLine,
             'dashed': Qt.DashLine,
             'dotted': Qt.DotLine,
             'dash dot': Qt.DashDotLine,
             'dash dot dot': Qt.DashDotDotLine,
             'null': Qt.NoPen
             }
    return types[style]


def symbol_pen_to_qpencapstyle(style):
    types = {'butt': Qt.FlatCap,
             'round': Qt.RoundCap,
             'square': Qt.SquareCap
             }
    return types[style]


def symbol_pen_to_qpenjoinstyle(style):
    types = {'miter': Qt.MiterJoin,
             'round': Qt.RoundJoin,
             'bevel': Qt.BevelJoin
             }
    return types[style]


def SimpleLineSymbolLayer_to_QgsSimpleLineSymbolLayer(layer):
    out = QgsSimpleLineSymbolLayer(symbol_color_to_qcolor(layer.color),
                                   points_to_mm(layer.width),
                                   symbol_pen_to_qpenstyle(layer.line_type)
                                   )
    return out


def CartographicLineSymbolLayer_to_QgsSimpleLineSymbolLayer(layer):
    out = QgsSimpleLineSymbolLayer(symbol_color_to_qcolor(layer.color),
                                   points_to_mm(layer.width),
                                   symbol_pen_to_qpenstyle(layer.line_type)
                                   )
    out.setPenCapStyle(symbol_pen_to_qpencapstyle(layer.cap))
    out.setPenJoinStyle(symbol_pen_to_qpenjoinstyle(layer.join))
    out.setOffset(points_to_mm(layer.offset))
    return out


def SimpleFillSymbolLayer_to_QgsSimpleFillSymbolLayer(layer):
    out = QgsSimpleFillSymbolLayer(symbol_color_to_qcolor(layer.color))

    if layer.outline_layer:
        if isinstance(layer.outline_layer, SimpleLineSymbolLayer) or isinstance(layer.outline_layer,
                                                                                CartographicLineSymbolLayer):
            out.setStrokeColor(symbol_color_to_qcolor(layer.outline_layer.color))
            out.setStrokeWidth(points_to_mm(layer.outline_layer.width))
        if isinstance(layer.outline_layer, SimpleLineSymbolLayer):
            out.setStrokeStyle(symbol_pen_to_qpenstyle(layer.outline_layer.line_type))
        if isinstance(layer.outline_layer, CartographicLineSymbolLayer):
            out.setPenJoinStyle(symbol_pen_to_qpenjoinstyle(layer.outline_layer.join))
        # todo - change to new symbol layer if outline offset set
    else:
        # todo - outline symbol layer
        pass

    return out


def FillSymbolLayer_to_QgsFillSymbolLayer(layer):
    if isinstance(layer, SimpleFillSymbolLayer):
        return SimpleFillSymbolLayer_to_QgsSimpleFillSymbolLayer(layer)
    else:
        return None


def SymbolLayer_to_QgsSymbolLayer(layer):
    out = None
    if issubclass(layer.__class__, FillSymbolLayer):
        out = FillSymbolLayer_to_QgsFillSymbolLayer(layer)
    else:
        return None

    out.setEnabled(layer.enabled)
    out.setLocked(layer.locked)
    return out


def FillSymbol_to_QgsFillSymbol(symbol):
    out = QgsFillSymbol()
    if issubclass(symbol.__class__, SymbolLayer):
        out.changeSymbolLayer(0,SymbolLayer_to_QgsSymbolLayer(symbol))
    else:
        out.changeSymbolLayer(0,SymbolLayer_to_QgsSymbolLayer(symbol.levels[0]))
        for l in symbol.levels[1:]:
            out.appendSymbolLayer(SymbolLayer_to_QgsSymbolLayer(l))
    return out


style = QgsStyle()
print(args.input)
for file_name in glob.glob(args.input):

    _, name = os.path.split(file_name)
    name, _ = os.path.splitext(name)
    print(name)

    f = open(file_name, 'rb')
    symbol = read_symbol(f, False)
    qgis_symbol = FillSymbol_to_QgsFillSymbol(symbol)
    style.addSymbol(name, qgis_symbol)


style.exportXml(out_file)
