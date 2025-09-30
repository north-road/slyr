#!/usr/bin/env python
"""
Serializable object subclass
"""

from .picture_element import PictureElement


class PngPictureElement(PictureElement):
    """
    PngPictureElement
    """

    @staticmethod
    def cls_id():
        return "85cd6330-d45a-11d3-a414-0004ac1b1d86"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
