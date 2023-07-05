
import os
import unittest
from pathlib import Path
from unittest.mock import patch
import builtins

from script_vocab import ScriptVocab, scriptVocabConfig

TEMP_TEST_DIR = "/tmp/dir/"
TEMP_TEST_FILE_LOAD = TEMP_TEST_DIR + "test_load.txt"
TEMP_TEST_FILE_SAVE = TEMP_TEST_DIR + "test_save.txt"

class TestScriptVocab(unittest.TestCase):
    def setUp(self):
        os.makedirs(TEMP_TEST_DIR, exist_ok=True)
        Path(TEMP_TEST_FILE_LOAD).write_text('This is a test.')

        self.config = scriptVocabConfig()
        self.sv = ScriptVocab(self.config)

    def tearDown(self):
        Path(TEMP_TEST_FILE_LOAD).unlink(missing_ok=True)
        Path(TEMP_TEST_FILE_SAVE).unlink(missing_ok=True)
        os.rmdir(TEMP_TEST_DIR)

    def test_enter_and_exit(self):
        with patch.object(builtins, 'print') as mock_print:
            with ScriptVocab(scriptVocabConfig()) as test_sv:
                self.assertIsInstance(test_sv, ScriptVocab)
        mock_print.assert_any_call('Exiting')

    def test_input_text(self):
        self.sv.config.min_appearance=1
        self.sv.config.min_word_size=1
        self.sv.input_text("This is a test.")
        self.assertEqual(self.sv.all_words, ["this", "is", "a", "test"])

    def test_input_text_empty_string(self):
        self.sv.input_text("")
        self.assertEqual(self.sv.all_words, [])

    def test_input_text_single_word(self):
        self.sv.input_text("word")
        self.assertEqual(self.sv.all_words, ["word"])

    def test_input_text_multiple_words(self):
        self.sv.input_text("This is a test.")
        self.assertEqual(self.sv.all_words, ["this", "is", "a", "test"])

    def test_input_files_one_file(self):
        self.sv.input_files((TEMP_TEST_FILE_LOAD), 'txt', 'utf-8')
        self.assertEqual(len(self.sv.all_words), 4)

    def test_input_files_directory(self):
        self.sv.input_files((TEMP_TEST_DIR), 'txt', 'utf-8')
        self.assertEqual(len(self.sv.all_words), 4)

    def test_input_files_nonexisting_file_throw_exception(self):
        with self.assertRaises(FileNotFoundError):
            self.sv.input_files(("nonExistingFile.txt"), 'txt', 'utf-8')

    def test_process_files(self):
        self.sv.config.min_appearance=1
        self.sv.process_files([TEMP_TEST_FILE_LOAD], "utf-8")
        self.assertEqual(len(self.sv.all_words), 4)

    def test_has_no_text(self):
        self.assertTrue(self.sv.has_no_text(""))
        self.assertTrue(self.sv.has_no_text("123"))
        self.assertTrue(self.sv.has_no_text("00:00:00,000"))
        self.assertTrue(self.sv.has_no_text("..."))
        self.assertFalse(self.sv.has_no_text("This is a test."))
        self.assertFalse(self.sv.has_no_text('Letters, and 1234567890!!'))

    def test_is_lowercase_letter_or_comma(self):
        self.assertTrue(self.sv.is_lowercase_letter_or_comma("a"))
        self.assertTrue(self.sv.is_lowercase_letter_or_comma(","))
        self.assertFalse(self.sv.is_lowercase_letter_or_comma("A"))
        self.assertFalse(self.sv.is_lowercase_letter_or_comma("1"))

    def test_clean_up(self):
        lines = [
            "1\n",
            "00:00:00,000 --> 00:00:01,000\n",
            "<i>This is a test.</i>\n",
            "2\n",
            "00:00:01,000 --> 00:00:02,000\n",
            "This is a\n",
            "test.\n",
        ]
        cleaned_lines = self.sv.clean_up(lines)
        self.assertEqual(len(cleaned_lines), 2)
        self.assertEqual(cleaned_lines[0], "This is a test.")
        self.assertEqual(cleaned_lines[1], "This is a test.")

    def test_create_word_list_from_text(self):
        text = "This is a test."
        words = self.sv.create_word_list_from_text(text, 1)
        self.assertEqual(len(words), 4)
        self.assertIn("this", words)
        self.assertIn("is", words)
        self.assertIn("a", words)
        self.assertIn("test", words)

    def test_create_word_list_from_text_with_no_text(self):
        text = "1234 1234567890"
        expected = []
        self.assertEqual(self.sv.create_word_list_from_text(text, 1), expected)

    def test_create_word_list_from_text_min_word_size_with_no_text(self):
        text = "word 1234 1234567890 w1rd sad"
        expected = ['word', 'w1rd']
        self.assertEqual(self.sv.create_word_list_from_text(text, 4), expected)

    def test_create_dictionary(self):
        words = ['test', 'test', 'example', 'example', 'example']
        expected = {'example': 3, 'test': 2}
        self.assertEqual(self.sv.create_dictionary(words, 2), expected)

    def test_create_dictionary_with_min_appearance(self):
        words = ['test', 'test', 'example', 'example', 'example']
        expected = {'example': 3}
        self.assertEqual(self.sv.create_dictionary(words, 3), expected)

    def test_create_dictionary_with_word_to_filter_out(self):
        words = ['test', 'test', 'example', 'example', 'example', 'filterme']
        expected = {'example': 3, 'test': 2}
        self.assertEqual(self.sv.create_dictionary(words, 2), expected)

    @patch('translators.translate_text')
    @patch('time.sleep')
    def test_translate_chunk(self, sleep_mock, mock_translate_text):
        mock_translate_text.return_value = "Esto es una prueba."
        chunk = ["This is a test."]
        input_lang = 'es'
        target_lang = 'en'

        translated_chunk = self.sv.translate_chunk(chunk, input_lang, target_lang)
        mock_translate_text.assert_called_with(
            "\n".join(chunk),
            translator='bing',
            from_language=input_lang,
            to_language=target_lang
        )
        self.assertEqual(len(translated_chunk), 1)
        self.assertEqual(translated_chunk[0], "Esto es una prueba.")
        self.assertEqual(sleep_mock.call_count, 0)

    @patch('translators.translate_text')
    @patch('time.sleep')
    def test_translate_chunk_throws_exception(self, sleep_mock, mock_translate_text):
        mock_translate_text.side_effect = Exception("Test Exception")
        chunk = ["This is a test."]
        input_lang = 'es'
        target_lang = 'en'

        self.assertRaises(Exception, self.sv.translate_chunk, chunk, input_lang, target_lang)
        mock_translate_text.assert_called_with(
            "\n".join(chunk),
            translator='bing',
            from_language=input_lang,
            to_language=target_lang
        )
        self.assertEqual(sleep_mock.call_count, 1)

    @patch('script_vocab.ScriptVocab.translate_chunk')
    @patch('time.sleep')
    def test_translate_dictionary(self, sleep_mock, translate_chunk_mock):
        translate_chunk_mock.return_value = ["word1", "word2", "word3"]

        test_dict = {"palabra1": 5, "palabra2": 3, "palabra3": 1}
        input_lang = 'es'
        target_lang = 'en'

        result = self.sv.translate_dictionary(
            test_dict, input_lang, target_lang, 3)

        translate_chunk_mock.assert_called_with(
            ["palabra1", "palabra2", "palabra3"],
            input_lang,
            target_lang
        )

        expected_result = {"palabra1": "word1",
                           "palabra2": "word2", "palabra3": "word3"}
        self.assertEqual(result, expected_result)
        self.assertEqual(sleep_mock.call_count, 1)

    @patch('script_vocab.ScriptVocab.translate_chunk')
    @patch('time.sleep')
    def test_translate_dictionary_waiting(self, sleep_mock, translate_chunk_mock):
        translate_chunk_mock.return_value = ["word1", "word2"]

        test_dict = {"palabra1": 5, "palabra2": 3, "palabra3": 1, "palabra4": 4}
        input_lang = 'es'
        target_lang = 'en'

        result = self.sv.translate_dictionary(
            test_dict, input_lang, target_lang, 2)

        expected_result = {"palabra1": "word1",
                           "palabra2": "word2", "palabra3": "word1", "palabra4": "word2"}
        self.assertEqual(result, expected_result)
        self.assertEqual(translate_chunk_mock.call_count, 2)
        self.assertEqual(sleep_mock.call_count, 2)

    @patch('script_vocab.ScriptVocab.create_dictionary')
    @patch('script_vocab.ScriptVocab.translate_dictionary')
    def test_run(self, translate_dictionary_mock, create_dictionary_mock):
        create_dictionary_mock.return_value = {"palabra1": 5, "palabra2": 3, "palabra3": 1}
        translate_dictionary_mock.return_value = {"palabra1": "word1", "palabra2": "word2", "palabra3": "word3"}
        self.sv.all_words = ['word1', 'word2', 'word3']
        self.sv.config.min_appearance = 2
        self.sv.run()
        self.assertEqual(self.sv.output, ['5, palabra1, word1', '3, palabra2, word2', '1, palabra3, word3'])

    @patch('script_vocab.ScriptVocab.create_dictionary')
    @patch('script_vocab.ScriptVocab.translate_dictionary')
    def test_run_with_empty_input(self, translate_dictionary_mock, create_dictionary_mock):
        create_dictionary_mock.return_value = {}
        translate_dictionary_mock.return_value = {}
        self.sv.all_words = ['']
        self.sv.config.min_appearance = 2
        self.sv.run()
        self.assertEqual(self.sv.output, [])


    def test_save_output_to_file(self):
        self.sv.output = ['5, palabra1, word1', '3, palabra2, word2', '1, palabra3, word3']
        self.sv.save_output_to_file(TEMP_TEST_FILE_SAVE)
        with open(TEMP_TEST_FILE_SAVE, 'r') as f:
            self.assertEqual(f.read().strip(), 'Count, Word, Translation\n5, palabra1, word1\n3, palabra2, word2\n1, palabra3, word3')

    def test_save_output_to_file_no_output(self):
        self.sv.save_output_to_file(TEMP_TEST_FILE_SAVE)
        with open(TEMP_TEST_FILE_SAVE, 'r') as f:
            self.assertEqual(f.read().strip(), '')

    def test_get_output_as_json(self):
        self.sv.output = ['5, palabra1, word1']
        self.assertEqual(self.sv.get_output_as_json(), [{'occurrences': '5', 'original_text': 'palabra1', 'translated_text': 'word1'}])

    def test_get_output_as_json_when_output_is_empty(self):
        self.sv.output = ['']
        self.assertEqual(self.sv.get_output_as_json(), None)

    def test_get_output_as_json_when_output_has_invalid_data(self):
        self.sv.output = ['12,notTranslatedWord']
        self.assertEqual(self.sv.get_output_as_json(), None)
