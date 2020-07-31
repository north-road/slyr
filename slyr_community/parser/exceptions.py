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


class UnknownClsidException(Exception):
    """
    Thrown on encountering an unknown CLSID
    """
    pass


class CustomExtensionClsidException(Exception):
    """
    Thrown on encountering an known custom extension CLSID
    """

    def __init__(self, message, object=None, clsid=None):
        super(Exception, self).__init__(message)
        self.object = object
        self.clsid = clsid


class InvalidColorException(Exception):
    """
    Thrown when an error was encountered while converting a color
    """
    pass


class UnreadablePictureException(Exception):
    """
    Thrown on encountering an unreadable picture
    """
    pass


class EmptyDocumentException(Exception):
    """
    Thrown on encountering an empty document
    """
    pass


class DocumentTypeException(Exception):
    """
    Thrown on encountering a document of unexpected type
    """
    pass
