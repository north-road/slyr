#!/usr/bin/env python
"""
Serializable object subclass
"""

from .picture_element import PictureElement


class TifPictureElement(PictureElement):
    """
    TifPictureElement
    """

    @staticmethod
    def cls_id():
        return "5e7c0920-14a5-11d3-80cf-0080c7597e71"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
