#!/usr/bin/env python
"""
SLYR Exceptions
"""


class UnsupportedVersionException(Exception):
    """
    Thrown when an object of an unsupported version is encountered
    """


class UnreadableSymbolException(Exception):
    """
    Thrown when a symbol could not be read, for whatever reason
    """


class NotImplementedException(Exception):
    """
    Thrown when attempting to read/convert an object, which is known
    but not yet implemented
    """

    def __init__(self, message, original_object=None):
        super(Exception, self).__init__(message)  # pylint: disable=bad-super-call
        self.original_object = original_object


class PartiallyImplementedException(Exception):
    """
    Thrown when attempting to read/convert an object, which is known
    but only partially implemented, and if we know the size of the object
    from other means we should always use that instead
    """


class UnknownClsidException(Exception):
    """
    Thrown on encountering an unknown CLSID
    """


class UnknownObjectTypeException(Exception):
    """
    Thrown on encountering an unknown CIM object type
    """


class CustomExtensionClsidException(Exception):
    """
    Thrown on encountering an known custom extension CLSID
    """

    def __init__(self, message, custom_object=None, clsid=None):
        super(Exception, self).__init__(message)  # pylint: disable=bad-super-call
        self.custom_object = custom_object
        self.clsid = clsid


class InvalidColorException(Exception):
    """
    Thrown when an error was encountered while converting a color
    """


class UnreadablePictureException(Exception):
    """
    Thrown on encountering an unreadable picture
    """


class EmptyDocumentException(Exception):
    """
    Thrown on encountering an empty document
    """


class DocumentTypeException(Exception):
    """
    Thrown on encountering a document of unexpected type
    """


class RequiresLicenseException(Exception):
    """
    Raised when functionality requires a valid license
    """
