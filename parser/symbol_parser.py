#!/usr/bin/env python

from struct import unpack
from color_parser import (read_color_model,
                          read_color)
import binascii

"""
Extracts a symbol from a style blob
"""


def consume_padding(file_handle):
    # read padding
    last_position = file_handle.tell()
    while binascii.hexlify(file_handle.read(1)) == '00':
        last_position = file_handle.tell()
        pass
    file_handle.seek(last_position)


class SymbolLayer():
    def __init__(self):
        self.locked = False
        self.enabled = True
        self.locked = False

    def read_enabled(self, file_handle):
        enabled = unpack("<I", file_handle.read(4))[0]
        self.enabled = enabled == 1

    def read_locked(self, file_handle):
        locked = unpack("<I", file_handle.read(4))[0]
        self.locked = locked == 1


class LineSymbolLayer(SymbolLayer):
    def __init__(self):
        SymbolLayer.__init__(self)
        self.color_model = None
        self.color = None

    @staticmethod
    def create(file_handle):
        layer_type = binascii.hexlify(file_handle.read(2))
        symbol_layer = None
        if layer_type == 'f9e5':
            return SimpleLineSymbolLayer()
        elif layer_type == 'fbe5':
            return CartographicLineSymbolLayer()
        elif layer_type == 'fae5':
            return LineSymbol()
        else:
            return None


class SimpleLineSymbolLayer(LineSymbolLayer):
    def __init__(self):
        LineSymbolLayer.__init__(self)
        self.width = None
        self.line_type = None

    def read(self, file_handle):
        magic_1 = binascii.hexlify(file_handle.read(14))
        assert magic_1 == '147992c8d0118bb6080009ee4e41', 'Differing magic string 1'
        unknown = binascii.hexlify(file_handle.read(1))
        assert unknown == '01', 'Differing unknown byte'
        consume_padding(file_handle)

        self.color_model = read_color_model(file_handle)

        magic_2 = binascii.hexlify(file_handle.read(18))
        assert magic_2 == 'c4e97e23d1d0118383080009b996cc010001', 'Differing magic string 1: {}'.format(magic_2)
        consume_padding(file_handle)

        self.color = read_color(file_handle)
        self.width = unpack("<d", file_handle.read(8))[0]
        self.line_type = LineSymbol.read_line_type(file_handle)

        terminator = binascii.hexlify(file_handle.read(1))
        assert terminator == '0d', 'Expecting 0d terminator, got {}'.format(terminator)
        file_handle.read(7)

class CartographicLineSymbolLayer(LineSymbolLayer):
    def __init__(self):
        LineSymbolLayer.__init__(self)
        self.width = None
        self.cap = None
        self.join = None
        self.offset = None

    def read_cap(self, file_handle):
        cap_bin = unpack("<B", file_handle.read(1))[0]
        if cap_bin == 0:
            self.cap = 'butt'
        elif cap_bin == 1:
            self.cap = 'round'
        elif cap_bin == 2:
            self.cap = 'square'
        else:
            assert False, 'unknown cap style {}'.format(cap_bin)

    def read_join(self, file_handle):
        join_bin = unpack("<B", file_handle.read(1))[0]
        if join_bin == 0:
            self.join = 'miter'
        elif join_bin == 1:
            self.join = 'round'
        elif join_bin == 2:
            self.join = 'bevel'
        else:
            assert False, 'unknown join style {}'.format(join_bin)

    def read(self, file_handle):
        magic_1 = binascii.hexlify(file_handle.read(14))
        assert magic_1 == '147992c8d0118bb6080009ee4e41', 'Differing magic string 1'
        unknown = binascii.hexlify(file_handle.read(2))
        assert unknown == '0100', 'Differing unknown byte'

        self.read_cap(file_handle)

        unknown = binascii.hexlify(file_handle.read(3))
        assert unknown == '000000', 'Differing unknown string {}'.format(unknown)
        self.read_join(file_handle)
        unknown = binascii.hexlify(file_handle.read(3))
        assert unknown == '000000', 'Differing unknown string {}'.format(unknown)

        self.width = unpack("<d", file_handle.read(8))[0]

        unknown = binascii.hexlify(file_handle.read(1))
        assert unknown == '00', 'Differing unknown byte'

        self.offset= unpack("<d", file_handle.read(8))[0]

        self.color_model = read_color_model(file_handle)

        magic_2 = binascii.hexlify(file_handle.read(18))
        assert magic_2 == 'c4e97e23d1d0118383080009b996cc010001', 'Differing magic string 1: {}'.format(magic_2)
        consume_padding(file_handle)

        self.color = read_color(file_handle)

        # 48 unknown bytes!
        terminator = binascii.hexlify(file_handle.read(46))
        terminator = binascii.hexlify(file_handle.read(1))
        assert terminator == '0d', 'Expecting 0d terminator, got {} at {}'.format(terminator, hex(file_handle.tell()-1))
        file_handle.read(24)


class FillSymbolLayer(SymbolLayer):
    def __init__(self):
        SymbolLayer.__init__(self)
        self.color_model = None
        self.color = None
        self.outline_layer = None
        self.outline_symbol = None

    @staticmethod
    def create(file_handle):
        layer_type = binascii.hexlify(file_handle.read(2))
        symbol_layer = None
        if layer_type == '03e6':
            return SimpleFillSymbolLayer()
        else:
            return None


class SimpleFillSymbolLayer(FillSymbolLayer):
    def __init__(self):
        FillSymbolLayer.__init__(self)

    def read(self, file_handle):
        magic_1 = binascii.hexlify(file_handle.read(14))
        assert magic_1 == '147992c8d0118bb6080009ee4e41', 'Differing magic string 1'
        unknown = binascii.hexlify(file_handle.read(1))
        assert unknown == '01', 'Differing unknown byte'
        consume_padding(file_handle)

        outline = LineSymbolLayer.create(file_handle)
        if isinstance(outline, LineSymbol):
            # embedded outline symbol line
            self.outline_symbol = outline
            print 'starting outline symbol at {}'.format(hex(file_handle.tell()))
            self.outline_symbol.read(file_handle)

        else:
            self.outline_layer = outline
            self.outline_layer.read(file_handle)

        consume_padding(file_handle)

        # sometimes an extra 02 terminator here
        start = file_handle.tell()
        symbol_terminator = binascii.hexlify(file_handle.read(1))
        if symbol_terminator == '02':
            consume_padding(file_handle)
        else:
            file_handle.seek(start)

        self.color_model = read_color_model(file_handle)

        magic_2 = binascii.hexlify(file_handle.read(18))
        assert magic_2 == 'c4e97e23d1d0118383080009b996cc010001', 'Differing magic string 1: {}'.format(magic_2)
        file_handle.read(2)

        self.color = read_color(file_handle)

        terminator = binascii.hexlify(file_handle.read(1))
        assert terminator == '0d', 'Expecting 0d terminator, got {}'.format(terminator)
        file_handle.read(11)


class Symbol:
    def __init__(self):
        self.levels = []

    def read(self, file_handle):
        magic_1 = binascii.hexlify(file_handle.read(14))
        assert magic_1 == '147992c8d0118bb6080009ee4e41', 'Differing magic string 1'
        unknown_b = binascii.hexlify(file_handle.read(3))
        assert unknown_b == '02000d', 'Differing magic string b {}'.format(unknown_b)
        consume_padding(file_handle)
        self._read(file_handle)


class LineSymbol(Symbol):
    def __init__(self):
        Symbol.__init__(self)

    def _read(self, file_handle):
        number_layers = unpack("<L", file_handle.read(4))[0]
        print 'detected {} layers at {}'.format(number_layers, hex(file_handle.tell() - 4))

        for i in range(number_layers):
            layer = LineSymbolLayer.create(file_handle)
            if layer:
                layer.read(file_handle)
            self.levels.extend([layer])

        for l in self.levels:
            l.read_enabled(file_handle)
        for l in self.levels:
            l.read_locked(file_handle)

        print 'consuming padding at {}'.format(hex(file_handle.tell()))
        consume_padding(file_handle)

        symbol_terminator = binascii.hexlify(file_handle.read(1))
        assert symbol_terminator == '02', 'Differing terminator byte, expected 02 got {}'.format(symbol_terminator)

    @staticmethod
    def read_line_type(file_handle):
        type = unpack("<I", file_handle.read(4))[0]
        types = {0: 'solid',
                 1: 'dashed',
                 2: 'dotted',
                 3: 'dash dot',
                 4: 'dash dot dot',
                 5: 'null'
                 }
        return types[type]


class FillSymbol(Symbol):
    def __init__(self):
        Symbol.__init__(self)

    def _read(self, file_handle):

        # consume section of unknown purpose
        self.color_model = read_color_model(file_handle)
        magic_2 = binascii.hexlify(file_handle.read(18))
        assert magic_2 == 'c4e97e23d1d0118383080009b996cc010001', 'Differing magic string 1: {}'.format(magic_2)

        # either before or after this unknown color?
        file_handle.read(2)

        unknown_color = read_color(file_handle)
        assert unknown_color['R'] == 0
        assert unknown_color['G'] == 0
        assert unknown_color['B'] == 0
        assert not unknown_color['dither']
        assert not unknown_color['is_null']

        number_layers = unpack("<L", file_handle.read(4))[0]

        for i in range(number_layers):
            layer = FillSymbolLayer.create(file_handle)
            if layer:
                layer.read(file_handle)
            self.levels.extend([layer])

        for l in self.levels:
            l.read_enabled(file_handle)
        for l in self.levels:
            l.read_locked(file_handle)

            # symbol_terminator = binascii.hexlify(file_handle.read(1))
            # assert symbol_terminator == '02', 'Differing terminator byte, expected 02 got {}'.format(symbol_terminator)
            # consume_padding(file_handle)


class MarkerSymbol(Symbol):
    pass


def read_symbol(file_handle):
    symbol_type = binascii.hexlify(file_handle.read(2))
    symbol = None
    if symbol_type == '04e6':
        symbol = FillSymbol()
    elif symbol_type == 'ffe5':
        symbol = MarkerSymbol()
    elif symbol_type == 'fae5':
        symbol = LineSymbol()
    assert symbol, 'Unknown symbol type'
    symbol.read(file_handle)
    return symbol
