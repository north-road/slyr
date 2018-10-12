#!/usr/bin/env python3

"""
File utilities
"""


class FileUtils:
    """
    Contains various file utilities
    """

    @staticmethod
    def clean_symbol_name_for_file(symbol_name):
        """nasty little function to remove some characters which will choke"""
        file_name = symbol_name
        file_name = file_name.replace('/', '_')
        file_name = file_name.replace('>', '_')
        file_name = file_name.replace('<', '_')
        file_name = file_name.replace('\\', '_')
        file_name = file_name.replace('?', '_')
        file_name = file_name.replace('*', '_')
        file_name = file_name.replace('"', '_')
        file_name = file_name.replace(':', '_')
        return file_name.strip()
