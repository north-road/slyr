#!/usr/bin/env python

"""
Dumps the contents of an ESRI .style file to a QGIS style library XML
"""

import argparse
from io import BytesIO
from qgis.core import QgsStyle
from slyr.bintools.extractor import Extractor
from slyr.parser.symbol_parser import read_symbol, UnreadableSymbolException
from slyr.converters.qgis import FillSymbol_to_QgsFillSymbol

from slyr.parser.initalize_registry import initialize_registry

initialize_registry()


parser = argparse.ArgumentParser()
parser.add_argument("file", help="style file to extract", nargs='?')
parser.add_argument("destination", help="QGIS symbol XML file destination", nargs='?')
args = parser.parse_args()

if not args.file:
    args.file = '/home/nyall/Styles/GEO_Surface___Solid_Shades.style'

if not args.destination:
    args.destination = '/home/nyall/Styles/GEO_Surface___Solid_Shades.xml'

styles = [(args.file, Extractor.FILL_SYMBOLS)]

style = QgsStyle()

for (fill_style_db, symbol_type) in styles:
    print('{}:{}'.format(fill_style_db, symbol_type))

    raw_symbols = Extractor.extract_styles(fill_style_db, symbol_type)
    print('Found {} symbols of type "{}"\n\n'.format(len(raw_symbols), symbol_type))

    for index, raw_symbol in enumerate(raw_symbols):
        name = raw_symbol[Extractor.NAME]
        # print('{}/{}: {}'.format(index + 1, len(raw_symbols),name))

        handle = BytesIO(raw_symbol[Extractor.BLOB])
        try:
            symbol = read_symbol(file_handle=handle)
        except UnreadableSymbolException:
            print('Error reading symbol {}'.format(name))
            continue

        qgis_symbol = FillSymbol_to_QgsFillSymbol(symbol)
        style.addSymbol(name, qgis_symbol)

style.exportXml(args.destination)
