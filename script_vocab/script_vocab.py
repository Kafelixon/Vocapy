import glob
import re
import time
from collections import Counter
from pathlib import Path
import translators as ts


class scriptVocabConfig:
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
    def __init__(self, config: scriptVocabConfig):
        self.config = config
        self.all_words = []
        print(vars(self.config))

    def input_text(self, text: str):
        text = text.lower()
        words = self.create_word_list_from_text(text, self.config.min_word_size)
        print(f"Found {len(words)} words in input text.")
        self.all_words.extend(words)

    def input_files(self, path: Path, input_extension: str, encoding: str):
        if path.is_file():
            filenames = [path]
        elif path.is_dir():
            filenames = glob.glob(f"{path}/*.{input_extension}")
        else:
            raise FileNotFoundError(
                f"Error: The path {path} does not exist or is not a file or directory."
            )
        self.process_files(filenames, encoding)

    def process_files(self, filenames, encoding):
        print(f"Processing {len(filenames)} files...")
        for filename in filenames:
            with open(filename, encoding=encoding, errors="replace") as f:
                lines = f.readlines()
            text = " ".join(self.clean_up(lines)).lower()
            print(text)
            words = self.create_word_list_from_text(text, self.config.min_word_size)
            print(f"Found {len(words)} words in {filename}")
            self.all_words.extend(words)
        print(f"Found {len(self.all_words)} words in total.")

    def has_no_text(self, line) -> bool:
        line = line.strip()
        is_empty_or_numeric = not line or line.isnumeric()
        matches_timestamp = bool(re.match(r"^\d{1,2}:\d{2}:\d{2},\d{3}", line))
        contains_no_letters = not bool(re.search("[a-zA-Z]", line))
        return is_empty_or_numeric or matches_timestamp or contains_no_letters

    def is_lowercase_letter_or_comma(self, char: str):
        return char.isalpha() and char.lower() == char or char == ","

    def clean_up(self, lines):
        new_lines = [
            re.sub("<.*?>", "", line)
            for line in lines[1:]
            if not self.has_no_text(line)
        ]
        for i in range(1, len(new_lines)):
            if self.is_lowercase_letter_or_comma(new_lines[i][0]):
                new_lines[i - 1] += " " + new_lines.pop(i)
        return new_lines

    def create_word_list_from_text(self, text, min_word_size):
        return [
            word
            for word in re.findall(r"\b\w+\b", text)
            if not self.has_no_text(word) and len(word) > min_word_size
        ]

    def translate_chunk(self, chunk, input_lang, target_lang, wait_time=2):
        for attempt in range(2):
            print(f"Attempt {attempt + 1}...")
            try:
                return ts.translate_text(
                    "\n".join(chunk),
                    translator="bing",
                    from_language=input_lang,
                    to_language=target_lang,
                ).split("\n")
            except Exception as e:
                if attempt < 1:
                    print(f"Translation failed. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Translation failed, error: {e}\nTry again later.")

    def translate_dictionary(self, dictionary, source_language, target_language):
        words = list(dictionary.keys())
        translated_dict = {}
        chunk_size = 100
        wait_time = 2

        num_chunks = len(words) // chunk_size + 1
        for i in range(0, len(words), chunk_size):
            if i > 0:
                print(f"Waiting {wait_time} seconds to avoid rate limiting...")
                time.sleep(wait_time)
            chunk = words[i : i + chunk_size]
            print(f"Translating chunk {i // chunk_size + 1} of {num_chunks}...")
            translated_words = self.translate_chunk(
                chunk, source_language, target_language, wait_time
            )
            translated_dict.update(dict(zip(chunk, translated_words)))

        return translated_dict

    def create_dictionary(self, words, min_appearance):
        word_count = Counter(words)
        word_counts = {
            word: count for word, count in word_count.items() if count >= min_appearance
        }
        return dict(sorted(word_counts.items(), key=lambda item: item[1], reverse=True))

    def run(self):
        words_dict = self.create_dictionary(self.all_words, self.config.min_appearance)
        print(
            f"Found {len(words_dict)} unique words appearing at least {self.config.min_appearance} times."
        )

        translated_dict = self.translate_dictionary(
            words_dict, self.config.subs_language, self.config.target_language
        )

        self.output = []
        for word, count in words_dict.items():
            translation = translated_dict.get(word, "")
            self.output.append(f"{count}, {word}, {translation}")

    def save_output_to_file(self, output_file):
        with open(output_file, "w") as f:
            f.write("Count, Word, Translation\n")
            for line in self.output:
                f.write(line + "\n")
