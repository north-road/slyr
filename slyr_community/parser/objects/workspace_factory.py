#!/usr/bin/env python
"""
Workspace factories

Note that these are of limited value -- they aren't serializable and don't
store any useful properties of their own.
"""

from ..object import Object
from ..stream import Stream


class WorkspaceFactory(Object):
    """
    WorkspaceFactory
    """

    @staticmethod
    def compatible_versions():
        return None

    @staticmethod
    def supports_references():
        return False

    def read(self, stream: Stream, version):
        pass

    def to_dict(self):  # pylint: disable=method-hidden
        return {
        }


class SdeWorkspaceFactory(WorkspaceFactory):
    """
    SdeWorkspaceFactory
    """

    @staticmethod
    def cls_id():
        return 'd9b4fa40-d6d9-11d1-aa81-00c04fa33a15'

    @classmethod
    def from_dict(cls, definition: dict) -> 'SdeWorkspaceFactory':
        return SdeWorkspaceFactory()


class AccessWorkspaceFactory(WorkspaceFactory):
    """
    AccessWorkspaceFactory
    """

    @staticmethod
    def cls_id():
        return 'dd48c96a-d92a-11d1-aa81-00c04fa33a15'

    @classmethod
    def from_dict(cls, definition: dict) -> 'AccessWorkspaceFactory':
        return AccessWorkspaceFactory()


class ArcInfoWorkspaceFactory(WorkspaceFactory):
    """
    ArcInfoWorkspaceFactory
    """

    @staticmethod
    def cls_id():
        return '1d887452-d9f2-11d1-aa81-00c04fa33a15'

    @classmethod
    def from_dict(cls, definition: dict) -> 'ArcInfoWorkspaceFactory':
        return ArcInfoWorkspaceFactory()


class CadWorkspaceFactory(WorkspaceFactory):
    """
    CadWorkspaceFactory
    """

    @staticmethod
    def cls_id():
        return '9e2c27ce-62c6-11d2-9aed-00c04fa33299'

    @classmethod
    def from_dict(cls, definition: dict) -> 'CadWorkspaceFactory':
        return CadWorkspaceFactory()


class IMSWorkspaceFactory(WorkspaceFactory):
    """
    IMSWorkspaceFactory
    """

    @staticmethod
    def cls_id():
        return 'bac84d58-fa9d-11d3-9f48-00c04f79927c'

    @classmethod
    def from_dict(cls, definition: dict) -> 'IMSWorkspaceFactory':
        return IMSWorkspaceFactory()


class OLEDBWorkspaceFactory(WorkspaceFactory):
    """
    OLEDBWorkspaceFactory
    """

    @staticmethod
    def cls_id():
        return '59158055-3171-11d2-aa94-00c04fa37849'

    @classmethod
    def from_dict(cls, definition: dict) -> 'OLEDBWorkspaceFactory':
        return OLEDBWorkspaceFactory()


class PCCoverageWorkspaceFactory(WorkspaceFactory):
    """
    PCCoverageWorkspaceFactory
    """

    @staticmethod
    def cls_id():
        return '6de812d2-9ab6-11d2-b0d7-0000f8780820'

    @classmethod
    def from_dict(cls, definition: dict) -> 'PCCoverageWorkspaceFactory':
        return PCCoverageWorkspaceFactory()


class RasterWorkspaceFactory(WorkspaceFactory):
    """
    RasterWorkspaceFactory
    """

    @staticmethod
    def cls_id():
        return '4c91d963-3390-11d2-8d25-0000f8780535'

    @classmethod
    def from_dict(cls, definition: dict) -> 'RasterWorkspaceFactory':
        return RasterWorkspaceFactory()


class ShapefileWorkspaceFactory(WorkspaceFactory):
    """
    ShapefileWorkspaceFactory
    """

    @staticmethod
    def cls_id():
        return 'a06adb96-d95c-11d1-aa81-00c04fa33a15'

    @classmethod
    def from_dict(cls, definition: dict) -> 'ShapefileWorkspaceFactory':
        return ShapefileWorkspaceFactory()


class FileGDBWorkspaceFactory(WorkspaceFactory):
    """
    FileGDBWorkspaceFactory
    """

    @staticmethod
    def cls_id():
        return '71fe75f0-ea0c-4406-873e-b7d53748ae7e'

    @staticmethod
    def supports_references():
        return False

    @classmethod
    def from_dict(cls, definition: dict) -> 'FileGDBWorkspaceFactory':
        return FileGDBWorkspaceFactory()


class TextFileWorkspaceFactory(WorkspaceFactory):
    """
    TextFileWorkspaceFactory
    """

    @staticmethod
    def cls_id():
        return '72ce59ec-0be8-11d4-ae03-00c04fa33a15'

    @classmethod
    def from_dict(cls, definition: dict) -> 'TextFileWorkspaceFactory':
        return TextFileWorkspaceFactory()


class TinWorkspaceFactory(WorkspaceFactory):
    """
    TinWorkspaceFactory
    """

    @staticmethod
    def cls_id():
        return 'ad4e89d9-00a5-11d2-b1ca-00c04f8edeff'

    @classmethod
    def from_dict(cls, definition: dict) -> 'TinWorkspaceFactory':
        return TinWorkspaceFactory()


class VpfWorkspaceFactory(WorkspaceFactory):
    """
    VpfWorkspaceFactory
    """

    @staticmethod
    def cls_id():
        return '397847f9-c865-11d3-9b56-00c04fa33299'

    @classmethod
    def from_dict(cls, definition: dict) -> 'VpfWorkspaceFactory':
        return VpfWorkspaceFactory()


class FeatureServiceWorkspaceFactory(WorkspaceFactory):
    """
    FeatureServiceWorkspaceFactory
    """

    @staticmethod
    def cls_id():
        return 'c81194e7-4daa-418b-8c83-2942e65d2b8c'

    @classmethod
    def from_dict(cls, definition: dict) -> 'FeatureServiceWorkspaceFactory':
        return FeatureServiceWorkspaceFactory()


class SdcWorkspaceFactory(WorkspaceFactory):
    """
    SdcWorkspaceFactory
    """

    @staticmethod
    def cls_id():
        return '34dae34f-dbe2-409c-8f85-ddbb46138011'

    @classmethod
    def from_dict(cls, definition: dict) -> 'SdcWorkspaceFactory':
        return SdcWorkspaceFactory()


class ExcelOrMdbWorkspaceFactory(WorkspaceFactory):
    """
    ExcelOrMdbWorkspaceFactory
    """

    @staticmethod
    def cls_id():
        return '30f6f271-852b-4ee8-bd2d-099f51d6b238'

    @classmethod
    def from_dict(cls, definition: dict) -> 'ExcelOrMdbWorkspaceFactory':
        return ExcelOrMdbWorkspaceFactory()


class GpkgWorkspaceFactory(WorkspaceFactory):
    """
    GpkgWorkspaceFactory
    """

    @staticmethod
    def cls_id():
        return '5297187b-fd2b-4a5f-8991-eb3f6f1ca502'

    @classmethod
    def from_dict(cls, definition: dict) -> 'GpkgWorkspaceFactory':
        return GpkgWorkspaceFactory()


class FMEWorkspaceFactory(WorkspaceFactory):
    """
    FMEWorkspaceFactory
    """

    @staticmethod
    def cls_id():
        return 'cb59701c-1c24-4291-aff2-3a8d80923902'

    @classmethod
    def from_dict(cls, definition: dict) -> 'FMEWorkspaceFactory':
        return FMEWorkspaceFactory()


class StreetMapWorkspaceFactory(WorkspaceFactory):
    """
    StreetMapWorkspaceFactory
    """

    @staticmethod
    def cls_id():
        return 'ae2469e8-e110-4cd6-b3f4-a756cbf921ca'

    @classmethod
    def from_dict(cls, definition: dict) -> 'StreetMapWorkspaceFactory':
        return StreetMapWorkspaceFactory()


class LasDatasetWorkspaceFactory(WorkspaceFactory):
    """
    LasDatasetWorkspaceFactory
    """

    @staticmethod
    def cls_id():
        return '7ab01d9a-fdfe-4dfb-9209-86603ee9aec6'

    @classmethod
    def from_dict(cls, definition: dict) -> 'LasDatasetWorkspaceFactory':
        return LasDatasetWorkspaceFactory()


class NetCDFWorkspaceFactory(WorkspaceFactory):
    """
    NetCDFWorkspaceFactory
    """

    @staticmethod
    def cls_id():
        return 'df61a9e1-b8e2-498f-bde5-98de42e801f9'

    @classmethod
    def from_dict(cls, definition: dict) -> 'NetCDFWorkspaceFactory':
        return NetCDFWorkspaceFactory()


class ToolboxWorkspaceFactory(WorkspaceFactory):
    """
    ToolboxWorkspaceFactory
    """

    @staticmethod
    def cls_id():
        return 'e9231b31-2a34-4729-8de2-12cf39674b1b'

    @classmethod
    def from_dict(cls, definition: dict) -> 'ToolboxWorkspaceFactory':
        return ToolboxWorkspaceFactory()


class S57WorkspaceFactory(WorkspaceFactory):
    """
    S57WorkspaceFactory
    """

    @staticmethod
    def cls_id():
        return 'cc1a41b4-17ce-4ec1-92e3-acbd91bf7b30'

    @classmethod
    def from_dict(cls, definition: dict) -> 'S57WorkspaceFactory':
        return S57WorkspaceFactory()
