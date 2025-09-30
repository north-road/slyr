#!/usr/bin/env python
"""
Serializable object subclass
"""

from .picture_element import PictureElement


class GifPictureElement(PictureElement):
    """
    GifPictureElement
    """

    @staticmethod
    def cls_id():
        return "4a7c82b0-1953-11d3-a3ee-0004ac1b1d86"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
