#!/usr/bin/env python
"""

FeatureDatasetName

PARTIAL INTERPRETATION - many values of unknown use, but parsing is robust
"""

from ..object import Object
from ..stream import Stream
from ..object_registry import REGISTRY


class FeatureDatasetName(Object):
    """
    FeatureDatasetName
    """

    DATASET_TYPES = {
        1: "DATASET_TYPE_ANY",
        2: "DATASET_TYPE_CONTAINER",
        3: "DATASET_TYPE_GEO",
        4: "DATASET_TYPE_FEATURE_DATASET",
        5: "DATASET_TYPE_FEATURE_CLASS",
        6: "DATASET_TYPE_PLANAR_GRAPH",
        7: "DATASET_TYPE_GEOMETRIC_NETWORK",
        8: "DATASET_TYPE_TOPOLOGY",
        9: "DATASET_TYPE_TEXT",
        10: "DATASET_TYPE_TABLE",
        11: "DATASET_TYPE_RELATIONSHIP_CLASS",
        12: "DATASET_TYPE_RASTER_DATASET",
        13: "DATASET_TYPE_RASTER_BAND",
        14: "DATASET_TYPE_TIN",
        15: "DATASET_TYPE_CAD_DRAWING",
        16: "DATASET_TYPE_RASTER_CATALOG",
    }

    @staticmethod
    def cls_id():
        return "198846cf-ca42-11d1-aa7c-00c04fa33a15"

    def __init__(self):
        super().__init__()
        self.category = ""
        self.name = ""
        self.subset_names = None
        self.dataset_type = 1
        self.workspace_name = None

    def read(self, stream: Stream, version):
        _ = stream.read_string("unknown")
        self.dataset_type = stream.read_uint("unknown")
        _ = stream.read_ushort("unknown")
        _ = stream.read_string("unknown")
        _ = stream.read_string("unknown")
        _ = stream.read_uchar("unknown")
        self.workspace_name = stream.read_object("workspace name")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "category": self.category,
            "name": self.name,
            "subset_names": self.subset_names,
            "dataset_type": self.DATASET_TYPES[self.dataset_type],
            "workspace_name": self.workspace_name.to_dict(),
        }

    @classmethod
    def from_dict(cls, definition: dict) -> "FeatureDatasetName":
        res = FeatureDatasetName()
        res.category = definition["category"]
        res.name = definition["name"]
        res.subset_names = definition["subset_names"]
        res.workspace_name = REGISTRY.create_object_from_dict(
            definition["workspace_name"]
        )
        res.dataset_type = [
            k
            for k, v in FeatureDatasetName.DATASET_TYPES.items()
            if v == definition["dataset_type"]
        ][0]
        return res
