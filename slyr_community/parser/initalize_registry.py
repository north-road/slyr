#!/usr/bin/env python
"""
Loads all object modules, causing them to be initialized within the registry singleton
"""

from slyr_community.parser.objects import *  # pylint: disable=wildcard-import, unused-wildcard-import


def initialize_registry():
    """
    Registers all known objects with the registry singleton
    """

    def get_all_subclasses(cls):
        all_subclasses = []

        for subclass in cls.__subclasses__():
            all_subclasses.append(subclass)
            all_subclasses.extend(get_all_subclasses(subclass))

        return all_subclasses

    from slyr_community.parser.object import Object
    from slyr_community.parser.object_registry import REGISTRY

    for c in get_all_subclasses(Object):
        REGISTRY.register(c)
