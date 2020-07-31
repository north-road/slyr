#!/usr/bin/env python
"""
Line template

COMPLETE INTERPRETATION
"""
from slyr_community.parser.object import Object
from slyr_community.parser.stream import Stream


class LineTemplate(Object):
    """
    Line pattern template
    """

    @staticmethod
    def cls_id():
        return '41093a71-cce1-11d0-bfaa-0080c7e24280'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.pattern_interval = 0
        self.pattern_parts = []

    def to_dict(self):
        out = {
            'pattern_interval': self.pattern_interval,
            'pattern_parts': self.pattern_parts
        }
        return out

    def read(self, stream: Stream, version):
        self.pattern_interval = stream.read_double('pattern interval')

        pattern_part_count = stream.read_int('pattern parts')
        self.pattern_parts = []
        for p in range(pattern_part_count):
            filled_squares = stream.read_double()
            empty_squares = stream.read_double()
            self.pattern_parts.append([filled_squares, empty_squares])

        pattern = ''
        for p in self.pattern_parts:
            pattern += '-' * int(p[0]) + '.' * int(p[1])
        stream.log('deciphered line pattern {} ending'.format(pattern))
