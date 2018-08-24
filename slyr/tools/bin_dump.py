#!/usr/bin/env python

"""
Converts a binary style file blob to a symbol and dumps its properties to the console
"""

import argparse
import pprint
import subprocess
from slyr.parser.symbol_parser import read_symbol
from slyr.converters.dictionary import DictionaryConverter

parser = argparse.ArgumentParser()
parser.add_argument("file", help="bin file to parse")
parser.add_argument('--debug', help='Debug mode', action='store_true')

args = parser.parse_args()

if args.debug:
    dump_args = ['hexdump',
                 '-C',
                 args.file]
    result = subprocess.run(dump_args, stdout=subprocess.PIPE)
    print(result.stdout.decode('UTF-8'))

with open(args.file, 'rb') as f:
    symbol = read_symbol(file_handle=f, debug=args.debug)

converter = DictionaryConverter()
pprint.pprint(converter.convert_symbol(symbol))
