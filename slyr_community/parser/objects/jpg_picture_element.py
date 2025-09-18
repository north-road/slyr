#!/usr/bin/env python
"""
Serializable object subclass
"""

from .picture_element import PictureElement


class JpgPictureElement(PictureElement):
    """
    JpgPictureElement
    """

    @staticmethod
    def cls_id():
        return "06ac0980-1953-11d3-a3ee-0004ac1b1d86"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
