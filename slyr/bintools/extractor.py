#!/usr/bin/env python

"""
Dumps the contents of an ESRI .style file to a set of binary blobs
"""

import os
import subprocess


class Extractor:
    """
    Extracts style information and blobs from .style databases
    """

    __NEWLINE = b'!!newline!!'
    __DELIMITER = b',,,,,,,'

    COLORS = 'Colors'
    FILL_SYMBOLS = 'Fill symbols'
    LINE_SYMBOLS = 'Line symbols'
    MARKER_SYMBOLS = 'Marker symbols'
    COLOR_RAMPS = 'Color ramps'

    NAME = 'NAME'
    TAGS = 'TAGS'
    CATEGORY = 'CATEGORY'
    ID = 'ID'
    BLOB = 'BLOB'

    @staticmethod
    def extract_styles(file_path: str, symbol_type: str, mdbtools_path=None):  # pylint: disable=too-many-locals
        """
        Extracts all matching styles of a given symbol type from a .style file
        :param file_path: path to .style file
        :param symbol_type: symbol type to extract, e.g. Extractor.FILL_SYMBOLS
        :return: list of raw symbols, ready for parsing
        """

        binary = 'mdb-export'
        if mdbtools_path is not None:
            binary = os.path.join(mdbtools_path, binary)

        export_args = [binary,
                       '-H',
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
            result = subprocess.run(export_args, stdout=subprocess.PIPE, creationflags=CREATE_NO_WINDOW)
        except ValueError:
            result = subprocess.run(export_args, stdout=subprocess.PIPE)

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

            def extract_text(val):
                """
                Extracts a text component from a binary part
                :param val: binary field value
                :return: str value
                """
                val = val.decode('UTF-8')
                if val.startswith('"'):
                    val = val[1:]
                    if val.endswith('"'):
                        val = val[:-1]
                return val.strip()

            # need to strip " " from blob
            if blob[0] == 0x22:
                blob = blob[1:]
                while not blob[-1] != 0x22:
                    blob = blob[:-1]
                blob = blob[:-1]

            # also need to convert "" -> "
            blob = blob.replace(b'""', b'"')

            # on windows, mdbtools does a weird thing and replaces all 0a bytes with 0a0d. Wonderful wonderful
            # Windows new endings come round to bite us again
            blob = blob.replace(b'\r\n', b'\n')

            symbol = {
                Extractor.NAME: extract_text(name),
                Extractor.CATEGORY: extract_text(category),
                Extractor.TAGS: extract_text(tags) if tags else '',
                Extractor.ID: extract_text(symbol_id),
                Extractor.BLOB: blob
            }
            raw_symbols.append(symbol)

        return raw_symbols
