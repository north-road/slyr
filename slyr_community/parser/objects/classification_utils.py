#!/usr/bin/env python
"""
Serializable object subclass
"""


class ClassificationUtils:
    """
    ClassificationUtils
    """

    EQUAL_INTERVAL = 0
    NATURAL_BREAKS = 1
    DEFINED_INTERVAL = 2
    STANDARD_DEVIATION = 3
    GEOMETRIC_INTERVAL = 4
    QUANTILE = 5

    CLSID_TO_CLASSIFIER = {
        '62144be1-e05e-11d1-aaae-00c04fa334b3': EQUAL_INTERVAL,
        '62144bea-e05e-11d1-aaae-00c04fa334b3': NATURAL_BREAKS,
        '62144be8-e05e-11d1-aaae-00c04fa334b3': DEFINED_INTERVAL,
        'dc6d8015-49c2-11d2-aaff-00c04fa334b3': STANDARD_DEVIATION,
        'c79eb120-e98e-4af9-903d-70273e0c140e': GEOMETRIC_INTERVAL,
        '62144be9-e05e-11d1-aaae-00c04fa334b3': QUANTILE,
        '00000000-0000-0000-0000-000000000000': None
    }

    @staticmethod
    def classifier_to_string(classifier):  # pylint: disable=too-many-return-statements
        """
        Converts a classifier to a string
        """
        if classifier == ClassificationUtils.EQUAL_INTERVAL:
            return 'equal_interval'
        elif classifier == ClassificationUtils.NATURAL_BREAKS:
            return 'natural_breaks'
        elif classifier == ClassificationUtils.DEFINED_INTERVAL:
            return 'defined_interval'
        elif classifier == ClassificationUtils.STANDARD_DEVIATION:
            return 'standard_deviation'
        elif classifier == ClassificationUtils.GEOMETRIC_INTERVAL:
            return 'geometric_interval'
        elif classifier == ClassificationUtils.QUANTILE:
            return 'quantile'
        return None
