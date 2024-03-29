#!/usr/bin/env python
"""
Unit
"""

from typing import Optional


class Units:
    """
    Unit values
    """

    DISTANCE_UNKNOWN = 0
    DISTANCE_INCHES = 1
    DISTANCE_POINTS = 2
    DISTANCE_FEET = 3
    DISTANCE_YARDS = 4
    DISTANCE_MILES = 5
    DISTANCE_NAUTICAL_MILES = 6
    DISTANCE_MILLIMETERS = 7
    DISTANCE_CENTIMETERS = 8
    DISTANCE_METERS = 9
    DISTANCE_KILOMETERS = 10
    DISTANCE_DECIMAL_DEGREES = 11
    DISTANCE_DECIMETERS = 12

    TIME_UNITS_UNKNOWN = 0
    TIME_UNITS_MILLISECONDS = 1
    TIME_UNITS_SECONDS = 2
    TIME_UNITS_MINUTES = 3
    TIME_UNITS_HOURS = 4
    TIME_UNITS_DAYS = 5
    TIME_UNITS_WEEKS = 6
    TIME_UNITS_MONTHS = 7
    TIME_UNITS_YEARS = 8
    TIME_UNITS_DECADES = 9
    TIME_UNITS_CENTURIES = 10

    UNIT_TO_STRING_MAP = {
        DISTANCE_UNKNOWN: 'unknown',
        DISTANCE_INCHES: 'inches',
        DISTANCE_POINTS: 'points',
        DISTANCE_FEET: 'feet',
        DISTANCE_YARDS: 'yards',
        DISTANCE_MILES: 'miles',
        DISTANCE_NAUTICAL_MILES: 'nautical_miles',
        DISTANCE_MILLIMETERS: 'millimeters',
        DISTANCE_CENTIMETERS: 'centimeters',
        DISTANCE_METERS: 'meters',
        DISTANCE_KILOMETERS: 'kilometers',
        DISTANCE_DECIMAL_DEGREES: 'decimal_degrees',
        DISTANCE_DECIMETERS: 'decimeters',
    }

    @staticmethod
    def distance_unit_to_string(unit) -> Optional[str]:
        """
        Converts a distance unit to a string representation
        """
        return Units.UNIT_TO_STRING_MAP.get(unit, None)

    @staticmethod
    def string_to_distance_unit(unit: str):
        """
        Converts a string to a distance unit
        """
        return [k for k, v in Units.UNIT_TO_STRING_MAP.items() if v == unit][0]

    @staticmethod
    def time_unit_to_string(unit) -> Optional[str]:
        """
        Converts a time unit to a string representation
        """
        unit_map = {
            Units.TIME_UNITS_UNKNOWN: 'unknown',
            Units.TIME_UNITS_MILLISECONDS: 'milliseconds',
            Units.TIME_UNITS_SECONDS: 'seconds',
            Units.TIME_UNITS_MINUTES: 'minutes',
            Units.TIME_UNITS_HOURS: 'hours',
            Units.TIME_UNITS_DAYS: 'days',
            Units.TIME_UNITS_WEEKS: 'weeks',
            Units.TIME_UNITS_MONTHS: 'months',
            Units.TIME_UNITS_YEARS: 'years',
            Units.TIME_UNITS_DECADES: 'decades',
            Units.TIME_UNITS_CENTURIES: 'centuries',
        }
        return unit_map.get(unit, None)
