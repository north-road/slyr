# -*- coding: utf-8 -*-

# /***************************************************************************
# context.py
# ----------
# Date                 : September 2019
# copyright            : (C) 2019 by Nyall Dawson, North Road Consulting
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
Converts .style databases to GPL color palette files
"""

import os
from io import BytesIO

from qgis.core import (
    QgsProcessingParameterFile,
    QgsProcessingParameterFileDestination,
    QgsProcessingOutputNumber,
    QgsProcessingException,
)

from ...bintools.extractor import Extractor, MissingBinaryException
from ...converters.color import ColorConverter
from ...parser.exceptions import InvalidColorException
from ...parser.stream import Stream
from .algorithm import SlyrAlgorithm


class StyleToGpl(SlyrAlgorithm):
    """
    Converts .style databases to GPL color palette files
    """

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    COLOR_COUNT = "COLOR_COUNT"
    UNREADABLE_COLOR_COUNT = "UNREADABLE_COLOR_COUNT"

    # pylint: disable=missing-docstring,unused-argument

    def createInstance(self):
        return StyleToGpl()

    def name(self):
        return "styletogpl"

    def displayName(self):
        return "Convert ESRI style to GPL color palette"

    def shortDescription(self):
        return "Converts ESRI style database to a GPL format color palette file."

    def group(self):
        return "Style databases"

    def groupId(self):
        return "style"

    def shortHelpString(self):
        return (
            "Converts ESRI style database to a GPL format color palette file, extracting all color entities "
            "saved in the style."
        )

    def canExecute(self):
        res, error = super().canExecute()
        if not res:
            return False, error

        if not Extractor.is_mdb_tools_binary_available():
            return (
                False,
                'The MDB tools "mdb-export" utility is required to convert .style databases. Please setup a path to the MDB tools utility in the Settings - Options dialog, under the SLYR tab.',
            )

        return True, None

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(self.INPUT, "Style database", extension="style")
        )

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT, "Destination GPL file", fileFilter="GPL files (*.gpl)"
            )
        )

        self.addOutput(QgsProcessingOutputNumber(self.COLOR_COUNT, "Color Count"))
        self.addOutput(
            QgsProcessingOutputNumber(
                self.UNREADABLE_COLOR_COUNT, "Unreadable Color Count"
            )
        )

    def processAlgorithm(
        self,  # pylint: disable=too-many-locals,too-many-statements
        parameters,
        context,
        feedback,
    ):
        input_file = self.parameterAsString(parameters, self.INPUT, context)
        output_file = self.parameterAsFileOutput(parameters, self.OUTPUT, context)

        results = {}
        colors = []

        _, file_name = os.path.split(input_file)
        file_name, _ = os.path.splitext(file_name)

        feedback.pushInfo("Importing colors from {}".format(input_file))

        try:
            raw_colors = Extractor.extract_styles(input_file, Extractor.COLORS)
        except MissingBinaryException:
            raise QgsProcessingException(  # pylint: disable=raise-missing-from
                'The MDB tools "mdb-export" utility is required to convert .style databases. Please setup a path to the MDB tools utility in the SLYR options panel.'
            )

        feedback.pushInfo("Found {} colors".format(len(raw_colors)))

        unreadable = 0
        for index, raw_color in enumerate(raw_colors):
            feedback.setProgress(index / len(raw_colors) * 100)
            if feedback.isCanceled():
                break

            name = raw_color[Extractor.NAME]
            feedback.pushInfo("{}/{}: {}".format(index + 1, len(raw_colors), name))

            handle = BytesIO(raw_color[Extractor.BLOB])
            stream = Stream(handle)
            try:
                color = stream.read_object()
            except InvalidColorException:
                feedback.reportError("Error reading color {}".format(name), False)
                unreadable += 1
                continue

            qcolor = ColorConverter.color_to_qcolor(color)
            colors.append((name, qcolor))

        results[self.COLOR_COUNT] = len(raw_colors)
        results[self.UNREADABLE_COLOR_COUNT] = unreadable

        with open(output_file, "wt", encoding="utf8") as f:
            f.write("GIMP Palette\n")
            f.write("Name: {}\n".format(file_name))
            f.write("Columns: 4\n")
            f.write("#\n")
            for c in colors:
                f.write(
                    "{} {} {} {}\n".format(c[1].red(), c[1].green(), c[1].blue(), c[0])
                )

        results[self.OUTPUT] = output_file
        return results

    # pylint: enable=missing-docstring,unused-argument
