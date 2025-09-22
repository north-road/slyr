#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object


class Element(Object):
    """
    Base class for elements
    """

    ANCHOR_TOP_LEFT = 0
    ANCHOR_TOP_MIDDLE = 1
    ANCHOR_TOP_RIGHT = 2
    ANCHOR_LEFT = 3
    ANCHOR_MIDDLE = 4
    ANCHOR_RIGHT = 5
    ANCHOR_BOTTOM_LEFT = 6
    ANCHOR_BOTTOM_MIDDLE = 7
    ANCHOR_BOTTOM_RIGHT = 8

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.anchor = Element.ANCHOR_TOP_LEFT
        self.shape = None
        self.preserve_aspect = False
        self.auto_transform = False
        self.element_name = ""
        self.element_type = ""
        self.symbol = None
        self.border = None
        self.background = None
        self.shadow = None
        self.reference_scale = 0
        self.locked = False
        self.custom_property = None
        self.draft_mode = False

    @staticmethod
    def anchor_to_string(anchor) -> str:
        """
        Converts element anchor to a string
        """
        if anchor == Element.ANCHOR_TOP_LEFT:
            return "top_left"
        elif anchor == Element.ANCHOR_TOP_MIDDLE:
            return "top_middle"
        elif anchor == Element.ANCHOR_TOP_RIGHT:
            return "top_right"
        elif anchor == Element.ANCHOR_LEFT:
            return "left"
        elif anchor == Element.ANCHOR_MIDDLE:
            return "middle"
        elif anchor == Element.ANCHOR_RIGHT:
            return "right"
        elif anchor == Element.ANCHOR_BOTTOM_LEFT:
            return "bottom_left"
        elif anchor == Element.ANCHOR_BOTTOM_MIDDLE:
            return "bottom_middle"
        elif anchor == Element.ANCHOR_BOTTOM_RIGHT:
            return "bottom_right"
        assert False

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "anchor": Element.anchor_to_string(self.anchor),
            "shape": self.shape.to_dict() if self.shape else None,
            "preserve_aspect": self.preserve_aspect,
            "element_name": self.element_name,
            "element_type": self.element_type,
            "symbol": self.symbol.to_dict() if self.symbol else None,
            "border": self.border.to_dict() if self.border else None,
            "background": self.background.to_dict() if self.background else None,
            "shadow": self.shadow.to_dict() if self.shadow else None,
            "reference_scale": self.reference_scale,
            "auto_transform": self.auto_transform,
            "locked": self.locked,
            "custom_property": self.custom_property,
            "draft_mode": self.draft_mode,
        }
