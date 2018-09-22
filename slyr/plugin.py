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
QGIS Plugin interface to SLYR conversions
"""

from qgis.core import QgsApplication
from slyr.qgis_plugin.provider import SlyrProvider
from slyr.parser.initalize_registry import initialize_registry

initialize_registry()


class SlyrPlugin:
    """
    SLYR *air guitar* SCREEEEEAAAAAMMM
    """

    def __init__(self, iface):
        """init"""
        self.iface = iface
        self.provider = SlyrProvider()

    def initGui(self):
        """startup"""
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        """teardown"""
        QgsApplication.processingRegistry().removeProvider(self.provider)
