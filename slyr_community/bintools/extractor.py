#!/usr/bin/env python

# /***************************************************************************
# extractor.py
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
Dumps the contents of an ESRI .style file to a set of binary blobs
"""

import os
import subprocess
import sys
from ctypes import cdll
from PyQt5.QtCore import QSettings


class MissingBinaryException(Exception):
    """
    Thrown when a binary utility is not available
    """


class Extractor:
    """
    Extracts style information and blobs from .style databases
    """

    # something to keep in mind... mdb-export is somewhat... fragile
    # and tends to apply text formatting options and escaping within
    # binary blobs too. So we overwrite all the default newline, delimiter,
    # and quotation characters with strings which are almost guaranteed
    # to never come up in an ESRI style blob ;)
    __NEWLINE = b'arcgissuxxxxxxxxxx'
    __DELIMITER = b'reallynooneneedstopayourexorbitantlicensingfeesjustembracethefossinstead'
    __QUOTE = b'qgisisthebestweallknowthat'

    COLORS = 'Colors'
    FILL_SYMBOLS = 'Fill symbols'
    LINE_SYMBOLS = 'Line symbols'
    MARKER_SYMBOLS = 'Marker symbols'
    COLOR_RAMPS = 'Color ramps'
    LABELS = 'Labels'
    MAPLEX_LABELS = 'Maplex Labels'
    AREA_PATCHES = 'Area Patches'
    LINE_PATCHES = 'Line Patches'
    SCALE_BARS = 'Scale Bars'
    LEGEND_ITEMS = 'Legend Items'
    SCALE_TEXTS = 'Scale Texts'
    BORDERS = 'Borders'
    BACKGROUNDS = 'Backgrounds'
    TEXT_SYMBOLS = 'Text Symbols'
    NORTH_ARROWS = 'North Arrows'
    SHADOWS = 'Shadows'

    NAME = 'NAME'
    TAGS = 'TAGS'
    CATEGORY = 'CATEGORY'
    ID = 'ID'
    BLOB = 'BLOB'

    MDB_EXPORT_BINARY = 'mdb-export'

    @staticmethod
    def is_windows() -> bool:
        """
        Returns True if the plugin is running on Windows
        """
        return os.name == 'nt'

    @staticmethod
    def get_process_startup_info():
        """
        Returns the correct startup info to use when calling commands for different platforms
        """
        # For MS-Windows, we need to hide the console window.
        si = None
        if Extractor.is_windows():
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
        return si

    @staticmethod
    def get_windows_code_page():
        """
        Determines MS-Windows CMD.exe shell codepage.
        Used into GRASS exec script under MS-Windows.
        """
        return str(cdll.kernel32.GetACP())

    @staticmethod
    def get_process_keywords():
        """
        Returns the correct process keywords dict to use when calling commands for different platforms
        """
        kw = {}
        if Extractor.is_windows():
            kw['startupinfo'] = Extractor.get_process_startup_info()
            if sys.version_info >= (3, 6):
                kw['encoding'] = "cp{}".format(Extractor.get_windows_code_page())
        return kw

    @staticmethod
    def get_mdb_tools_binary_path(executable: str) -> str:
        """
        Calculates the path for a MDB tools binary
        :param executable: mdb tools executable name
        :return: path for executable
        """
        mdbtools_path = QSettings().value('/plugins/slyr/mdbtools_path')
        if mdbtools_path:
            return os.path.join(mdbtools_path, executable)
        elif Extractor.is_windows():
            return os.path.join(os.path.dirname(__file__), 'bin', executable)
        return executable

    @staticmethod
    def is_mdb_tools_binary_available() -> bool:
        """
        Returns True if the MDB tools binary is available for execution
        :return: True if binary is available
        """

        command = [Extractor.get_mdb_tools_binary_path(Extractor.MDB_EXPORT_BINARY)]
        try:
            with subprocess.Popen(command,
                                  stdout=subprocess.PIPE,
                                  stdin=subprocess.DEVNULL,
                                  stderr=subprocess.STDOUT,
                                  universal_newlines=True,
                                  **Extractor.get_process_keywords()) as proc:
                for line in proc.stdout:
                    if 'row-delimiter' in line:
                        return True
        except FileNotFoundError:
            pass

        return False

    @staticmethod
    def _remove_quote(val):
        """
        Removes the custom quotation character from start/end of values
        """
        if val[:len(Extractor.__QUOTE)] == Extractor.__QUOTE:
            val = val[len(Extractor.__QUOTE):]
        if val[-len(Extractor.__QUOTE):] == Extractor.__QUOTE:
            val = val[:-len(Extractor.__QUOTE)]
        return val

    @staticmethod
    def _extract_text(val):
        """
        Extracts a text component from a binary part
        :param val: binary field value
        :return: str value
        """
        val = Extractor._remove_quote(val)
        try:
            val = val.decode('UTF-8')
        except UnicodeDecodeError:
            val = val.decode('latin-1')
        return val

    @staticmethod
    def _format_value(val):
        """
        Tries to convert a string value to a nicer type
        """
        val = Extractor._extract_text(val)
        if val == '':
            return None

        try:
            res = float(val)
            if int(res) == res:
                return int(res)
            return res
        except ValueError:
            pass

        return val

    @staticmethod
    def extract_styles(file_path: str, symbol_type: str):  # pylint: disable=too-many-locals
        """
        Extracts all matching styles of a given symbol type from a .style file
        :param file_path: path to .style file
        :param symbol_type: symbol type to extract, e.g. Extractor.FILL_SYMBOLS
        :return: list of raw symbols, ready for parsing
        """
        binary = Extractor.get_mdb_tools_binary_path(Extractor.MDB_EXPORT_BINARY)

        export_args = [binary,
                       '-H',
                       '-q',
                       '{}'.format(Extractor.__QUOTE.decode('ASCII')),
                       '-R',
                       '{}'.format(Extractor.__NEWLINE.decode('ASCII')),
                       '-d',
                       '{}'.format(Extractor.__DELIMITER.decode('ASCII')),
                       '-b',
                       'raw',
                       file_path,
                       symbol_type]

        CREATE_NO_WINDOW = 0x08000000
        try:
            result = subprocess.run(export_args, stdout=subprocess.PIPE,  # pylint: disable=subprocess-run-check
                                    creationflags=CREATE_NO_WINDOW)
        except ValueError:
            try:
                result = subprocess.run(export_args, stdout=subprocess.PIPE)  # pylint: disable=subprocess-run-check
            except FileNotFoundError as e:
                raise MissingBinaryException from e
        except FileNotFoundError as e:
            raise MissingBinaryException from e

        raw_symbols = []
        for r in result.stdout.split(Extractor.__NEWLINE):
            if not r:
                continue

            res = r.split(Extractor.__DELIMITER)
            if len(res) == 5:
                symbol_id, name, category, blob, tags = res
            elif len(res) == 4:
                symbol_id, name, category, blob = res
                tags = None
            else:
                assert False, 'Error reading style table'

            # need to strip __QUOTE from blob too
            blob = Extractor._remove_quote(blob)

            if Extractor.is_windows():
                # on windows, mdbtools does a weird thing and replaces all 0a bytes with 0a0d. Wonderful wonderful
                # Windows new endings come round to bite us again
                blob = blob.replace(b'\r\n', b'\n')

            symbol = {
                Extractor.NAME: Extractor._extract_text(name),
                Extractor.CATEGORY: Extractor._extract_text(category),
                Extractor.TAGS: Extractor._extract_text(tags) if tags else '',
                Extractor.ID: Extractor._extract_text(symbol_id),
                Extractor.BLOB: blob
            }
            raw_symbols.append(symbol)

        return raw_symbols
