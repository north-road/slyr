#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object
from ..stream import Stream


class EditTemplateManager(Object):
    """
    EditTemplateManager
    """

    @staticmethod
    def cls_id():
        return 'a0162e85-e170-4b10-a370-cee08d8d4b8c'

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.templates = []

    @staticmethod
    def compatible_versions():
        return [1, 2]

    def read(self, stream: Stream, version):
        templates_count = stream.read_int('template count')
        for i in range(templates_count):
            self.templates.append(stream.read_object('template {}'.format(i + 1)))

        if version > 1:
            stream.read_uchar('unknown', expected=1)

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            'templates': [t.to_dict() for t in self.templates]
        }
