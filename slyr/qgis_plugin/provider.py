# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (C) 2018 Nyall Dawson, SMEC
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
###############################################################################

"""
SLYR QGIS Processing provider
"""

from qgis.core import QgsProcessingProvider
from processing.core.ProcessingConfig import ProcessingConfig, Setting
from slyr.qgis_plugin.algorithms import StyleToQgisXml


class SlyrProvider(QgsProcessingProvider):
    """
    SLYR QGIS Processing provider
    """

    def __init__(self):
        QgsProcessingProvider.__init__(self)

    def load(self):  # pylint: disable=missing-docstring
        ProcessingConfig.settingIcons[self.name()] = self.icon()
        ProcessingConfig.addSetting(Setting(
            self.name(),
            'MDB_PATH',
            self.tr('Location of mdbtools binaries'),
            '', valuetype=Setting.FOLDER))
        ProcessingConfig.readSettings()
        return super().load()

    def unload(self):  # pylint: disable=missing-docstring
        ProcessingConfig.removeSetting('MDB_PATH')

    def loadAlgorithms(self):  # pylint: disable=missing-docstring
        for alg in [StyleToQgisXml]:
            self.addAlgorithm(alg())

    def id(self):  # pylint: disable=missing-docstring
        return 'slyr'

    def name(self):  # pylint: disable=missing-docstring
        return 'SLYR'

    def longName(self):  # pylint: disable=missing-docstring
        return 'Converts ESRI Style and LYR files'
