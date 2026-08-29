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
        """Remove characters which are invalid in Windows filenames or may cause issues"""
        file_name = symbol_name.strip()
        # Remove Windows forbidden characters: < > : " / \ | ? *
        file_name = re.sub(r'[<>:"/\\|?*]', "_", file_name)
        # Remove control characters and other problematic chars
        file_name = re.sub(r'[\x00-\x1f\x7f;,\']', "_", file_name)
        # Replace spaces with underscores
        file_name = file_name.replace(" ", "_")
        # Collapse multiple underscores
        file_name = re.sub(r"_+", "_", file_name)
        # Remove leading/trailing underscores
        file_name = file_name.strip("_")
        if not file_name:
            return "__"
        # limit to 30 chars
        return file_name[:30]
