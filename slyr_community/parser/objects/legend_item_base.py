#!/usr/bin/env python
"""
Serializable object subclass
"""

from ..object import Object


class LegendItemBase(Object):
    """
    LegendItemBase
    """

    ARRANGEMENT_SYMBOL_LABEL_DESCRIPTION = 0
    ARRANGEMENT_SYMBOL_DESCRIPTION_LABEL = 1
    ARRANGEMENT_LABEL_SYMBOL_DESCRIPTION = 2
    ARRANGEMENT_LABEL_DESCRIPTION_SYMBOL = 3
    ARRANGEMENT_DESCRIPTION_SYMBOL_LABEL = 4
    ARRANGEMENT_DESCRIPTION_LABEL_SYMBOL = 5

    @staticmethod
    def arrangement_to_string(arrangement) -> str:
        """
        Converts legend arrangement to a string
        """
        if arrangement == LegendItemBase.ARRANGEMENT_SYMBOL_LABEL_DESCRIPTION:
            return "symbol_label_description"
        elif arrangement == LegendItemBase.ARRANGEMENT_SYMBOL_DESCRIPTION_LABEL:
            return "symbol_description_label"
        elif arrangement == LegendItemBase.ARRANGEMENT_LABEL_SYMBOL_DESCRIPTION:
            return "label_symbol_description"
        elif arrangement == LegendItemBase.ARRANGEMENT_LABEL_DESCRIPTION_SYMBOL:
            return "label_description_symbol"
        elif arrangement == LegendItemBase.ARRANGEMENT_DESCRIPTION_SYMBOL_LABEL:
            return "description_symbol_label"
        elif arrangement == LegendItemBase.ARRANGEMENT_DESCRIPTION_LABEL_SYMBOL:
            return "description_label_symbol"
        assert False

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.show_heading = True
        self.heading_text_symbol = None
        self.legend_class_format = None
        self.show_labels = True
        self.show_description = True
        self.prevent_column_split = False
        self.arrangement = LegendItemBase.ARRANGEMENT_SYMBOL_LABEL_DESCRIPTION
        self.angle_text_above = 0
        self.angle_text_below = 0
        self.show_layer_name = False
        self.layer_name_text_symbol = None
        self.place_in_new_column = False
        self.column_count = 1
        self.layer = None
        self.only_show_classes_visible_in_map = False
        self.show_feature_count = False
        self.before_count = " ("
        self.after_count = ")"
        self.count_format = None
        self.group_index = 0

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "layer": self.layer,
            "place_in_new_column": self.place_in_new_column,
            "column_count": self.column_count,
            "show_heading": self.show_heading,
            "heading_text_symbol": self.heading_text_symbol.to_dict()
            if self.heading_text_symbol
            else None,
            "legend_class_format": self.legend_class_format.to_dict()
            if self.legend_class_format
            else None,
            "show_labels": self.show_labels,
            "show_description": self.show_description,
            "prevent_column_split": self.prevent_column_split,
            "arrangement": LegendItemBase.arrangement_to_string(self.arrangement),
            "angle_text_above": self.angle_text_above,
            "angle_text_below": self.angle_text_below,
            "show_layer_name": self.show_layer_name,
            "layer_name_text_symbol": self.layer_name_text_symbol.to_dict()
            if self.layer_name_text_symbol
            else None,
            "only_show_classes_visible_in_map": self.only_show_classes_visible_in_map,
            "show_feature_count": self.show_feature_count,
            "before_count": self.before_count,
            "after_count": self.after_count,
            "count_format": self.count_format.to_dict() if self.count_format else None,
            "group_index": self.group_index,
        }
