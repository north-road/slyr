#!/usr/bin/env python


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

    def read(self, stream):
        """
        Reads the object from the given stream
        """
        pass
