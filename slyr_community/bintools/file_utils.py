#!/usr/bin/env python3

# /***************************************************************************
# file_utils.py
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
File utilities
"""

import re


class FileUtils:
    """
    Contains various file utilities
    """

    @staticmethod
    def clean_symbol_name_for_file(symbol_name):
        """nasty little function to remove some characters which will choke"""
        file_name = symbol_name.strip()
        file_name = file_name.replace("/", "_")
        file_name = file_name.replace(">", "_")
        file_name = file_name.replace("<", "_")
        file_name = file_name.replace("\\", "_")
        file_name = file_name.replace("?", "_")
        file_name = file_name.replace("*", "_")
        file_name = file_name.replace('"', "_")
        file_name = file_name.replace("'", "_")
        file_name = file_name.replace(":", "_")
        file_name = file_name.replace(";", "_")
        file_name = file_name.replace(" ", "_")
        file_name = file_name.replace(",", "_")
        file_name = file_name.replace("|", "_")
        file_name = re.sub(r"_+", "_", file_name)
        if file_name.endswith("_"):
            file_name = file_name[:-1]
        if file_name.startswith("_"):
            file_name = file_name[1:]
        if not file_name:
            return "__"
        # limit to 30 chars
        return file_name[:30]
