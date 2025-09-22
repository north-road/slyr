"""
MXD Browser widget

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

import os
from qgis.PyQt.uic import loadUiType
from qgis.core import QgsApplication
from ...parser.streams.map_document import MapDocument
from ...parser.exceptions import (
    UnreadableSymbolException,
    UnsupportedVersionException,
    NotImplementedException,
    UnknownClsidException,
    EmptyDocumentException,
    DocumentTypeException,
    RequiresLicenseException,
)

path = os.path.dirname(os.path.abspath(__file__))
ui, base = loadUiType(os.path.join(path, "..", "ui", "itempropertiesbase.ui"))


class MxdBrowserWidget(base, ui):
    def __init__(self, path, parent=None):
        super().__init__(parent)

        self.setupUi(self)

        self.metadata_text_browser.setOpenLinks(False)
        self.path = path

        style = QgsApplication.reportStyleSheet()
        self.metadata_text_browser.document().setDefaultStyleSheet(style)
        self.metadata_text_browser.setHtml(self.createMetadata())

    def createMetadata(self):
        metadata = "<html>\n<body>\n"
        metadata += "<h1>" + "Document Metadata" + "</h1>\n<hr>\n"

        with open(self.path, "rb") as f:
            try:
                obj = MapDocument(f, False, tolerant=True, metadata_only=True)

                metadata += (
                    '<tr><td class="highlight">'
                    + "Title"
                    + "</td><td>"
                    + obj.title
                    + "</td></tr>\n"
                )
                metadata += (
                    '<tr><td class="highlight">'
                    + "Author"
                    + "</td><td>"
                    + obj.author
                    + "</td></tr>\n"
                )
                metadata += (
                    '<tr><td class="highlight">'
                    + "Description"
                    + "</td><td>"
                    + obj.description
                    + "</td></tr>\n"
                )
                metadata += (
                    '<tr><td class="highlight">'
                    + "Summary"
                    + "</td><td>"
                    + obj.summary
                    + "</td></tr>\n"
                )
                metadata += (
                    '<tr><td class="highlight">'
                    + "Tags"
                    + "</td><td>"
                    + obj.tags
                    + "</td></tr>\n"
                )
                metadata += (
                    '<tr><td class="highlight">'
                    + "Credits"
                    + "</td><td>"
                    + obj.credits
                    + "</td></tr>\n"
                )
                metadata += (
                    '<tr><td class="highlight">'
                    + "Original path"
                    + "</td><td>"
                    + obj.original_path
                    + "</td></tr>\n"
                )
                if obj.last_saved:
                    metadata += (
                        '<tr><td class="highlight">'
                        + "Last saved"
                        + "</td><td>"
                        + obj.last_saved
                        + "</td></tr>\n"
                    )
                if obj.last_printed:
                    metadata += (
                        '<tr><td class="highlight">'
                        + "Last printed"
                        + "</td><td>"
                        + obj.last_printed
                        + "</td></tr>\n"
                    )
                if obj.last_exported:
                    metadata += (
                        '<tr><td class="highlight">'
                        + "Last exported"
                        + "</td><td>"
                        + obj.last_exported
                        + "</td></tr>\n"
                    )

                return metadata

            except EmptyDocumentException:
                pass
            except DocumentTypeException:
                return "File is corrupt or not an MXD document"
            except NotImplementedException as e:
                return "Cannot read MXD document: {}".format(e)
            except UnreadableSymbolException as e:
                return "Cannot read MXD document: {}".format(e)
            except UnsupportedVersionException as e:
                return "Cannot read MXD document: {}".format(e)
            except AssertionError:
                return "Cannot read MXD document"
            except KeyError:
                return "Cannot read MXD document"
            except IndexError:
                return "Cannot read MXD document"
            except RequiresLicenseException as e:
                return (
                    "{}. Please see https://north-road.com/slyr/ for details.".format(e)
                )
            except UnknownClsidException:
                pass

        return "File is empty or corrupt"
