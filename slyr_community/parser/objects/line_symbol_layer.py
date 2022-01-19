#!/usr/bin/env python
"""
Line symbol layer subclasses

COMPLETE INTERPRETATION of most common subclasses
"""

from .symbol_layer import SymbolLayer
from ..stream import Stream
from ..exceptions import UnreadableSymbolException


class LineSymbolLayer(SymbolLayer):
    """
    Base class for line symbol layers
    """

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.color = None

    def children(self):
        res = super().children()
        if self.color:
            res.append(self.color)
        return res

    @staticmethod
    def read_cap(stream: Stream):
        """
        Reads a line cap style from the stream
        """
        cap_bin = stream.read_int('cap')
        if cap_bin == 0:
            return 'butt'
        elif cap_bin == 1:
            return 'round'
        elif cap_bin == 2:
            return 'square'
        else:
            raise UnreadableSymbolException('unknown cap style {}'.format(cap_bin))

    @staticmethod
    def read_join(stream: Stream):
        """
        Reads a line join style from the stream
        """
        join_bin = stream.read_int('join')
        if join_bin == 0:
            return 'miter'
        elif join_bin == 1:
            return 'round'
        elif join_bin == 2:
            return 'bevel'
        else:
            raise UnreadableSymbolException('unknown join style {}'.format(join_bin))

    @staticmethod
    def read_line_type(stream: Stream):
        """
        Interprets the line type bytes
        """
        line_type = stream.read_uint()
        types = {0: 'solid',
                 1: 'dashed',
                 2: 'dotted',
                 3: 'dash dot',
                 4: 'dash dot dot',
                 5: 'null'}
        if line_type not in types:
            raise UnreadableSymbolException('unknown line type {} at {}'.format(line_type, hex(stream.tell() - 4)))
        return types[line_type]


class SimpleLineSymbol(LineSymbolLayer):
    """
    Simple line symbol layer
    """

    @staticmethod
    def cls_id():
        return '7914e5f9-c892-11d0-8bb6-080009ee4e41'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.width = None
        self.line_type = None

    @staticmethod
    def compatible_versions():
        return [1]

    def to_dict(self):  # pylint: disable=method-hidden
        out = {
            'color': self.color.to_dict() if self.color is not None else None,
            'width': self.width,
            'line_type': self.line_type
        }
        return out

    def read(self, stream: Stream, version):
        self.color = stream.read_object('color')
        self.width = stream.read_double('width')

        self.line_type = self.read_line_type(stream)
        stream.log('read line type of {}'.format(self.line_type))
        self.symbol_level = SymbolLayer.read_symbol_level(stream)


class CartographicLineSymbol(LineSymbolLayer):
    """
    Cartographic line symbol layer
    """

    @staticmethod
    def cls_id():
        return '7914e5fb-c892-11d0-8bb6-080009ee4e41'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.width = None
        self.cap = None
        self.join = None
        self.offset = None
        self.template = None
        self.decoration = None
        self.miter_limit = 0
        self.decoration_on_top = False
        self.flip = False
        self.line_start_offset = 0

    def to_dict(self):  # pylint: disable=method-hidden
        out = {
            'color': self.color.to_dict() if self.color is not None else None,
            'width': self.width,
            'offset': self.offset,
            'cap': self.cap,
            'join': self.join,
            'template': None,
            'decoration': None,
            'miter_limit': self.miter_limit,
            'decoration_on_top': self.decoration_on_top,
            'flip': self.flip,
            'line_start_offset': self.line_start_offset
        }
        if self.template is not None:
            out['template'] = self.template.to_dict()

        if self.decoration is not None:
            out['decoration'] = self.decoration.to_dict()

        return out

    def children(self):
        res = super().children()
        if self.template:
            res.append(self.template)
        if self.decoration:
            res.append(self.decoration)
        return res

    def read(self, stream: Stream, version):
        self.cap = self.read_cap(stream)
        self.join = self.read_join(stream)
        self.width = stream.read_double('width')

        self.flip = stream.read_uchar('flip') != 0

        self.offset = stream.read_double('offset')
        self.color = stream.read_object('color')
        self.template = stream.read_object('template')

        self.decoration = stream.read_object('decoration')
        self.symbol_level = SymbolLayer.read_symbol_level(stream)

        self.decoration_on_top = stream.read_uchar('decoration on top') != 0
        self.line_start_offset = stream.read_double('line start offset')
        self.miter_limit = stream.read_double('miter limit')


class MarkerLineSymbol(LineSymbolLayer):
    """
    Marker line symbol layer
    """

    @staticmethod
    def cls_id():
        return '7914e5fd-c892-11d0-8bb6-080009ee4e41'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.cap = None
        self.join = None
        self.offset = None
        self.template = None
        self.pattern_marker = None
        self.decoration = None
        self.line_start_offset = 0
        self.decoration_on_top = False
        self.miter_limit = 10
        self.flip = False

    @staticmethod
    def compatible_versions():
        return [2]

    def to_dict(self):  # pylint: disable=method-hidden
        out = {
            'color': self.color.to_dict() if self.color is not None else None,
            'offset': self.offset,
            'join': self.join,
            'template': None,
            'pattern_marker': None,
            'decoration': None,
            'line_start_offset': self.line_start_offset,
            'decoration_on_top': self.decoration_on_top,
            'miter_limit': self.miter_limit,
            'flip': self.flip
        }
        if self.template is not None:
            out['template'] = self.template.to_dict()

        if self.pattern_marker is not None:
            out['pattern_marker'] = self.pattern_marker.to_dict()

        if self.decoration is not None:
            out['decoration'] = self.decoration.to_dict()

        return out

    def children(self):
        res = super().children()
        if self.template:
            res.append(self.template)
        if self.decoration:
            res.append(self.decoration)
        if self.pattern_marker:
            res.append(self.pattern_marker)
        return res

    def read(self, stream: Stream, version):
        self.flip = stream.read_uchar('flip') != 0
        self.offset = stream.read_double('offset')
        self.pattern_marker = stream.read_object('pattern marker')
        self.template = stream.read_object('template')
        self.decoration = stream.read_object('decoration')

        self.symbol_level = SymbolLayer.read_symbol_level(stream)
        self.decoration_on_top = stream.read_uchar('decoration on top') != 0
        self.line_start_offset = stream.read_double('line start offset')

        self.cap = self.read_cap(stream)
        self.join = self.read_join(stream)
        self.miter_limit = stream.read_double('miter limit')


class HashLineSymbol(LineSymbolLayer):
    """
    Hash line symbol layer
    """

    @staticmethod
    def cls_id():
        return '7914e5fc-c892-11d0-8bb6-080009ee4e41'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.cap = None
        self.join = None
        self.offset = None
        self.template = None
        self.decoration = None
        self.line = None
        self.width = 0
        self.angle = 90
        self.line_start_offset = 0
        self.miter_limit = 10
        self.decoration_on_top = False
        self.flip = False

    @staticmethod
    def compatible_versions():
        return [1]

    def to_dict(self):  # pylint: disable=method-hidden
        out = {
            'color': self.color.to_dict() if self.color is not None else None,
            'width': self.width,
            'offset': self.offset,
            'cap': self.cap,
            'join': self.join,
            'template': None,
            'decoration': None,
            'line': None,
            'line_start_offset': self.line_start_offset,
            'miter_limit': self.miter_limit,
            'decoration_on_top': self.decoration_on_top,
            'flip': self.flip
        }
        if self.template is not None:
            out['template'] = self.template.to_dict()

        if self.line is not None:
            out['line'] = self.line.to_dict()

        if self.decoration is not None:
            out['decoration'] = self.decoration.to_dict()

        return out

    def children(self):
        res = super().children()
        if self.template:
            res.append(self.template)
        if self.decoration:
            res.append(self.decoration)
        if self.line:
            res.append(self.line)
        return res

    def read(self, stream: Stream, version):
        self.angle = stream.read_double('angle')
        self.cap = self.read_cap(stream)
        self.join = self.read_join(stream)
        self.width = stream.read_double('width')
        self.flip = stream.read_uchar('flip') != 0
        self.offset = stream.read_double('offset')

        self.line = stream.read_object('line')

        self.color = stream.read_object('color')
        self.template = stream.read_object('template')

        self.decoration = stream.read_object('decoration')
        self.symbol_level = SymbolLayer.read_symbol_level(stream)

        self.decoration_on_top = stream.read_uchar('decoration on top') != 0
        self.line_start_offset = stream.read_double('line start offset')
        self.miter_limit = stream.read_double('miter limit')


class PictureLineSymbol(LineSymbolLayer):
    """
    PictureLineSymbol
    """

    @staticmethod
    def cls_id():
        return '22c8c5a1-84fc-11d4-834d-0080c79f0371'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.offset = 0
        self.width = 0
        self.fill_symbol = None

    def read(self, stream: Stream, version):
        stream.read_uchar('unknown', expected=0)
        self.offset = stream.read_double('offset')
        self.width = stream.read_double('width')
        self.fill_symbol = stream.read_object('fill symbol')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'width': self.width,
            'offset': self.offset,
            'fill_symbol': self.fill_symbol.to_dict() if self.fill_symbol else None
        }
