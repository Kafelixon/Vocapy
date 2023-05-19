import unittest
from ScriptVocab import *
from unittest.mock import patch, MagicMock
import time


class TestScriptVocab(unittest.TestCase):

    def test_is_time_stamp_with_timestamp(self):
        self.assertTrue(is_time_stamp('00:01:23,456'))

    def test_is_time_stamp_with_no_timestamp(self):
        self.assertFalse(is_time_stamp('This is not a timestamp'))

    def test_has_letters_with_letters(self):
        self.assertTrue(has_letters('This line has letters'))

    def test_has_letters_with_numbers_and_no_letters(self):
        self.assertFalse(has_letters('1234567890'))

    def test_has_letters_with_punctuation_and_no_letters(self):
        self.assertFalse(has_letters('!!!,,,,...;;;'))

    def test_has_no_text_with_letters(self):
        self.assertFalse(has_no_text('This line has letters'))

    def test_has_no_text_with_numbers(self):
        self.assertTrue(has_no_text('1234567890'))

    def test_has_no_text_with_punctuation(self):
        self.assertTrue(has_no_text('!!!,,,,...;;;'))

    def test_has_no_text_with_letters_and_numbers(self):
        self.assertFalse(has_no_text(
            'This line has letters and numbers 1234567890'))

    def test_has_no_text_with_letters_and_punctuation(self):
        self.assertFalse(has_no_text(
            'This line has letters and punctuation !!!,,,,...;;;'))

    def test_has_no_text_with_time_stamp(self):
        self.assertTrue(has_no_text('00:01:23,456'))

    def test_has_no_text_empty_string(self):
        self.assertTrue(has_no_text(''))

    def test_is_lowercase_letter_or_comma_lowercase(self):
        self.assertTrue(is_lowercase_letter_or_comma('a'))

    def test_is_lowercase_letter_or_comma_comma(self):
        self.assertTrue(is_lowercase_letter_or_comma(','))

    def test_is_lowercase_letter_or_comma_uppercase(self):
        self.assertFalse(is_lowercase_letter_or_comma('A'))

    def test_is_lowercase_letter_or_comma_number(self):
        self.assertFalse(is_lowercase_letter_or_comma('1'))

    def test_is_lowercase_letter_or_comma_punctuation(self):
        self.assertFalse(is_lowercase_letter_or_comma('!'))

    def test_clean_up(self):
        lines = ['00:01:23,456', '', 'This line should remain']
        expected = ['This line should remain']
        self.assertEqual(clean_up(lines), expected)

    def test_create_word_list_from_text_min_word_size(self):
        text = "This is a simple test text"
        expected = ['This', 'simple', 'test', 'text']
        self.assertEqual(create_word_list_from_text(text, 3), expected)

    def test_create_word_list_from_text_with_no_text(self):
        text = "1234 1234567890"
        expected = []
        self.assertEqual(create_word_list_from_text(text, 1), expected)

    def test_create_word_list_from_text_min_word_size_with_no_text(self):
        text = "word 1234 1234567890 w1rd sad"
        expected = ['word', 'w1rd']
        self.assertEqual(create_word_list_from_text(text, 3), expected)

    def test_create_dictionary(self):
        words = ['test', 'test', 'example', 'example', 'example']
        expected = {'example': 3, 'test': 2}
        self.assertEqual(create_dictionary(words, 2), expected)

    def test_create_dictionary_with_word_to_filter_out(self):
        words = ['test', 'test', 'example', 'example', 'example', 'filterme']
        expected = {'example': 3, 'test': 2}
        self.assertEqual(create_dictionary(words, 2), expected)

    @patch('ScriptVocab.ts.translate_text')  # Patch the function
    # Patch the sleep function to speed up tests
    @patch('ScriptVocab.time.sleep')
    def test_translate_dictionary(self, sleep_mock, translate_mock):
        # Setup mock to return specific translation
        translate_mock.return_value = "word1\nword2\nword3"

        # Test dictionary
        test_dict = {"palabra1": 5, "palabra2": 3, "palabra3": 1}
        input_lang = 'es'
        target_lang = 'en'

        # Call the function - translate_text has been replaced by the mock
        result = translate_dictionary(
            test_dict, input_lang, target_lang)

        # Check that translate_text was called with the correct arguments
        translate_mock.assert_called_with(
            "\n".join(test_dict.keys()),
            translator='bing',
            from_language=input_lang,
            to_language=target_lang
        )

        # Check that the return value is as expected
        expected_result = {"palabra1": "word1",
                           "palabra2": "word2", "palabra3": "word3"}
        self.assertEqual(result, expected_result)

    @patch('ScriptVocab.ts.translate_text')
    @patch('ScriptVocab.time.sleep')
    def test_translate_dictionary_with_exception(self, sleep_mock, translate_mock):
        # Simulate an exception on the first call and success on the second
        translate_mock.side_effect = [Exception('Test exception'), "word1\nword2\nword3"]

        test_dict = {"palabra1": 5, "palabra2": 3, "palabra3": 1}
        input_lang = 'es'
        target_lang = 'en'
        
        result = translate_dictionary(test_dict, input_lang, target_lang)

        # The translate_text method should have been called twice because of the exception
        self.assertEqual(translate_mock.call_count, 2)

        # The sleep function should have been called once before the second attempt
        sleep_mock.assert_called_once_with(2)

        expected_result = {"palabra1": "word1", "palabra2": "word2", "palabra3": "word3"}
        self.assertEqual(result, expected_result)

    @patch('ScriptVocab.ts.translate_text')
    @patch('ScriptVocab.time.sleep')
    def test_translate_dictionary_with_persistent_exception(self, sleep_mock, translate_mock):
        # Simulate an exception on both calls
        translate_mock.side_effect = Exception('Test exception')

        test_dict = {"palabra1": 5, "palabra2": 3, "palabra3": 1}
        input_lang = 'es'
        target_lang = 'en'

        with self.assertRaises(Exception):
            translate_dictionary(test_dict, input_lang, target_lang)

        # The translate_text method should have been called twice because of the exception
        self.assertEqual(translate_mock.call_count, 2)

        # The sleep function should have been called once before the second attempt
        sleep_mock.assert_called_once_with(2)

    def test_make_output_filename(self):
        filename = 'input.txt'
        output_extension = 'csv'
        expected = 'Dictionary [input].csv'
        self.assertEqual(make_output_filename(
            filename, output_extension), expected)

    def test_make_output_filename_with_extension(self):
        filename = 'input.subtitle.txt'
        output_extension = 'csv'
        expected = 'Dictionary [input.subtitle].csv'
        self.assertEqual(make_output_filename(
            filename, output_extension), expected)


if __name__ == '__main__':
    unittest.main()
