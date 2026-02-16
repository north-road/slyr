"""
SLYR QGIS Processing provider
"""

# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/

from qgis.core import QgsProcessingProvider, Qgis

from .algorithms import (
    StyleToQgisXml,
    StyleToGpl,
    StylxToGpl,
    GplToStylx,
    StylxToQgisXml,
    XmlToStylx,
    LyrToQlr,
    LyrxToQlr,
    LyrxToQml,
    StyleFromLyr,
    LyrToQml,
    LyrToStyleXml,
    ConvertMxdToQgs,
    ConvertMxdAndData,
    AddLayersFromMxd,
    ConvertPmfToQgs,
    ConvertSxdToQgs,
    ExportStructureToJson,
    AvlToQml,
    ConvertAnnotations,
    ConvertAnnotationClassToGeopackage,
    ConvertProjectData,
    ExtractHyperlinksToTables,
    ExtractSDEConnectionDetails,
    LayerToLyrx,
    ConvertMapxToQgs,
    ConvertQgsToMapx,
    ConvertAprxToQgs,
    GdbToGpkg,
    LyrxToSld,
    LyrToSld,
    ConvertQgsToAprx,
    ConvertAprxAndData,
    QmlToStylex,
    ConvertQptToPagx,
    ConvertQlrToLyrx,
    MxdToSld,
    StylxToSld,
    LpkToQlr,
    LpkxToQlr,
)
from .algorithms.pagx_to_qgs import ConvertPagxToQgs
from .gui_utils import GuiUtils


class SlyrProvider(QgsProcessingProvider):
    """
    SLYR QGIS Processing provider
    """

    def __init__(self):  # pylint: disable=useless-super-delegation
        QgsProcessingProvider.__init__(self)

    def loadAlgorithms(self):  # pylint: disable=missing-docstring
        for alg in [
            StyleToQgisXml,
            StyleToGpl,
            StylxToGpl,
            GplToStylx,
            StylxToQgisXml,
            XmlToStylx,
            LyrToQlr,
            LyrxToQlr,
            LyrxToQml,
            StyleFromLyr,
            LyrToQml,
            LyrToStyleXml,
            ConvertMxdToQgs,
            ConvertMapxToQgs,
            ConvertQgsToMapx,
            AddLayersFromMxd,
            ConvertPmfToQgs,
            ConvertSxdToQgs,
            ExportStructureToJson,
            ConvertPagxToQgs,
            AvlToQml,
            ExtractHyperlinksToTables,
            ExtractSDEConnectionDetails,
            LayerToLyrx,
            ConvertAprxToQgs,
            LyrxToSld,
            LyrToSld,
            ConvertQgsToAprx,
            ConvertAprxAndData,
            QmlToStylex,
            ConvertQptToPagx,
            ConvertQlrToLyrx,
            MxdToSld,
            ConvertMxdAndData,
            ConvertProjectData,
            ConvertAnnotations,
            ConvertAnnotationClassToGeopackage,
            StylxToSld,
            LpkToQlr,
            LpkxToQlr,
        ]:
            self.addAlgorithm(alg())

        if Qgis.QGIS_VERSION_INT >= 32800:
            self.addAlgorithm(GdbToGpkg())

    def id(self):  # pylint: disable=missing-docstring
        return "slyr"

    def name(self):  # pylint: disable=missing-docstring
        return "SLYR (community edition)"

    def longName(self):  # pylint: disable=missing-docstring
        return "Converts ESRI Style and LYR files"

    def icon(self):  # pylint: disable=missing-docstring
        return GuiUtils.get_icon("icon.svg")

    def versionInfo(self):
        # pylint: disable=missing-docstring
        return "6.0.0"
