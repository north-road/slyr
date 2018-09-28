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

        print(' '.join(export_args))

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

            def remove_quote(val):
                """
                Removes the custom quotation character from start/end of values
                """
                if val[:len(Extractor.__QUOTE)] == Extractor.__QUOTE:
                    val = val[len(Extractor.__QUOTE):]
                if val[-len(Extractor.__QUOTE):] == Extractor.__QUOTE:
                    val = val[:-len(Extractor.__QUOTE)]
                return val

            def extract_text(val):
                """
                Extracts a text component from a binary part
                :param val: binary field value
                :return: str value
                """
                val = remove_quote(val)
                val = val.decode('UTF-8')
                return val

            # need to strip __QUOTE from blob too
            blob = remove_quote(blob)

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
