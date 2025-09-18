#!/usr/bin/env python
"""
Serializable object subclass
"""

from .picture_element import PictureElement


class Jp2PictureElement(PictureElement):
    """
    Jp2PictureElement
    """

    @staticmethod
    def cls_id():
        return "8bbf863b-d0c7-4b5f-88b0-21d5a4ca06fd"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
