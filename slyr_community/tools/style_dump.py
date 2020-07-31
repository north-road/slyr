#!/usr/bin/env python

"""
Dumps the contents of an ESRI .style file
"""

import argparse
from io import BytesIO
from slyr_community.bintools.extractor import Extractor
from slyr_community.parser.symbol_parser import read_symbol, UnreadableSymbolException
from slyr_community.parser.color_parser import read_color_and_model

from slyr_community.parser.initalize_registry import initialize_registry

initialize_registry()


parser = argparse.ArgumentParser()
parser.add_argument("file", help="style file to extract")
args = parser.parse_args()

total = 0
unreadable = []

for symbol_type in (Extractor.FILL_SYMBOLS, Extractor.LINE_SYMBOLS, Extractor.MARKER_SYMBOLS, Extractor.COLORS):
    print('{}:{}'.format(args.file, symbol_type))

    raw_symbols = Extractor.extract_styles(args.file, symbol_type)
    print('Found {} symbols of type "{}"\n\n'.format(len(raw_symbols), symbol_type))

    for index, symbol in enumerate(raw_symbols):
        print('{}.\t{}\n\tCategory: {}\n\tTags: {}'.format(index + 1,
                                                           symbol[Extractor.NAME],
                                                           symbol[Extractor.CATEGORY],
                                                           symbol[Extractor.TAGS]))

        handle = BytesIO(symbol[Extractor.BLOB])
        if symbol_type == Extractor.COLORS:
            color_model, color = read_color_and_model(handle)
            print(color_model, color)
        else:
            try:
                symbol_properties = read_symbol(file_handle=handle)
                print(symbol_properties)
            except UnreadableSymbolException as e:
                print('\t**Symbol could not be parsed!:\n\t{}'.format(e))
                unreadable.append(symbol[Extractor.NAME])
        print('\n\n')
        total += 1

print('***Parsed {}/{} symbols'.format(total - len(unreadable), total))
if unreadable:
    print('Unreadable symbols:\n- {}'.format('\n- '.join(unreadable)))
