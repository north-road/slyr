# pylint: too-many-lines

"""
Test file utils
"""

import unittest

from .test_case import SlyrTestCase

from ..bintools.file_utils import FileUtils


class TestFileUtils(SlyrTestCase):
    def test_clean_symbol_name_for_file(self):
        # empty string
        self.assertEqual(FileUtils.clean_symbol_name_for_file(""), "__")

        # string with no special characters, less than 30 chars
        self.assertEqual(
            FileUtils.clean_symbol_name_for_file("HelloWorld"), "HelloWorld"
        )

        # string with one of each special character
        self.assertEqual(
            FileUtils.clean_symbol_name_for_file('a/b>c<d\\e?f*g"h:i;j k,l'),
            "a_b_c_d_e_f_g_h_i_j_k_l",
        )

        # string with multiple special characters of the same type
        self.assertEqual(
            FileUtils.clean_symbol_name_for_file("test//test>>test<<test"),
            "test_test_test_test",
        )

        # string with mixed special characters
        self.assertEqual(
            FileUtils.clean_symbol_name_for_file("file/name with?many*chars<end>"),
            "file_name_with_many_chars_end",
        )

        # string that is exactly 30 characters long (after cleaning)
        clean_target = "abcdefghijklmnopqrstuvwxyz1234"  # 30 chars
        self.assertEqual(
            FileUtils.clean_symbol_name_for_file(clean_target), clean_target
        )

        # string that is longer than 30 characters (after cleaning) and needs truncation
        long_string = "this_is_a_very_long_file_name_that_will_be_truncated"
        expected_long = "this_is_a_very_long_file_name_"  # 30 chars
        self.assertEqual(
            FileUtils.clean_symbol_name_for_file(long_string), expected_long
        )

        # string with leading/trailing spaces before cleaning
        self.assertEqual(
            FileUtils.clean_symbol_name_for_file("  leading_and_trailing_spaces  "),
            "leading_and_trailing_spaces",
        )

        # string with leading/trailing spaces that gets cleaned and truncated
        self.assertEqual(
            FileUtils.clean_symbol_name_for_file(
                "  valid/name but very long indeed for a filename "
            ),
            "valid_name_but_very_long_indee",
        )

        # string with special characters that results in a name less than 30 chars
        self.assertEqual(
            FileUtils.clean_symbol_name_for_file("short name with / and ,"),
            "short_name_with_and",
        )

        # string with only special characters
        self.assertEqual(
            FileUtils.clean_symbol_name_for_file(
                '///\\\\\\???***""":::;;;   ,,,<<<>>>'
            ),
            "__",
        )

        # string that becomes empty after stripping (only spaces)
        self.assertEqual(FileUtils.clean_symbol_name_for_file("     "), "__")

        # string with mixed alphanumeric and special characters, requiring truncation
        self.assertEqual(
            FileUtils.clean_symbol_name_for_file(
                'A/B>C<D\\E?F*G"H:I;J K,L_very_long_suffix'
            ),
            "A_B_C_D_E_F_G_H_I_J_K_L_very_l",
        )

        # string already clean and exactly 30 chars
        self.assertEqual(
            FileUtils.clean_symbol_name_for_file("already_clean_and_length_is_30"),
            "already_clean_and_length_is_30",
        )

        # string already clean and shorter than 30 chars
        self.assertEqual(
            FileUtils.clean_symbol_name_for_file("already_clean_short"),
            "already_clean_short",
        )

        # string with all replaceable characters at the beginning
        self.assertEqual(
            FileUtils.clean_symbol_name_for_file(
                "/><\\?*\"':;, normal_text_here_1234567890"
            ),
            "normal_text_here_1234567890",
        )

        # string with all replaceable characters at the end
        self.assertEqual(
            FileUtils.clean_symbol_name_for_file(
                "normal_text_here_1234567890/><\\?*\"':;, "
            ),
            "normal_text_here_1234567890",
        )

        # string containing numbers and special characters
        self.assertEqual(
            FileUtils.clean_symbol_name_for_file("123/456*789:;<>,? "), "123_456_789"
        )

        # real world example
        self.assertEqual(
            FileUtils.clean_symbol_name_for_file(
                """Gepland, Privé, 2018; Gepland, Privé, 2017; Gepland, Privé, 2016; Gepland, Privé, 2027; Gepland, Privé, 2015; Gepland, Privé, 2014; Gepland, Privé, 2013; Gepland, Privé, 2021; Gepland, Privé, 2020; Gepland, Privé, 2019"""
            ),
            "Gepland_Privé_2018_Gepland_Pri",
        )


if __name__ == "__main__":
    unittest.main()
