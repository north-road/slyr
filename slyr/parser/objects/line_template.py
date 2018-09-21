#!/usr/bin/env python

from slyr.parser.object import Object
from slyr.parser.stream import Stream


class LineTemplate(Object):

    def __init__(self):
        super().__init__()
        self.pattern_interval = 0
        self.pattern_parts = []

    @staticmethod
    def guid():
        return '41093a71-cce1-11d0-bfaa-0080c7e24280'

    def read(self, stream: Stream):
        stream.read(2)

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
