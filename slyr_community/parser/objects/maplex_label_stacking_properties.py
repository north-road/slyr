#!/usr/bin/env python
"""
MaplexLabelStackingProperties
"""

from ..object import Object
from ..stream import Stream


class MaplexLabelStackingProperties(Object):
    """
    MaplexLabelStackingProperties
    """

    STACKING_JUSTIFICATION_BEST = 0
    STACKING_JUSTIFICATION_LEFT_OR_RIGHT = 1
    STACKING_JUSTIFICATION_LEFT = 2
    STACKING_JUSTIFICATION_RIGHT = 3
    STACKING_JUSTIFICATION_CENTER = 4

    @staticmethod
    def cls_id():
        return '20664808-41c9-11d1-840a-08abc9ed731a'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.stacking_justification = MaplexLabelStackingProperties.STACKING_JUSTIFICATION_BEST
        self.stacking_separators = []
        self.max_stacking_lines = 0
        self.min_stacking_chars_per_line = 0
        self.max_stacking_chars_per_line = 0

    @staticmethod
    def compatible_versions():
        return [3]

    @staticmethod
    def stacking_justification_to_string(justification):
        """
        Convert stacking justification to string
        """
        if justification == MaplexLabelStackingProperties.STACKING_JUSTIFICATION_BEST:
            return 'best'
        elif justification == MaplexLabelStackingProperties.STACKING_JUSTIFICATION_LEFT_OR_RIGHT:
            return 'left_or_right'
        elif justification == MaplexLabelStackingProperties.STACKING_JUSTIFICATION_LEFT:
            return 'left'
        elif justification == MaplexLabelStackingProperties.STACKING_JUSTIFICATION_RIGHT:
            return 'right'
        elif justification == MaplexLabelStackingProperties.STACKING_JUSTIFICATION_CENTER:
            return 'center'
        return None

    def read(self, stream: Stream, version):
        self.stacking_justification = stream.read_int('stacking justification')
        stacking_separator_count = stream.read_int('stacking_separator_count')
        for i in range(stacking_separator_count):
            separator = stream.read_stringv2('separator {}'.format(i + 1))
            visible = stream.read_ushort('visible') != 0
            forced_split = stream.read_ushort('forced split') != 0
            split_after = stream.read_ushort('split after') != 0
            self.stacking_separators.append({'separator': separator,
                                             'forced_split': forced_split,
                                             'visible': visible,
                                             'split_after': split_after})
        self.max_stacking_lines = stream.read_int('max lines')
        self.min_stacking_chars_per_line = stream.read_int('min chars per line')
        self.max_stacking_chars_per_line = stream.read_int('max characters per line')

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'stacking_justification': MaplexLabelStackingProperties.stacking_justification_to_string(
                self.stacking_justification),
            'stacking_separators': self.stacking_separators,
            'max_stacking_lines': self.max_stacking_lines,
            'min_stacking_chars_per_line': self.min_stacking_chars_per_line,
            'max_stacking_chars_per_line': self.max_stacking_chars_per_line,
        }
