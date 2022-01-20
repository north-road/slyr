# -*- coding: utf-8 -*-

# /***************************************************************************
# browser.py
# ----------
# Date                 : September 2019
# copyright            : (C) 2019 by Nyall Dawson
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
Browser utilities
"""

from qgis.PyQt.QtWidgets import (
    QPushButton)

from qgis.core import (
    Qgis,
    QgsMessageOutput
)
from qgis.utils import iface


class BrowserUtils:
    """
    Browser utilities
    """

    @staticmethod
    def show_warning(short_message, title, long_message, level=Qgis.Warning, message_bar=None):
        """
        Shows a warning via the QGIS message bar
        """

        def show_details(_):
            dialog = QgsMessageOutput.createMessageOutput()
            dialog.setTitle(title)
            dialog.setMessage(long_message, QgsMessageOutput.MessageHtml)
            dialog.showMessage()

        if message_bar is None:
            message_bar = iface.messageBar()
        message_widget = message_bar.createMessage('SLYR', short_message)
        details_button = QPushButton("Details")
        details_button.clicked.connect(show_details)
        message_widget.layout().addWidget(details_button)
        return message_bar.pushWidget(message_widget, level, 0)

    @staticmethod
    def open_settings(message_bar_widget=None):
        """
        Opens the settings dialog at the SLYR options page
        """
        iface.showOptionsDialog(iface.mainWindow(), currentPage='slyrOptions')
        if message_bar_widget:
            iface.messageBar().popWidget(message_bar_widget)
