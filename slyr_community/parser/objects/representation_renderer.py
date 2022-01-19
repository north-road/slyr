#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class RepresentationRenderer(Object):
    """
    RepresentationRenderer
    """

    @staticmethod
    def cls_id():
        return '18db8dbb-f658-4c9c-ba71-175022e9ece3'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.hidden_legend_items = []
        self.representation_class = None
        self.draw_invisible = False
        self.invisible_color = None
        self.draw_invalid_rule = False
        self.invalid_rule_color = None

    @staticmethod
    def compatible_versions():
        return [7]

    def read(self, stream: Stream, version):
        self.representation_class = stream.read_object('representation class')

        self.draw_invisible = stream.read_ushort('draw invisible') != 0
        self.invisible_color = stream.read_object('invisible color')
        self.draw_invalid_rule = stream.read_ushort('draw invalid rule') != 0
        self.invalid_rule_color = stream.read_object('invalid rule color')

        stream.read_int('unknown', expected=0)
        stream.read_int('unknown', expected=0)
        stream.read_ushort('unknown', expected=(0, 65535))

        count = stream.read_int('count')
        for i in range(count):
            stream.read_int('unknown {}'.format(i + 1), expected=i + 1)
            res = stream.read_int('unknown {}'.format(i + 1), expected=(2, 3))
            stream.read_ushort('unknown {}'.format(i + 1), expected=65535)
            stream.read_ushort('unknown {}'.format(i + 1), expected=65535)
            stream.read_int('unknown {}'.format(i + 1), expected=0)
            stream.read_int('unknown {}'.format(i + 1), expected=0)
            stream.read_int('unknown {}'.format(i + 1), expected=0)
            if res == 3:
                stream.read_int('unknown {}'.format(i + 1), expected=1)
                stream.read_int('unknown {}'.format(i + 1), expected=0)

        count = stream.read_int('count')
        for i in range(count):
            self.hidden_legend_items.append(stream.read_int('hidden legend item {}'.format(i + 1)))

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'representation_class': self.representation_class.to_dict() if self.representation_class else None,
            'draw_invisible': self.draw_invisible,
            'invisible_color': self.invisible_color.to_dict() if self.invisible_color else None,
            'draw_invalid_rule': self.draw_invalid_rule,
            'invalid_rule_color': self.invalid_rule_color.to_dict() if self.invalid_rule_color else None,
            'hidden_legend_items': self.hidden_legend_items
        }
