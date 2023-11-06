"""
This module defines the ScriptVocab and ScriptVocabConfig classes 
for processing text files and creating a vocabulary of words.

Classes:
    ScriptVocab: A class for processing text files and creating a vocabulary of words.
    ScriptVocabConfig: A configuration object for the ScriptVocab class.

Constants:
    CHUNK_SIZE (int): The size of the chunks used for translating text.

Exceptions:
    FileNotFoundError: Raised when the input path does not exist or is not a file or directory.
"""

import glob
import re
import socket
import time
from collections import Counter
from pathlib import Path
from deep_translator import GoogleTranslator

CHUNK_SIZE = 100


class ScriptVocabConfig:
    """
    A configuration object for the ScriptVocab class.

    Attributes:
        subs_language (str): Defaults to "auto".
            The language of the subtitles.
        target_language (str): Defaults to "en".
            The target language for vocabulary extraction.
        min_word_size (int): Defaults to 1.
            The minimum length of a word to be included in the vocabulary.
        min_appearance (int): Defaults to 4.
            The minimum number of times a word must appear to be included in the vocabulary.
    """

    def __init__(
        self,
        subs_language="auto",
        target_language="en",
        min_word_size=1,
        min_appearance=4,
    ):
        self.subs_language = subs_language
        self.target_language = target_language
        self.min_word_size = min_word_size
        self.min_appearance = min_appearance


class ScriptVocab:
    """
    A class for processing text files and creating a vocabulary of words.

    Attributes:
        config (ScriptVocabConfig): An instance of ScriptVocabConfig class.
        all_words (list[str]): A list of all words found in the input text.
        output (list[str]): A list of translated words.
        _translators_imported (bool): A flag to check if the translators module is imported.

    Methods:
        __init__(config: ScriptVocabConfig): Initializes the ScriptVocab class.
        __enter__(self): Returns the instance of the ScriptVocab class.
        __exit__(exc_type, exc_value, traceback): Prints "Exiting".

        is_internet_available(self) -> bool:
            Checks if the internet is available.
        input_text(text: str):
            Processes input text and adds words to all_words.
        input_files(path: str, input_extension: str, encoding: str):
            Processes input files and adds words to all_words.
        process_files(file_paths: list[str], encoding: str):
            Processes a list of file paths and adds words to all_words.
        has_no_text(line: str) -> bool:
            Checks if a line has no text.
        is_lowercase_letter_or_comma(char: str) -> bool:
            Checks if a character is a lowercase letter or comma.
        clean_up(lines: list[str]) -> list[str]:
            Cleans up lines of text.
        create_word_list_from_text(text: str, min_word_size: int) -> list[str]:
            Creates a list of words from text.
        translate_chunk(chunk: list[str], input_lang: str, target_lang: str, wait_time: int = 2
            ) -> list[str]: Translates a chunk of text.
        translate_text(chunk: list[str], input_lang: str, target_lang: str) -> list[str]:
            Translates text using the translators module.
        convert_to_chunks(words_list: list[str], chunk_size: int) -> list[list[str]]:
            Converts a list of words into chunks.
        translate_dictionary(
            dictionary: dict[str, int],
            source_language: str,
            target_language: str,
            chunk_size: int,
            ) -> dict[str, str]: Translates a dictionary of words.
    """

    def __init__(self, config: ScriptVocabConfig):
        """
        Initializes the ScriptVocab class.

        Args:
            config (ScriptVocabConfig): An instance of ScriptVocabConfig class.
        """
        self.config = config
        self.all_words: list[str] = []
        self.output: list[str] = []

    def __enter__(self):
        """
        Returns the instance of the ScriptVocab class.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Prints "Exiting".
        """
        print("Exiting")

    def is_internet_available(self) -> bool:
        """
        Checks if the internet is available.

        Returns:
            bool: True if the internet is available, False otherwise.
        """
        try:
            sock = socket.create_connection(("www.google.com", 80))
            if sock is not None:
                sock.close()
            print("isInternetAvailable succeeded")
            return True
        except OSError:
            pass
        print("isInternetAvailable failed")
        return False

    def input_text(self, text: str):
        """
        Processes input text and adds words to all_words.

        Args:
            text (str): The input text to process.
        """
        words = self.create_word_list_from_text(text, self.config.min_word_size)
        print(f"Found {len(words)} words in input text.")
        self.all_words.extend(words)

    def input_files(self, path: str, input_extension: str, encoding: str):
        """
        Processes input files and adds words to all_words.

        Args:
            path (str): The path to the input files.
            input_extension (str): The extension of the input files.
            encoding (str): The encoding of the input files.
        """
        path_obj = Path(path)
        if path_obj.is_file():
            filenames = [path_obj]
        elif path_obj.is_dir():
            filenames = glob.glob(f"{path}/*.{input_extension}")
        else:
            raise FileNotFoundError(
                f"Error: The path {path} does not exist or is not a file or directory."
            )
        self.process_files(filenames, encoding)

    def process_files(self, file_paths: list[str], encoding: str):
        """
        Processes a list of file paths and adds words to all_words.

        Args:
            file_paths (list[str]): A list of file paths to process.
            encoding (str): The encoding of the input files.
        """
        for file_path in file_paths:
            with open(file_path, "r", encoding=encoding) as f:
                lines = f.readlines()
                cleaned_lines = self.clean_up(lines)
                for line in cleaned_lines:
                    words = self.create_word_list_from_text(line, self.config.min_word_size)
                    self.all_words.extend(words)

    def has_no_text(self, line: str) -> bool:
        """
        Checks if a line has no text.

        Args:
            line (str): The line to check.

        Returns:
            bool: True if the line has no text, False otherwise.
        """
        line = line.strip()
        is_empty_or_numeric = not line or line.isnumeric()
        matches_timestamp = bool(re.match(r"^\d{1,2}:\d{2}:\d{2},\d{3}", line))
        contains_no_letters = not bool(re.search("[a-zA-Z]", line))
        return is_empty_or_numeric or matches_timestamp or contains_no_letters

    def is_lowercase_letter_or_comma(self, char: str) -> bool:
        """
        Checks if a character is a lowercase letter or comma.

        Args:
            char (str): The character to check.

        Returns:
            bool: True if the character is a lowercase letter or comma, False otherwise.
        """
        return char.isalpha() and char.lower() == char or char == ","

    def clean_up(self, lines: list[str]) -> list[str]:
        """
        Cleans up lines of text.

        Args:
            lines (list[str]): A list of lines to clean up.

        Returns:
            list[str]: A list of cleaned up lines.
        """
        cleaner_lines = [
            re.sub("<.*?>", "", line).rstrip() for line in lines if not self.has_no_text(line)
        ]
        for i in range(1, len(cleaner_lines)):
            if self.is_lowercase_letter_or_comma(cleaner_lines[i][0]):
                cleaner_lines[i - 1] += " " + cleaner_lines.pop(i)
        return cleaner_lines

    def create_word_list_from_text(self, text: str, min_word_size: int) -> list[str]:
        """
        Creates a list of words from text.

        Args:
            text (str): The text to create the list of words from.
            min_word_size (int): The minimum size of a word.

        Returns:
            list[str]: A list of words.
        """
        return [
            word.lower()
            for word in re.findall(r"\b\w+\b", text)
            if not self.has_no_text(word) and len(word) >= min_word_size
        ]

    def translate_chunk(
        self, chunk: list[str], input_lang: str, target_lang: str, wait_time: int = 2
    ) -> list[str]:
        """
        Translates a chunk of text.

        Args:
            chunk (list[str]): The chunk of text to translate.
            input_lang (str): The input language.
            target_lang (str): The target language.
            wait_time (int): The time to wait before retrying the translation.

        Returns:
            list[str]: A list of translated words.
        """
        translated_chunk = []
        for attempt in range(2):
            try:
                translated_chunk = self.translate_text(chunk, input_lang, target_lang)
                break
            except ScriptVocab.ExternalTranslationError as e:
                if attempt < 1:
                    print(f"Translation failed. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise ScriptVocab.ExternalTranslationError(
                        f"Translation failed, error: {e}\nTry again later."
                    ) from e
        return translated_chunk

    def translate_text(self, chunk: list[str], input_lang: str, target_lang: str) -> list[str]:
        """
        Translates text using the translators module.

        Args:
            chunk (list[str]): The chunk of text to translate.
            input_lang (str): The input language.
            target_lang (str): The target language.

        Returns:
            list[str]: A list of translated words.
        """
        translated_chunk = []
        if self.is_internet_available():
            try:
                translated_chunk = str(
                    GoogleTranslator(
                        source=input_lang, target=target_lang
                    ).translate("\n".join(chunk))
                ).split("\n")
                return translated_chunk
            except Exception as e:
                raise ScriptVocab.ExternalTranslationError("Translation failed") from e
        print("You are offline, using offline translation")
        for _ in chunk:
            translated_chunk.append("placeholder")
        return translated_chunk

    def convert_to_chunks(self, words_list: list[str], chunk_size: int) -> list[list[str]]:
        """
        Converts a list of words into chunks.

        Args:
            words_list (list[str]): The list of words to convert.
            chunk_size (int): The size of each chunk.

        Returns:
            list[list[str]]: A list of chunks.
        """
        return [words_list[i : i + chunk_size] for i in range(0, len(words_list), chunk_size)]

    def translate_dictionary(
        self,
        dictionary: dict[str, int],
        source_language: str,
        target_language: str,
        chunk_size: int,
    ) -> dict[str, str]:
        """
        Translates a dictionary of words.

        Args:
            dictionary (dict[str, int]): The dictionary of words to translate.
            source_language (str): The source language.
            target_language (str): The target language.
            chunk_size (int): The size of each chunk.

        Returns:
            dict[str, str]: A dictionary of translated words.
        """
        translated_dict: dict[str, str] = {}
        chunks = self.convert_to_chunks(list(dictionary.keys()), chunk_size)
        # for chunk in chunks:
        #     translated_chunk = self.translate_chunk(
        #         chunk, source_language, target_language
        #     )
        #     for index, value in enumerate(chunk):
        #         translated_dict[value] = translated_chunk[index]
        # return translated_dict

        for chunk in chunks:
            print(f"Translating chunk {chunks.index(chunk) + 1}")
            translated_words = self.translate_chunk(chunk, source_language, target_language)
            translated_dict.update(dict(zip(chunk, translated_words)))
            time.sleep(2)  # rate limiter
        return translated_dict

    def create_dictionary(self, words, min_appearance):
        """
        Create a dictionary of words and their counts from a list of words.

        Args:
            words (list):
                A list of words to count.
            min_appearance (int):
                The minimum number of times a word must appear to be included in the dictionary.

        Returns:
            dict: A dictionary of words and their counts, sorted by count in descending order.
        """
        word_count = Counter(words)
        word_counts = {word: count for word, count in word_count.items() if count >= min_appearance}
        return dict(sorted(word_counts.items(), key=lambda item: item[1], reverse=True))

    def run(self):
        """
        Runs the script, creating a dictionary of words and their counts,
        translating the dictionary, and appending the results to the output list.
        """
        words_dict: dict[str, int] = self.create_dictionary(
            self.all_words, self.config.min_appearance
        )
        print(f"Found {len(words_dict)} unique words")

        translated_dict = self.translate_dictionary(
            words_dict,
            self.config.subs_language,
            self.config.target_language,
            CHUNK_SIZE,
        )

        for word, count in words_dict.items():
            translation = translated_dict.get(word, "")
            self.output.append(f"{count}, {word}, {translation}")

    def save_output_to_file(self, output_file):
        """
        Saves the output of the script to a file.

        Args:
            output_file (str): The path to the output file.

        Returns:
            None
        """
        with open(output_file, "w", encoding="UTF-8") as f:
            if len(self.output) > 0:
                f.write("Count, Word, Translation\n")
                for line in self.output:
                    f.write(line + "\n")
        print(f"Output saved to {output_file}")

    def get_output_as_json(self):
        """
        Converts the output of the ScriptVocab program to a dictionary in JSON format.

        Returns:
            A list of entries, where each entry represents a.
            Each entry has the following keys:
                - "occurrences": the number of times the word appears in the input file
                - "original_text": the original word in the input file
                - "translated_text": the translated word in the output file
        """
        response = []
        for line in self.output:
            line_items = line.split(",")
            if len(line_items) != 3:
                print(f"Error: Invalid number of items in line: {line}")
                return None

            occurrences = line_items[0].strip()
            original_text = line_items[1].strip()
            translated_text = line_items[2].strip()

            obj = {
                "occurrences": occurrences,
                "original_text": original_text,
                "translated_text": translated_text,
            }
            response.append(obj)
        return response

    class ExternalTranslationError(Exception):
        """
        An exception to handle external translation errors.
        """
