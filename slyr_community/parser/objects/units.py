#!/usr/bin/env python
"""
Unit
"""


class Units:
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

    @staticmethod
    def distance_unit_to_string(unit):
        if unit == Units.DISTANCE_UNKNOWN:
            return 'unknown'
        elif unit == Units.DISTANCE_INCHES:
            return 'inches'
        elif unit == Units.DISTANCE_POINTS:
            return 'points'
        elif unit == Units.DISTANCE_FEET:
            return 'feet'
        elif unit == Units.DISTANCE_YARDS:
            return 'yards'
        elif unit == Units.DISTANCE_MILES:
            return 'miles'
        elif unit == Units.DISTANCE_NAUTICAL_MILES:
            return 'nautical_miles'
        elif unit == Units.DISTANCE_MILLIMETERS:
            return 'millimeters'
        elif unit == Units.DISTANCE_CENTIMETERS:
            return 'centimeters'
        elif unit == Units.DISTANCE_METERS:
            return 'meters'
        elif unit == Units.DISTANCE_KILOMETERS:
            return 'kilometers'
        elif unit == Units.DISTANCE_DECIMAL_DEGREES:
            return 'decimal_degrees'
        elif unit == Units.DISTANCE_DECIMETERS:
            return 'decimeters'
        return None

    @staticmethod
    def time_unit_to_string(unit):
        if unit == Units.TIME_UNITS_UNKNOWN:
            return 'unknown'
        elif unit == Units.TIME_UNITS_MILLISECONDS:
            return 'milliseconds'
        elif unit == Units.TIME_UNITS_SECONDS:
            return 'seconds'
        elif unit == Units.TIME_UNITS_MINUTES:
            return 'minutes'
        elif unit == Units.TIME_UNITS_HOURS:
            return 'hours'
        elif unit == Units.TIME_UNITS_DAYS:
            return 'days'
        elif unit == Units.TIME_UNITS_WEEKS:
            return 'weeks'
        elif unit == Units.TIME_UNITS_MONTHS:
            return 'months'
        elif unit == Units.TIME_UNITS_YEARS:
            return 'years'
        elif unit == Units.TIME_UNITS_DECADES:
            return 'decades'
        elif unit == Units.TIME_UNITS_CENTURIES:
            return 'centuries'
        return None
