"""
ArcObjects enums
"""

from enum import Enum


class DMSGridLabelType(Enum):
    """
    DMS grid label types
    """

    Standard = 0
    MinutesStackedOverSeconds = 1
    DecimalDegrees = 2
    DecimalMinutes = 3
    DecimalSeconds = 4
