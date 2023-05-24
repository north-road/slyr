# pylint: disable=bad-continuation,too-many-lines

"""
Test Conversion Utils
"""

import unittest

from ..converters.context import Context


class TestConversionContext(unittest.TestCase):
    """
    Test Conversion Context
    """

    def test_find_relative_path(self):
        """
        Test finding relative paths between two paths
        """
        # Test to get relative path when both paths are equal lengths
        self.assertEqual(Context.find_relative_path('foo/bar', "foo/sans"), '../bar')
        # Test to get relative path when both paths are the same
        self.assertEqual(Context.find_relative_path('foo/bar', "foo/bar"), '.')
        # Test to get relative path when both paths are technically the same
        self.assertEqual(Context.find_relative_path('foo/bar', "foo/bar/"), '.')
        # Test to get relative path when both paths are not relative
        self.assertEqual(Context.find_relative_path('foo/bar', "sans/eggs"), False)
        # Test to get relative path when the first path is longer than the second
        self.assertEqual(Context.find_relative_path('foo/bar/sans', "foo/sans"), '../bar/sans')
        # Test to get relative path when the second path is longer than the first
        self.assertEqual(Context.find_relative_path('foo/sans', "foo/bar/sans"), '../../sans')
        # Test to get relative path when both paths contain same path names after divergence
        self.assertEqual(Context.find_relative_path('foo/sans/eggs/let', "foo/bar/eggs/let"),
                         '../../../sans/eggs/let')

    def test_convert_dataset_path(self):
        """
        Test converting dataset paths
        """

        context = Context()
        # Test to get relative path when destination path is undefined
        self.assertEqual(context.convert_dataset_path('foo/bar'), 'foo\\bar')
        # Test to get relative path when destination path is same as input path
        context.destination_path = 'foo/bar'
        self.assertEqual(context.convert_dataset_path('foo/bar'), '.')
        # Test to get relative path when destination path is not relative to input path
        context.destination_path = 'sans/eggs'
        self.assertEqual(context.convert_dataset_path('foo/bar'), 'foo\\bar')
        # Test to get relative path when both paths are equal lengths
        context.destination_path = 'foo/sans'
        self.assertEqual(context.convert_dataset_path('foo/bar'), '..\\bar')
        # Test to get relative path when the first path is longer than the second
        context.destination_path = 'foo/sans'
        self.assertEqual(context.convert_dataset_path('foo/bar/sans'), '..\\bar\\sans')
        # Test to get relative path when the second path is longer than the first
        context.destination_path = 'foo/bar/sans'
        self.assertEqual(context.convert_dataset_path('foo/sans'), '..\\..\\sans')
        # Test to get relative path when both paths contain same path names after divergence
        context.destination_path = 'foo/bar/eggs/let'
        self.assertEqual(context.convert_dataset_path('foo/sans/eggs/let'),
                         '..\\..\\..\\sans\\eggs\\let')

        context.destination_path = '/home/nyall/dev/QGIS/tests/testdata/'
        self.assertEqual(context.convert_dataset_path('/home/nyall/dev/QGIS/tests/testdata'),
                         '.')

        context.destination_path = '/home/nyall/dev/QGIS/tests/testdata'
        self.assertEqual(context.convert_dataset_path('/home/nyall/dev/QGIS/tests/testdata/'),
                         '.')

        context.destination_path = '/home/nyall/dev/QGIS/tests/testdata'
        self.assertEqual(context.convert_dataset_path('/home/nyall/dev/QGIS/tests/testdata/lines.shp'),
                         '.\\lines.shp')

        context.destination_path = '/home/nyall/dev/QGIS/tests'
        self.assertEqual(context.convert_dataset_path('/home/nyall/dev/QGIS/tests/testdata/lines.shp'),
                         '.\\testdata\\lines.shp')

        context.destination_path = '/home/nyall/dev/QGIS/tests'
        self.assertEqual(context.convert_dataset_path('c:/home/nyall/dev/QGIS/tests/testdata/lines.shp'),
                         'c:\\home\\nyall\\dev\\QGIS\\tests\\testdata\\lines.shp')


if __name__ == '__main__':
    unittest.main()
