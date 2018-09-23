#!/usr/bin/env python
"""
SLYR Exceptions
"""


class UnsupportedVersionException(Exception):
    """
    Thrown when an object of an unsupported version is encountered
    """
    pass


class UnreadableSymbolException(Exception):
    """
    Thrown when a symbol could not be read, for whatever reason
    """
    pass


class NotImplementedException(Exception):
    """
    Thrown when attempting to read/convert an object, which is known
    but not yet implemented
    """
    pass


class UnknownGuidException(Exception):
    """
    Thrown on encountering an unknown GUID
    """
    pass


class InvalidColorException(Exception):
    """
    Thrown when an error was encountered while converting a color
    """
    pass
