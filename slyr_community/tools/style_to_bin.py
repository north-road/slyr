#!/usr/bin/env python3

"""
Dumps the contents of an ESRI .style file to separate bin files
"""

import argparse
import os
from slyr_community.bintools.extractor import Extractor
from slyr_community.parser.initalize_registry import initialize_registry
from slyr_community.bintools.file_utils import FileUtils

initialize_registry()


parser = argparse.ArgumentParser()
parser.add_argument("file", help="style file to extract")
parser.add_argument("destination", help="destination folder")
args = parser.parse_args()

styles = [(args.file, Extractor.FILL_SYMBOLS)]
output_path = args.destination

for symbol_type in [Extractor.FILL_SYMBOLS, Extractor.LINE_SYMBOLS, Extractor.MARKER_SYMBOLS, Extractor.COLORS, Extractor.COLOR_RAMPS]:

    raw_symbols = Extractor.extract_styles(args.file, symbol_type)
    print('Found {} symbols of type "{}"\n\n'.format(len(raw_symbols), symbol_type))

    for raw_symbol in raw_symbols:
        symbol_name = raw_symbol[Extractor.NAME]
        print('Extracting {}'.format(symbol_name))

        out_filename = FileUtils.clean_symbol_name_for_file(symbol_name) + '.bin'
        file = os.path.join(output_path, out_filename)
        with open(file, 'wb') as e:
            e.write(raw_symbol[Extractor.BLOB])
