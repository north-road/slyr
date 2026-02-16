#!/usr/bin/env python
"""
Workspace name

COMPLETE INTERPRETATION - some properties of unknown use, but low value and parsing is robust
"""

from ..object import Object
from ..object_registry import REGISTRY
from ..stream import Stream


class WorkspaceName(Object):
    """
    Workspace name information
    """

    TYPES = {
        0: "ESRI_FILESYSTEM_WORKSPACE",
        1: "ESRI_LOCALDATABASE_WORKSPACE",
        2: "ESRI_REMOTEDATABASE_WORKSPACE",
        99: "IN_MEMORY_WORKSPACE",
    }

    @staticmethod
    def cls_id():
        return "5a350011-e371-11d1-aa82-00c04fa33a15"

    def __init__(self):  # pylint: disable=useless-super-delegation
        super().__init__()
        self.name = ""
        self.browse_name = ""
        self.connection_properties = None
        self.path_name = ""
        self.type = 0
        self.workspace_factory = None
        self.name_string = ""

    @staticmethod
    def compatible_versions():
        return [1]

    def read(self, stream: Stream, version):
        self.name = stream.read_string("path name")
        self.name_string = stream.read_string("name string")
        self.browse_name = stream.read_string("browse_name")
        self.connection_properties = stream.read_object("connection properties")
        if stream.read_uchar("has factory") != 0:
            self.workspace_factory = stream.read_object("workspace factory")
        self.type = stream.read_int("type")

    def to_dict(self):  # pylint: disable=method-hidden
        return {
            "name": self.name,
            "browse_name": self.browse_name,
            "connection_properties": self.connection_properties.to_dict()
            if self.connection_properties
            else None,
            "path_name": self.path_name,
            "workspace_type": WorkspaceName.TYPES[self.type],
            "workspace_factory": self.workspace_factory.to_dict(),
            "name_string": self.name_string,
        }

    @classmethod
    def from_dict(cls, definition: dict) -> "WorkspaceName":
        res = WorkspaceName()
        res.browse_name = definition["browse_name"]
        res.name = definition["name"]
        res.name_string = definition["name_string"]
        res.connection_properties = REGISTRY.create_object_from_dict(
            definition["connection_properties"]
        )
        res.path_name = definition["path_name"]
        res.type = [
            k
            for k, v in WorkspaceName.TYPES.items()
            if v == definition["workspace_type"]
        ][0]
        res.workspace_factory = REGISTRY.create_object_from_dict(
            definition["workspace_factory"]
        )
        return res
