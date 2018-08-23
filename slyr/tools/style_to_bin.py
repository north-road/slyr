#!/usr/bin/env python3

"""
Dumps the contents of an ESRI .style file to separate bin files
"""

import argparse
from io import BytesIO
import os
from slyr.bintools.extractor import Extractor


def clean_symbol_name_for_file(symbol_name):
    """nasty little function to remove some characters which will choke"""
    file_name = symbol_name
    file_name = file_name.replace('/', '_')
    file_name = file_name.replace('>', '_')
    file_name = file_name.replace('\\', '_')
    file_name = file_name.replace('?', '_')
    file_name = file_name.replace('*', '_')
    return file_name


parser = argparse.ArgumentParser()
parser.add_argument("file", help="style file to extract")
parser.add_argument("destination", help="destination folder")
args = parser.parse_args()

styles = [(args.file, Extractor.FILL_SYMBOLS)]
output_path = args.destination

for symbol_type in [Extractor.FILL_SYMBOLS, Extractor.LINE_SYMBOLS, Extractor.MARKER_SYMBOLS]:

    raw_symbols = Extractor.extract_styles(args.file, symbol_type)
    print('Found {} symbols of type "{}"\n\n'.format(len(raw_symbols), symbol_type))

    for raw_symbol in raw_symbols:
        symbol_name=raw_symbol[Extractor.NAME]
        print('Extracting {}'.format(symbol_name))

        out_filename=clean_symbol_name_for_file(symbol_name) + '.bin'
        file = os.path.join(output_path,out_filename)
        with open(file, 'wb') as e:
            e.write(raw_symbol[Extractor.BLOB])
