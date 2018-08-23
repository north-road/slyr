#!/usr/bin/env python

"""
Dumps the contents of an ESRI .style file
"""

import argparse
from io import BytesIO
from slyr.bintools.extractor import Extractor
from slyr.parser.symbol_parser import read_symbol

parser = argparse.ArgumentParser()
parser.add_argument("file", help="style file to extract", nargs='?')
args = parser.parse_args()

if not args.file:
    args.file = '/home/nyall/Styles/GEO_Surface___Solid_Shades.style'

styles = [(args.file, Extractor.FILL_SYMBOLS)]

for (fill_style_db, symbol_type) in styles:
    print('{}:{}'.format(fill_style_db, symbol_type))

    raw_symbols = Extractor.extract_styles(fill_style_db, symbol_type)
    print('Found {} symbols of type "{}"\n\n'.format(len(raw_symbols), symbol_type))

    for index, symbol in enumerate(raw_symbols):
        print('{}.\t{}\n\tCategory: {}\n\tTags: {}'.format(index + 1,
                                                          symbol[Extractor.NAME],
                                                          symbol[Extractor.CATEGORY],
                                                          symbol[Extractor.TAGS]))

        handle = BytesIO(symbol[Extractor.BLOB])
        symbol_properties = read_symbol(file_handle=handle)
        print(symbol_properties)
        print('\n\n')
