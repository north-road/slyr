#!/usr/bin/env python
"""
Base class for persistent objects
"""

import functools
from typing import List, Optional
from slyr_community.parser.exceptions import NotImplementedException, PartiallyImplementedException


class Object:
    """
    Base class for objects which can be read from a stream
    """

    def __init__(self):
        def to_dict_(func):
            """
            Adds common attributes to the to_dict function
            """

            @functools.wraps(func)
            def wrapper(*args, **kwargs):  # pylint: disable=unused-argument
                """
                Wrapper which adds common attributes to the to_dict call
                """
                d = func()
                if d is not None:
                    d['type'] = self.__class__.__name__
                    d['version'] = self.version
                return d

            return wrapper

        self.to_dict = to_dict_(self.to_dict)
        self.version = None

    @staticmethod
    def cls_id():
        """
        Returns the object's class id
        """
        return None

    @staticmethod
    def compatible_versions():
        """
        Returns the list of compatible object versions, or None to skip
        ESRI version bytes
        """
        return [1]

    @staticmethod
    def supports_references():
        """
        Returns true if the object supports reference counting
        """
        return True

    def read(self, stream, version):
        """
        Reads the object from the given stream
        """

    def children(self) -> List['Object']:
        """
        Returns a list of all child objects referenced by this object
        """
        return []

    def to_dict(self) -> Optional[dict]:  # pylint: disable=method-hidden
        """
        Converts the object to a dictionary
        """
        raise NotImplementedException('{} objects are not yet supported'.format(self.__class__.__name__))


def not_implemented(cls):
    """
    Decorator which raises a NotImplementedException on object read
    """

    def not_implemented_(func, cls):
        """
        Raises a NotImplementedException on call
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # pylint: disable=unused-argument
            """
            Wrapper which raises a NotImplementedException on function call
            """
            raise NotImplementedException('{} objects are not yet supported'.format(cls.__name__))

        return wrapper

    cls.read = not_implemented_(cls.read, cls)
    cls.compatible_versions = not_implemented_(cls.compatible_versions, cls)
    return cls

def partially_implemented(cls):
    """
    Decorator which raises a PartiallyImplementedException on object read
    """

    def partially_implemented_(func, cls):
        """
        Raises a PartiallyImplementedException on call
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # pylint: disable=unused-argument
            """
            Wrapper which raises a PartiallyImplementedException on function call
            """
            raise PartiallyImplementedException('{} objects are not fully supported'.format(cls.__name__))

        return wrapper

    cls.compatible_versions = partially_implemented_(cls.compatible_versions, cls)
    return cls