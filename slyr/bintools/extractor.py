#!/usr/bin/env python

"""
Dumps the contents of an ESRI .style file to a set of binary blobs
"""

import subprocess


class Extractor:
    """
    Extracts style information and blobs from .style databases
    """

    __NEWLINE = b'\nnewline\n'
    __DELIMITER = b',,,,,,,'

    FILL_SYMBOLS = 'Fill symbols'
    LINE_SYMBOLS = 'Line symbols'
    MARKER_SYMBOLS = 'Marker symbols'

    NAME = 'NAME'
    TAGS = 'TAGS'
    CATEGORY = 'CATEGORY'
    ID = 'ID'
    BLOB = 'BLOB'

    @staticmethod
    def extract_styles(file_path: str, symbol_type: str):
        """
        Extracts all matching styles of a given symbol type from a .style file
        :param file_path: path to .style file
        :param symbol_type: symbol type to extract, e.g. Extractor.FILL_SYMBOLS
        :return: list of raw symbols, ready for parsing
        """
        export_args = ['mdb-export',
                       '-H',
                       '-R {}'.format(Extractor.__NEWLINE.decode('UTF-8')),
                       '-d {}'.format(Extractor.__DELIMITER.decode('UTF-8')),
                       '-b',
                       'raw',
                       file_path,
                       symbol_type]
        result = subprocess.run(export_args, stdout=subprocess.PIPE)

        raw_symbols = []
        for r in result.stdout.split(Extractor.__NEWLINE):
            if not r:
                continue

            symbol_id, name, category, blob, tags = r.split(Extractor.__DELIMITER)

            def extract_text(val):
                """
                Extracts a text component from a binary part
                :param val: binary field value
                :return: str value
                """
                val = val.decode('UTF-8')
                if val.startswith('"'):
                    val = val[1:-2]
                return val.strip()

            # need to strip " " from blob
            if blob[0] == 0x22:
                blob = blob[1:]
                while not blob[-1] != 0x22:
                    blob = blob[:-1]
                blob = blob[:-2]

            # also need to convert "" -> "
            blob=blob.replace(b'""',b'"')

            symbol = {
                Extractor.NAME: extract_text(name),
                Extractor.CATEGORY: extract_text(category),
                Extractor.TAGS: extract_text(tags),
                Extractor.ID: extract_text(symbol_id),
                Extractor.BLOB: blob
            }
            raw_symbols.append(symbol)

        return raw_symbols
