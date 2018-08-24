#!/usr/bin/env python

"""
Converts a binary style file blob to a symbol and dumps its properties to the console
"""

import argparse
import pprint
from slyr.parser.symbol_parser import read_symbol
from slyr.converters.dictionary import DictionaryConverter

parser = argparse.ArgumentParser()
parser.add_argument("file", help="bin file to parse")
args = parser.parse_args()

with open(args.file, 'rb') as f:
    symbol = read_symbol(file_handle=f)

converter = DictionaryConverter()
pprint.pprint(converter.convert_symbol(symbol))
