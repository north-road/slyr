#!/usr/bin/env python

"""
Converts a binary style file blob to a symbol and dumps its properties to the console
"""

import argparse
from slyr.parser.symbol_parser import read_symbol

parser = argparse.ArgumentParser()
parser.add_argument("file", help="bin file to parse")
args = parser.parse_args()

with open(args.file, 'rb') as f:
    symbol_properties = read_symbol(file_handle=f)
    print(symbol_properties)
    print('\n\n')
