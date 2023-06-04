import os
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from ScriptVocab import ScriptVocab


class TestScriptVocab(unittest.TestCase):

    def setUp(self):
        os.makedirs('/tmp/dir', exist_ok=True)
        Path('/tmp/dir/file.txt').touch()
        Path('/tmp/dir/file2.txt').touch()
        Path('/tmp/file.txt').touch()

        args = {'path': '/tmp/file.txt', 'subs_language': 'auto', 'target_language': 'en', 'output': 'output.txt',
                'input_extension': 'txt', 'min_word_size': 1, 'min_appearance': 4, 'encoding': 'utf-8'}
        self.sv = ScriptVocab(args)

    def tearDown(self):
        Path('/tmp/dir/file.txt').unlink(missing_ok=True)
        Path('/tmp/dir/file2.txt').unlink(missing_ok=True)
        Path('/tmp/file.txt').unlink(missing_ok=True)
        os.rmdir('/tmp/dir')

    def test_create_list_of_files_to_process_with_file(self):
        self.sv.path = '/tmp/file.txt'
        self.assertEqual(self.sv.create_list_of_files_to_process(), [
                         Path('/tmp/file.txt')])

    def test_create_list_of_files_to_process_with_directory(self):
        self.sv.path = '/tmp/dir'
        self.assertEqual(
            set(self.sv.create_list_of_files_to_process()),
            set([str(Path('/tmp/dir/file.txt')), str(Path('/tmp/dir/file2.txt'))]))

    def test_create_list_of_files_to_process_with_nonexistent_path(self):
        self.sv.path = '/nonexistent/path'
        with self.assertRaises(FileNotFoundError):
            self.sv.create_list_of_files_to_process()

    def test_has_no_text_with_letters(self):
        self.assertFalse(self.sv.has_no_text('This line has letters'))

    def test_has_no_text_with_numbers(self):
        self.assertTrue(self.sv.has_no_text('1234567890'))

    def test_has_no_text_with_punctuation(self):
        self.assertTrue(self.sv.has_no_text('!!!,,,,...;;;'))

    def test_has_no_text_with_letters_and_numbers(self):
        self.assertFalse(self.sv.has_no_text(
            'This line has letters and numbers 1234567890'))

    def test_has_no_text_with_letters_and_punctuation(self):
        self.assertFalse(self.sv.has_no_text(
            'This line has letters and punctuation !!!,,,,...;;;'))

    def test_has_no_text_with_time_stamp(self):
        self.assertTrue(self.sv.has_no_text('00:01:23,456'))

    def test_has_no_text_empty_string(self):
        self.assertTrue(self.sv.has_no_text(''))

    def test_is_lowercase_letter_or_comma_lowercase(self):
        self.assertTrue(self.sv.is_lowercase_letter_or_comma('a'))

    def test_is_lowercase_letter_or_comma_comma(self):
        self.assertTrue(self.sv.is_lowercase_letter_or_comma(','))

    def test_is_lowercase_letter_or_comma_uppercase(self):
        self.assertFalse(self.sv.is_lowercase_letter_or_comma('A'))

    def test_is_lowercase_letter_or_comma_number(self):
        self.assertFalse(self.sv.is_lowercase_letter_or_comma('1'))

    def test_is_lowercase_letter_or_comma_punctuation(self):
        self.assertFalse(self.sv.is_lowercase_letter_or_comma('!'))

    def test_clean_up(self):
        lines = ['00:01:23,456', '',
                 'This line should remain', 'Hello with number 1']
        expected = ['This line should remain', 'Hello with number 1']
        self.assertEqual(self.sv.clean_up(lines), expected)

    def test_create_word_list_from_text_min_word_size(self):
        text = "This is a simple test text"
        expected = ['This', 'simple', 'test', 'text']
        self.assertEqual(self.sv.create_word_list_from_text(text, 3), expected)

    def test_create_word_list_from_text_with_no_text(self):
        text = "1234 1234567890"
        expected = []
        self.assertEqual(self.sv.create_word_list_from_text(text, 1), expected)

    def test_create_word_list_from_text_min_word_size_with_no_text(self):
        text = "word 1234 1234567890 w1rd sad"
        expected = ['word', 'w1rd']
        self.assertEqual(self.sv.create_word_list_from_text(text, 3), expected)

    def test_create_dictionary(self):
        words = ['test', 'test', 'example', 'example', 'example']
        expected = {'example': 3, 'test': 2}
        self.assertEqual(self.sv.create_dictionary(words, 2), expected)

    def test_create_dictionary_with_word_to_filter_out(self):
        words = ['test', 'test', 'example', 'example', 'example', 'filterme']
        expected = {'example': 3, 'test': 2}
        self.assertEqual(self.sv.create_dictionary(words, 2), expected)

    @patch('ScriptVocab.ts.translate_text')
    @patch('ScriptVocab.time.sleep')
    def test_translate_chunk(self, sleep_mock, mock_translate_text):
        mock_translate_text.return_value = "translated text"

        chunk = ['text1', 'text2']
        input_lang = 'es'
        target_lang = 'en'

        translated = self.sv.translate_chunk(chunk, input_lang, target_lang)
        mock_translate_text.assert_called_with(
            "\n".join(chunk),
            translator='bing',
            from_language=input_lang,
            to_language=target_lang
        )
        self.assertEqual(translated, ['translated text'])
        self.assertEqual(sleep_mock.call_count, 0)

    @patch('ScriptVocab.ts.translate_text')
    @patch('ScriptVocab.time.sleep')
    def test_translate_chunk_with_exception(self, sleep_mock, mock_translate_text):
        mock_translate_text.return_value = "translated text"

        chunk = ['text1', 'text2']
        input_lang = 'es'
        target_lang = 'en'

        translated = self.sv.translate_chunk(chunk, input_lang, target_lang)
        mock_translate_text.assert_called_with(
            "\n".join(chunk),
            translator='bing',
            from_language=input_lang,
            to_language=target_lang
        )
        self.assertEqual(translated, ['translated text'])
        self.assertEqual(sleep_mock.call_count, 1)

    @patch('ScriptVocab.ts.translate_text')
    @patch('ScriptVocab.time.sleep')
    def test_translate_dictionary(self, sleep_mock, translate_mock):
        # Setup mock to return specific translation
        translate_mock.return_value = "word1\nword2\nword3"

        # Test dictionary
        test_dict = {"palabra1": 5, "palabra2": 3, "palabra3": 1}
        input_lang = 'es'
        target_lang = 'en'

        # Call the function - translate_text has been replaced by the mock
        result = self.sv.translate_dictionary(
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
        # Check that the sleep function was not called
        self.assertEqual(sleep_mock.call_count, 0)

    @patch('ScriptVocab.ts.translate_text')
    @patch('ScriptVocab.time.sleep')
    def test_translate_dictionary_with_exception(self, sleep_mock, translate_mock):
        # Simulate an exception on the first call and success on the second
        translate_mock.side_effect = [
            Exception('Test exception'), "word1\nword2\nword3"]

        test_dict = {"palabra1": 5, "palabra2": 3, "palabra3": 1}
        input_lang = 'es'
        target_lang = 'en'
        result = self.sv.translate_dictionary(
            test_dict, input_lang, target_lang)

        # The translate_text method should have been called twice because of the exception
        self.assertEqual(translate_mock.call_count, 2)

        # Check that the sleep function was called once before the second attempt
        self.assertEqual(sleep_mock.call_count, 1)

        expected_result = {"palabra1": "word1",
                           "palabra2": "word2", "palabra3": "word3"}
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
            self.sv.translate_dictionary(test_dict, input_lang, target_lang)

        # The translate_text method should have been called twice because of the exception
        self.assertEqual(translate_mock.call_count, 2)

        # Check that the sleep function was called twice before the second attempt
        self.assertEqual(sleep_mock.call_count, 1)


if __name__ == '__main__':
    unittest.main()
