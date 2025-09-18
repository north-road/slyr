#!/usr/bin/env python
"""
Serializable object subclass
"""

from .picture_element import PictureElement


class EmfPictureElement(PictureElement):
    """
    EmfPictureElement
    """

    @staticmethod
    def cls_id():
        return "827b9a90-c067-11d2-9f22-00c04f6bc8dd"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
