#!/usr/bin/env python
"""

FeatureDatasetName

PARTIAL INTERPRETATION - many values of unknown use, but parsing is robust
"""

from ..object import Object
from ..stream import Stream


class NetworkDatasetName(Object):
    """
    NetworkDatasetName
    """

    @staticmethod
    def cls_id():
        return "8167fe6a-e992-4ecb-b6ae-e5dfe4655247"

    def __init__(self):
        super().__init__()
        self.category = ""
        self.name = ""
        self.subset_names = None
        self.dataset_type = 1
        self.workspace_name = None

    def read(self, stream: Stream, version):
        _ = stream.read_string("unknown")
        _ = stream.read_string("unknown")
        stream.read_object("feature dataset name")
        self.workspace_name = stream.read_object("workspace name")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "category": self.category,
            "name": self.name,
            "subset_names": self.subset_names,
            "dataset_type": self.dataset_type,
            "workspace_name": self.workspace_name.to_dict(),
        }
