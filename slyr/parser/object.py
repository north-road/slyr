#!/usr/bin/env python
"""
Base class for persistent objects
"""


class Object:
    """
    Base class for objects which can be read from a stream
    """

    @staticmethod
    def guid() -> str:
        """
        Returns the object's GUID
        """
        return ''

    @staticmethod
    def compatible_versions():
        """
        Returns the list of compatible object versions
        """
        return [1]

    def read(self, stream, version):
        """
        Reads the object from the given stream
        """
        pass
