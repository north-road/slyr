# -*- coding: utf-8 -*-

# /***************************************************************************
# provider.py
# ----------
# Date                 : September 2019
# copyright            : (C) 2019 by Nyall Dawson, SMEC
# email                : nyall.dawson@gmail.com
#
#  ***************************************************************************/
#
# /***************************************************************************
#  *                                                                         *
#  *   This program is free software; you can redistribute it and/or modify  *
#  *   it under the terms of the GNU General Public License as published by  *
#  *   the Free Software Foundation; either version 2 of the License, or     *
#  *   (at your option) any later version.                                   *
#  *                                                                         *
#  ***************************************************************************/


"""
SLYR QGIS Processing provider
"""

from qgis.core import QgsProcessingProvider
from slyr_community.qgis_plugin.algorithms import (
    StyleToQgisXml,
    StyleToGpl,
    LyrToQlr,
    StyleFromLyr,
    LyrToQml,
    LyrToStyleXml,
    ConvertMxdToQgs,
    AddLayersFromMxd,
    ConvertPmfToQgs,
    ConvertSxdToQgs,
    ExportStructureToJson,
    AvlToQml
)
from slyr_community.qgis_plugin.gui_utils import GuiUtils


class SlyrProvider(QgsProcessingProvider):
    """
    SLYR QGIS Processing provider
    """

    def __init__(self):  # pylint: disable=useless-super-delegation
        QgsProcessingProvider.__init__(self)

    def loadAlgorithms(self):  # pylint: disable=missing-docstring
        for alg in [StyleToQgisXml, StyleToGpl, LyrToQlr, StyleFromLyr, LyrToQml, LyrToStyleXml, ConvertMxdToQgs,
                    AddLayersFromMxd, ConvertPmfToQgs, ConvertSxdToQgs, ExportStructureToJson, AvlToQml]:
            self.addAlgorithm(alg())

    def id(self):  # pylint: disable=missing-docstring
        return 'slyr'

    def name(self):  # pylint: disable=missing-docstring
        return 'SLYR (community)'

    def longName(self):  # pylint: disable=missing-docstring
        return 'Converts ESRI Style and LYR files'

    def icon(self):  # pylint: disable=missing-docstring
        return GuiUtils.get_icon('icon.svg')

    def versionInfo(self):
        # pylint: disable=missing-docstring
        return '3.1.0'
