import unittest
from ScriptVocab import is_time_stamp, has_letters, has_no_text, clean_up, create_word_list_from_text, create_dictionary, translate_dictionary, make_output_filename


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
        self.assertFalse(has_no_text('This line has letters and numbers 1234567890'))
      
    def test_has_no_text_with_letters_and_punctuation(self):
        self.assertFalse(has_no_text('This line has letters and punctuation !!!,,,,...;;;'))

    def test_has_no_text_with_time_stamp(self):
        self.assertTrue(has_no_text('00:01:23,456'))
    
    def test_has_no_text_empty_string(self):   
        self.assertTrue(has_no_text(''))

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

    def test_make_output_filename_with_extension(self):
        filename = 'input.subtitle.txt'
        output_extension = 'csv'
        expected = 'Dictionary [input.subtitle].csv'
        self.assertEqual(make_output_filename(
            filename, output_extension), expected)


if __name__ == '__main__':
    unittest.main()
