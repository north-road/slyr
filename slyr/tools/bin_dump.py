#!/usr/bin/env python

"""
Converts a binary style file blob to a symbol and dumps its properties to the console
"""

import argparse
import pprint

from slyr.parser.symbol_parser import read_symbol
from slyr.converters.dictionary import DictionaryConverter
from slyr.bin_tools.scanner import SCANNERS

parser = argparse.ArgumentParser()
parser.add_argument("file", help="bin file to parse")
parser.add_argument('--debug', help='Debug mode', action='store_true')
parser.add_argument('--scan', help='Scan mode', action='store_true')

args = parser.parse_args()

if args.scan:
    from colorama import init, Fore

    init()

    print('Scanning....')
    with open(args.file, 'rb') as f:

        f.seek(0, 2)
        length_file = f.tell()
        f.seek(0)
        colors = [Fore.WHITE] * length_file

        scan_results_array = [None] * length_file
        scan_results = []

        while True:

            for s in SCANNERS:
                res = s.scan(f)
                if res is not None:
                    scan_results.append(res)
                    for i in range(res.match_start, res.match_end):
                        if scan_results_array[i] is None or scan_results_array[i].precedence() < res.precedence():
                            scan_results_array = scan_results_array[:i] + [res] + scan_results_array[i + 1:]

            if not f.read(1):
                break

        f.seek(0)

        while True:
            def format_line(line_start, line):
                def format_char(char):
                    hex_part = str(hex(char))[-2:]
                    if hex_part[0] == 'x':
                        hex_part = '0' + hex_part[1]
                    return hex_part

                formatted = ''
                for i, c in enumerate(line):
                    char = format_char(c)
                    if scan_results_array[line_start + i] is not None:
                        formatted += scan_results_array[line_start + i].color()
                    formatted += char + ' ' + Fore.WHITE
                    if i % 8 == 7:
                        formatted += ' '

                formatted += '\t'
                found_parts = []
                for res in scan_results:
                    if line_start <= res.match_start < line_start + 16:
                        found_parts.append(hex(res.match_start)[2:] + ':' + res.color() + res.value() + Fore.WHITE)

                formatted += ' '.join(found_parts)

                return formatted

            start = f.tell()
            part = f.read(16)
            print('{}\t{}'.format(hex(start), format_line(start, part)))
            if len(part) < 16:
                break

    print('Scanning complete\n\n\n')

with open(args.file, 'rb') as f:
    symbol = read_symbol(file_handle=f, debug=args.debug)

converter = DictionaryConverter()
pprint.pprint(converter.convert_symbol(symbol))
