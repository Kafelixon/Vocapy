import unittest
from ScriptVocab import is_time_stamp, has_letters, has_no_text, clean_up, create_word_list_from_text, create_dictionary, translate_dictionary, make_output_filename


class TestScriptVocab(unittest.TestCase):

    def test_is_time_stamp(self):
        self.assertTrue(is_time_stamp('00:01:23,456'))
        self.assertFalse(is_time_stamp('This is not a timestamp'))

    def test_has_letters(self):
        self.assertTrue(has_letters('This line has letters'))
        self.assertFalse(has_letters('1234567890'))
        # Additional test case: check a line with punctuation but no letters
        self.assertFalse(has_letters('!!!,,,,...;;;'))

    def test_has_no_text(self):
        self.assertTrue(has_no_text('1234567890'))
        self.assertFalse(has_no_text('This line has text'))
        self.assertTrue(is_time_stamp('00:01:23,456'))
        self.assertTrue(has_no_text(''))
        # Additional test case: check a line with punctuation but no letters
        self.assertTrue(has_no_text('!!!,,,,...;;;'))

    def test_clean_up(self):
        lines = ['00:01:23,456', '', 'This line should remain']
        expected = ['This line should remain']
        self.assertEqual(clean_up(lines), expected)

    def test_create_word_list_from_text(self):
        text = "This is a simple test text"
        expected = ["This", "is", "a", "simple", "test", "text"]
        self.assertEqual(create_word_list_from_text(text), expected)

    def test_create_dictionary(self):
        words = ['test', 'test', 'example', 'example', 'example']
        expected = {'example': 3, 'test': 2}
        self.assertEqual(create_dictionary(words, 2), expected)
        # Additional test case: check a word list with words that should be filtered out
        words = ['test', 'test', 'example', 'example', 'example', 'filterme']
        expected = {'example': 3, 'test': 2}
        self.assertEqual(create_dictionary(words, 2), expected)

    # This method interacts with an external service, so you would typically mock it in your tests.
    # This is a very simplistic example.
    def test_translate_dictionary(self):
        words_dict = {'example': 3, 'test': 2}
        input_lang = 'en'
        target_lang = 'es'
        expected = {'example': 'ejemplo', 'test': 'prueba'}
        self.assertEqual(translate_dictionary(
            words_dict, input_lang, target_lang), expected)

    def test_make_output_filename(self):
        filename = 'input.txt'
        output_extension = 'csv'
        expected = 'Dictionary [input].csv'
        self.assertEqual(make_output_filename(
            filename, output_extension), expected)
        # Additional test case: check an input filename with an extension
        filename = 'input.subtitle.txt'
        expected = 'Dictionary [input.subtitle].csv'
        self.assertEqual(make_output_filename(
            filename, output_extension), expected)


if __name__ == '__main__':
    unittest.main()
