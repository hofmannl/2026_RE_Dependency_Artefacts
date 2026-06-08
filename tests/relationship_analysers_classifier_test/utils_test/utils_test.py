import unittest
from parameterized import parameterized

from relationship_analysers_classifier.relationship_analysers.utitls.utils import (
    clean_element,
    extract_triple,
    extract_triple_elements,
)


class UtilsTest(unittest.TestCase):
    @parameterized.expand([
        ("simple", "hello", "hello"),
        ("uppercase", "HELLO", "hello"),
        ("mixed_case", "HeLLo", "hello"),
        ("leading_whitespace", "  hello", "hello"),
        ("trailing_whitespace", "hello  ", "hello"),
        ("both_whitespace", "  hello  ", "hello"),
        ("tabs_and_spaces", "\t  hello  \n", "hello"),
        ("empty_string", "", ""),
        ("only_whitespace", "   ", ""),
    ])
    def test_clean_element(self, name: str, input_str: str, expected: str):
        result = clean_element(input_str)
        self.assertEqual(result, expected)

    @parameterized.expand([
        ("basic_triple",
         "car--is contained in--vehicle",
         ("car", "is contained in", "vehicle")),
        ("with_whitespace",
         "  car--is contained in--vehicle  ",
         ("car", "is contained in", "vehicle")),
        ("uppercase_elements",
         "CAR--IS CONTAINED IN--VEHICLE",
         ("car", "is contained in", "vehicle")),
        ("mixed_case",
         "Car--Is Contained In--Vehicle",
         ("car", "is contained in", "vehicle")),
        ("single_words",
         "wheel--part of--bicycle",
         ("wheel", "part of", "bicycle")),
        ("complex_phrases",
         "database entry--is part of--system database",
         ("database entry", "is part of", "system database")),
        ("special_chars",
         "user_admin--contains--user",
         ("user_admin", "contains", "user")),
    ])
    def test_extract_triple_valid(self, name: str, triple: str, expected: tuple):
        result = extract_triple(triple)
        self.assertEqual(result, expected)

    @parameterized.expand([
        ("missing_second_part", "car--vehicle"),
        ("missing_all_separators", "car is contained in vehicle"),
        ("extra_separators", "car--is--contained--in--vehicle"),
        ("empty_string", ""),
        ("only_separators", "----"),
    ])
    def test_extract_triple_invalid(self, name: str, triple: str):
        result = extract_triple(triple)
        self.assertIsNone(result)

    def test_extract_triple_custom_separator(self):
        """Test extraction with custom separator."""
        result = extract_triple("car | is contained in | vehicle", seperator=" | ")
        expected = ("car", "is contained in", "vehicle")
        self.assertEqual(result, expected)

    @parameterized.expand([
        ("single_line",
         "car--is contained in--vehicle",
         [("car", "is contained in", "vehicle")]),
        ("two_lines",
         "car--is contained in--vehicle\nbattery--is contained in--car",
         [("car", "is contained in", "vehicle"), ("battery", "is contained in", "car")]),
        ("three_lines_with_whitespace",
         "  car --is contained in--vehicle  \n  wheel --part of--bicycle  \n  engine --component of--car  ",
         [("car", "is contained in", "vehicle"), ("wheel", "part of", "bicycle"), ("engine", "component of", "car")]),
        ("with_empty_lines",
         "car--is contained in--vehicle\n\nbattery--is contained in--car",
         [("car", "is contained in", "vehicle"), ("battery", "is contained in", "car")]),
        ("uppercase_mixed",
         "CAR--IS CONTAINED IN--VEHICLE\nBATTERY--IS CONTAINED IN--CAR",
         [("car", "is contained in", "vehicle"), ("battery", "is contained in", "car")]),
    ])
    def test_extract_triple_elements_valid(self, name: str, triples: str, expected: list):
        result = extract_triple_elements(triples)
        self.assertEqual(result, expected)

    @parameterized.expand([
        ("with_invalid_lines",
         "car--is contained in--vehicle\ninvalid line\nbattery--is contained in--car",
         [("car", "is contained in", "vehicle"), None, ("battery", "is contained in", "car")]),
        ("all_invalid",
         "invalid1\ninvalid2\ninvalid3",
         [None, None, None]),
    ])
    def test_extract_triple_elements_with_invalid(self, name: str, triples: str, expected: list):
        result = extract_triple_elements(triples)
        self.assertEqual(result, expected)

    def test_extract_triple_elements_custom_separators(self):
        """Test extraction with custom separators."""
        triples = "car | is contained in | vehicle\nbattery | is contained in | car"
        result = extract_triple_elements(triples, seperator=" | ", line_seperator="\n")
        expected = [
            ("car", "is contained in", "vehicle"),
            ("battery", "is contained in", "car")
        ]
        self.assertEqual(result, expected)

    def test_extract_triple_elements_empty_string(self):
        """Test extraction from empty string."""
        result = extract_triple_elements("")
        self.assertEqual(result, [])

    def test_extract_triple_elements_only_whitespace(self):
        """Test extraction from whitespace-only string."""
        result = extract_triple_elements("   \n   \n   ")
        self.assertEqual(result, [])

    def test_llm_output_format(self):
        """Test extraction from LLM output format."""
        llm_output = """car--battery--false\ncar--car--false\ncar--engine--true\ncar--wheel--true\nbattery--car--true"""
        result = extract_triple_elements(llm_output)
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0], ("car", "battery", "false"))
        self.assertEqual(result[2], ("car", "engine", "true"))
        self.assertEqual(result[4], ("battery", "car", "true"))

    def test_requirements_engineering_format(self):
        """Test extraction from requirements engineering analysis output."""
        analysis_output = """wheel--is part of--bicycle
engine--is component of--car
battery--is contained in--car
door--is part of--car"""
        result = extract_triple_elements(analysis_output)
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0], ("wheel", "is part of", "bicycle"))
        self.assertEqual(result[1], ("engine", "is component of", "car"))