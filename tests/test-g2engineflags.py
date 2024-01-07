#! /usr/bin/env python3

import unittest
from senzing import G2EngineFlags


class TestEnumMethods(unittest.TestCase):

    def test_flag_values(self):
        '''Test that each detailed flag has the correct value.'''

        self.assertEqual(G2EngineFlags.G2_EXPORT_INCLUDE_MULTI_RECORD_ENTITIES, 2 ** 0)
        self.assertEqual(G2EngineFlags.G2_EXPORT_INCLUDE_POSSIBLY_SAME, 2 ** 1)
        self.assertEqual(G2EngineFlags.G2_EXPORT_INCLUDE_POSSIBLY_RELATED, 2 ** 2)
        self.assertEqual(G2EngineFlags.G2_EXPORT_INCLUDE_NAME_ONLY, 2 ** 3)
        self.assertEqual(G2EngineFlags.G2_EXPORT_INCLUDE_DISCLOSED, 2 ** 4)
        self.assertEqual(G2EngineFlags.G2_EXPORT_INCLUDE_SINGLE_RECORD_ENTITIES, 2 ** 5)
        self.assertEqual(G2EngineFlags.G2_ENTITY_INCLUDE_POSSIBLY_SAME_RELATIONS, 2 ** 6)
        self.assertEqual(G2EngineFlags.G2_ENTITY_INCLUDE_POSSIBLY_RELATED_RELATIONS, 2 ** 7)
        self.assertEqual(G2EngineFlags.G2_ENTITY_INCLUDE_NAME_ONLY_RELATIONS, 2 ** 8)
        self.assertEqual(G2EngineFlags.G2_ENTITY_INCLUDE_DISCLOSED_RELATIONS, 2 ** 9)
        self.assertEqual(G2EngineFlags.G2_ENTITY_INCLUDE_ALL_FEATURES, 2 ** 10)
        self.assertEqual(G2EngineFlags.G2_ENTITY_INCLUDE_REPRESENTATIVE_FEATURES, 2 ** 11)
        self.assertEqual(G2EngineFlags.G2_ENTITY_INCLUDE_ENTITY_NAME, 2 ** 12)
        self.assertEqual(G2EngineFlags.G2_ENTITY_INCLUDE_RECORD_SUMMARY, 2 ** 13)
        self.assertEqual(G2EngineFlags.G2_ENTITY_INCLUDE_RECORD_TYPES, 2 ** 28)
        self.assertEqual(G2EngineFlags.G2_ENTITY_INCLUDE_RECORD_DATA, 2 ** 14)
        self.assertEqual(G2EngineFlags.G2_ENTITY_INCLUDE_RECORD_MATCHING_INFO, 2 ** 15)
        self.assertEqual(G2EngineFlags.G2_ENTITY_INCLUDE_RECORD_JSON_DATA, 2 ** 16)
        self.assertEqual(G2EngineFlags.G2_ENTITY_INCLUDE_RECORD_UNMAPPED_DATA, 2 ** 31)
        self.assertEqual(G2EngineFlags.G2_ENTITY_INCLUDE_RECORD_FEATURE_IDS, 2 ** 18)
        self.assertEqual(G2EngineFlags.G2_ENTITY_INCLUDE_RELATED_ENTITY_NAME, 2 ** 19)
        self.assertEqual(G2EngineFlags.G2_ENTITY_INCLUDE_RELATED_MATCHING_INFO, 2 ** 20)
        self.assertEqual(G2EngineFlags.G2_ENTITY_INCLUDE_RELATED_RECORD_SUMMARY, 2 ** 21)
        self.assertEqual(G2EngineFlags.G2_ENTITY_INCLUDE_RELATED_RECORD_TYPES, 2 ** 29)
        self.assertEqual(G2EngineFlags.G2_ENTITY_INCLUDE_RELATED_RECORD_DATA, 2 ** 22)
        self.assertEqual(G2EngineFlags.G2_ENTITY_OPTION_INCLUDE_INTERNAL_FEATURES, 2 ** 23)
        self.assertEqual(G2EngineFlags.G2_ENTITY_OPTION_INCLUDE_FEATURE_STATS, 2 ** 24)
        self.assertEqual(G2EngineFlags.G2_ENTITY_OPTION_INCLUDE_FEATURE_ELEMENTS, 2 ** 32)
        self.assertEqual(G2EngineFlags.G2_ENTITY_OPTION_INCLUDE_MATCH_KEY_DETAILS, 2 ** 34)
        self.assertEqual(G2EngineFlags.G2_FIND_PATH_PREFER_EXCLUDE, 2 ** 25)
        self.assertEqual(G2EngineFlags.G2_FIND_PATH_MATCHING_INFO, 2 ** 30)
        self.assertEqual(G2EngineFlags.G2_FIND_NETWORK_MATCHING_INFO, 2 ** 33)
        self.assertEqual(G2EngineFlags.G2_SEARCH_INCLUDE_FEATURE_SCORES, 2 ** 26)
        self.assertEqual(G2EngineFlags.G2_SEARCH_INCLUDE_STATS, 2 ** 27)

    def test_flag_by_string(self):
        '''Test that a flag can be retrieved by string.'''

        a_string = "G2_EXPORT_INCLUDE_DISCLOSED"
        an_enum = G2EngineFlags[a_string]
        self.assertEqual(an_enum, G2EngineFlags.G2_EXPORT_INCLUDE_DISCLOSED)

    def test_flag_by_bad_string(self):
        '''Test that a bad string does not create an enum.'''

        # Create a string that is _not_ the name of an enum member.

        a_string = "G2_EXPORT_INCLUDE_DISCLOSED_XXXXXXXXXXXXXX"

        # Expect a "KeyError" exception.

        success = False
        try:
            an_enum = G2EngineFlags[a_string]
        except KeyError as err:
            success = True
        except:
            success = False

        # Perform tests.

        self.assertTrue(success)

    def test_flag_or_by_string(self):
        '''Test that a series of strings can be OR-ed together.'''

        # Create a list of strings that are names of enum members.

        strings = {
            "G2_SEARCH_INCLUDE_ALL_ENTITIES",
            "G2_ENTITY_INCLUDE_REPRESENTATIVE_FEATURES",
            "G2_ENTITY_INCLUDE_ENTITY_NAME",
            "G2_ENTITY_INCLUDE_RECORD_SUMMARY",
            "G2_SEARCH_INCLUDE_FEATURE_SCORES"
        }

        # Bitwise "or" list of strings.

        result = 0
        for string in strings:
            result = result | G2EngineFlags[string]

        # Perform tests.

        self.assertEqual(result, G2EngineFlags.G2_SEARCH_BY_ATTRIBUTES_ALL)

    def test_or_by_list(self):
        '''Test that the "addition" works.'''

        # Create a list of strings that are names of enum members.

        strings = [
            "G2_SEARCH_INCLUDE_ALL_ENTITIES",
            "G2_ENTITY_INCLUDE_REPRESENTATIVE_FEATURES",
            "G2_ENTITY_INCLUDE_ENTITY_NAME",
            "G2_ENTITY_INCLUDE_RECORD_SUMMARY",
            "G2_SEARCH_INCLUDE_FEATURE_SCORES"
        ]

        # Bitwise "or" list of strings.

        result = G2EngineFlags.combine_flags(strings)

        # Perform tests.

        self.assertEqual(result, G2EngineFlags.G2_SEARCH_BY_ATTRIBUTES_ALL)

    def test_or_by_dict(self):
        '''Test that the "addition" works.'''

        # Create a list of strings that are names of enum members.

        strings = {
            "G2_SEARCH_INCLUDE_ALL_ENTITIES",
            "G2_ENTITY_INCLUDE_REPRESENTATIVE_FEATURES",
            "G2_ENTITY_INCLUDE_ENTITY_NAME",
            "G2_ENTITY_INCLUDE_RECORD_SUMMARY",
            "G2_SEARCH_INCLUDE_FEATURE_SCORES"
        }

        # Bitwise "or" list of strings.

        result = G2EngineFlags.combine_flags(strings)

        # Perform tests.

        self.assertEqual(result, G2EngineFlags.G2_SEARCH_BY_ATTRIBUTES_ALL)

    def test_or_by_set(self):
        '''Test that the "addition" works.'''

        # Create a list of strings that are names of enum members.

        strings = (
            "G2_SEARCH_INCLUDE_ALL_ENTITIES",
            "G2_ENTITY_INCLUDE_REPRESENTATIVE_FEATURES",
            "G2_ENTITY_INCLUDE_ENTITY_NAME",
            "G2_ENTITY_INCLUDE_RECORD_SUMMARY",
            "G2_SEARCH_INCLUDE_FEATURE_SCORES"
        )

        # Bitwise "or" list of strings.

        result = G2EngineFlags.combine_flags(strings)

        # Perform tests.

        self.assertEqual(result, G2EngineFlags.G2_SEARCH_BY_ATTRIBUTES_ALL)

    def test_or_by_list_alias(self):
        '''Test that the "addition" works.'''

        # Create a list of strings that are names of enum members.

        strings = (
            "G2_SEARCH_INCLUDE_ALL_ENTITIES",
            "G2_ENTITY_INCLUDE_REPRESENTATIVE_FEATURES",
            "G2_ENTITY_INCLUDE_ENTITY_NAME",
            "G2_ENTITY_INCLUDE_RECORD_SUMMARY",
            "G2_SEARCH_INCLUDE_FEATURE_SCORES"
        )

        # Dynamically add a method to the G2EngineFlags.

        setattr(G2EngineFlags, 'computeApiFlags', G2EngineFlags.combine_flags)

        # Bitwise "or" list of strings.

        result = G2EngineFlags.computeApiFlags(strings)

        # Perform tests.

        self.assertEqual(result, G2EngineFlags.G2_SEARCH_BY_ATTRIBUTES_ALL)

    def test_flag_add_values(self):
        '''Test that the "addition" works.'''

        # Create a list of strings that are names of enum members that add up to 7.

        strings = {
            "G2_EXPORT_INCLUDE_MULTI_RECORD_ENTITIES",
            "G2_EXPORT_INCLUDE_POSSIBLY_SAME",
            "G2_EXPORT_INCLUDE_POSSIBLY_RELATED"
        }

        # Bitwise "or" list of strings.

        result = 0
        for string in strings:
            result = result | G2EngineFlags[string]

        self.assertEqual(result, 7)

    def test_print_enums(self):
        '''Test that the "addition" works.'''

        print()
        for g2_engine_flag in G2EngineFlags:
            print("name: {0} value: {1}". format(g2_engine_flag.name, g2_engine_flag.value))


if __name__ == '__main__':
    unittest.main()
