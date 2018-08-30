#!/usr/bin/env python

"""
Converts a binary style file blob to a symbol and dumps its properties to the console
"""

import argparse
import pprint
import subprocess
import string
from struct import unpack
import binascii

from slyr.parser.symbol_parser import read_symbol, read_string, Handle, read_color, read_magic_2, UnreadableSymbolException
from slyr.parser.color_parser import read_color_model,InvalidColorException
from slyr.converters.dictionary import DictionaryConverter

parser = argparse.ArgumentParser()
parser.add_argument("file", help="bin file to parse")
parser.add_argument('--debug', help='Debug mode', action='store_true')
parser.add_argument('--scan', help='Scan mode', action='store_true')

args = parser.parse_args()

if args.debug:
    dump_args = ['hexdump',
                 '-C',
                 args.file]
    result = subprocess.run(dump_args, stdout=subprocess.PIPE)
    print(result.stdout.decode('UTF-8'))


class ObjectScan:

    def scan(self, file_handle):
        start = file_handle.tell()
        res = self.check_handle(file_handle)
        file_handle.seek(start)
        return res

    def check_handle(self, file_handle):
        pass


class ObjectMatch:

    def __init__(self, match_start, match_length):
        self.match_start = match_start
        self.match_length = match_length
        self.match_end = match_start + match_length

    @staticmethod
    def precedence():
        return 1

    @staticmethod
    def color():
        return Fore.WHITE

    def value(self):
        return ''


class StringMatch(ObjectMatch):

    def __init__(self, match_start, match_length, found_string):
        super().__init__(match_start, match_length)
        self.found_string = found_string

    @staticmethod
    def precedence():
        return 100

    @staticmethod
    def color():
        return Fore.RED

    def value(self):
        return '"' + self.found_string + '"'


class StringScan(ObjectScan):
    PRINTABLE = set(string.printable)

    @staticmethod
    def strip_non_ascii(string):
        return ''.join(filter(lambda x: x in StringScan.PRINTABLE, string))

    def check_handle(self, file_handle):
        try:
            start = file_handle.tell()
            string_value = read_string(Handle(file_handle))
            if string_value and StringScan.strip_non_ascii(string_value) == string_value:
                return StringMatch(start, file_handle.tell() - start, string_value)
        except:
            return None


class ObjectCodeMatch(ObjectMatch):

    def __init__(self, match_start, match_length, found_type):
        super().__init__(match_start, match_length)
        self.found_type = found_type

    @staticmethod
    def precedence():
        return 50

    @staticmethod
    def color():
        return Fore.CYAN

    def value(self):
        return self.found_type


class ObjectCodeScan(ObjectScan):
    OBJECT_DICT = {
        b'04e6': 'FillSymbol',
        b'ffe5': 'MarkerSymbol',
        b'fae5': 'LineSymbol',
        b'f9e5': 'SimpleLineSymbolLayer',
        b'fbe5': 'CartographicLineSymbolLayer',
        b'03e6': 'SimpleFillSymbolLayer',
        b'fee5': 'SimpleMarkerSymbolLayer',
        b'00e6': 'CharacterMarkerSymbolLayer',
        b'02e6': 'PictureMarkerSymbolLayer'
    }

    def check_handle(self, file_handle):
        try:
            object_type = binascii.hexlify(file_handle.read(2))
            if object_type in self.OBJECT_DICT:
                return ObjectCodeMatch(file_handle.tell() - 2, 2, self.OBJECT_DICT[object_type])
        except:
            return None


class DoubleMatch(ObjectMatch):

    def __init__(self, match_start, match_length, found_value):
        super().__init__(match_start, match_length)
        self.found_value = found_value

    @staticmethod
    def precedence():
        return 30

    @staticmethod
    def color():
        return Fore.GREEN

    def value(self):
        return str(self.found_value)


class DoubleScan(ObjectScan):

    def check_handle(self, file_handle):
        try:
            real_value = unpack("<d", f.read(8))[0]
            if -1000 < real_value < 10000 and (real_value > 0.00001 or real_value < -0.00001) \
                    and round(real_value * 10) == real_value * 10:
                return DoubleMatch(file_handle.tell() - 8, 8, real_value)
        except:
            return None


class IntMatch(ObjectMatch):

    def __init__(self, match_start, match_length, found_value):
        super().__init__(match_start, match_length)
        self.found_value = found_value

    @staticmethod
    def precedence():
        return 20

    @staticmethod
    def color():
        return Fore.YELLOW

    def value(self):
        return str(self.found_value)


class IntScan(ObjectScan):

    def check_handle(self, file_handle):
        try:
            int_value = unpack("<I", f.read(4))[0]
            if -100 < int_value < 255 and int_value != 0:
                return IntMatch(file_handle.tell() - 4, 4, int_value)
        except:
            return None


class Magic1Match(ObjectMatch):

    def __init__(self, match_start, match_length):
        super().__init__(match_start, match_length)

    @staticmethod
    def precedence():
        return 25

    @staticmethod
    def color():
        return Fore.BLUE

    def value(self):
        return '147992c8d0118bb6080009ee4e41'


class Magic1Scan(ObjectScan):

    def check_handle(self, file_handle):
        try:
            magic = binascii.hexlify(f.read(14))
            if magic == b'147992c8d0118bb6080009ee4e41':
                return Magic1Match(file_handle.tell() - 14, 14)
        except:
            return None


class Magic2Match(ObjectMatch):

    def __init__(self, match_start, match_length):
        super().__init__(match_start, match_length)

    @staticmethod
    def precedence():
        return 25

    @staticmethod
    def color():
        return Fore.LIGHTBLUE_EX

    def value(self):
        return 'c4e97e23d1d0118383080009b996cc'


class Magic2Scan(ObjectScan):

    def check_handle(self, file_handle):
        try:
            magic = binascii.hexlify(f.read(15))
            if magic == b'c4e97e23d1d0118383080009b996cc':
                return Magic2Match(file_handle.tell() - 15, 15)
        except:
            return None


class ColorMatch(ObjectMatch):

    def __init__(self, match_start, match_length, matched_color):
        super().__init__(match_start, match_length)
        self.matched_color = matched_color

    @staticmethod
    def precedence():
        return 80

    @staticmethod
    def color():
        return Fore.MAGENTA

    def value(self):
        return str(self.matched_color['R']) + ',' + str(self.matched_color['G']) + ',' + str(self.matched_color['B'])


class ColorScan(ObjectScan):

    def check_handle(self, file_handle):
        try:
            start = file_handle.tell()
            color_model = read_color_model(file_handle)
            if color_model == 'rgb':
                read_magic_2(Handle(file_handle))
                file_handle.read(2)
                color = read_color(file_handle)
                if True or (color['R'] == 255 or color['G'] == 255 or color['B'] == 255) and (
                        not color['dither'] and not color['is_null']):
                    return ColorMatch(start, file_handle.tell() - start, color)
        except:
            return None


SCANNERS = [StringScan(), ObjectCodeScan(), DoubleScan(), IntScan(), Magic1Scan(), Magic2Scan(), ColorScan()]

if args.scan:
    from colorama import init, Fore, Back, Style

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
