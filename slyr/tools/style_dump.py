#!/usr/bin/env python

"""
Dumps the contents of an ESRI .style file
"""

import argparse
from io import BytesIO
from slyr.bintools.extractor import Extractor
from slyr.parser.symbol_parser import read_symbol, UnreadableSymbolException

parser = argparse.ArgumentParser()
parser.add_argument("file", help="style file to extract")
args = parser.parse_args()

for symbol_type in (Extractor.FILL_SYMBOLS, Extractor.LINE_SYMBOLS, Extractor.MARKER_SYMBOLS):
    print('{}:{}'.format(args.file, symbol_type))

    raw_symbols = Extractor.extract_styles(args.file, symbol_type)
    print('Found {} symbols of type "{}"\n\n'.format(len(raw_symbols), symbol_type))

    for index, symbol in enumerate(raw_symbols):
        print('{}.\t{}\n\tCategory: {}\n\tTags: {}'.format(index + 1,
                                                          symbol[Extractor.NAME],
                                                          symbol[Extractor.CATEGORY],
                                                          symbol[Extractor.TAGS]))

        handle = BytesIO(symbol[Extractor.BLOB])
        try:
            symbol_properties = read_symbol(file_handle=handle)
            print(symbol_properties)
        except UnreadableSymbolException as e:
            print('\t**Symbol could not be parsed!:\n\t{}'.format(e))
        print('\n\n')
