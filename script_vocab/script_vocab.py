import glob
import re
import time
from collections import Counter
from pathlib import Path
import translators as ts

CHUNK_SIZE = 100

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
        self.all_words: list[str] = []
        self.output: list[str] = []
        print(vars(self.config))

    def __enter__(self):
        return self
  
    def __exit__(self, exc_type, exc_value, traceback):
        print("Exiting")
        self.dupa = 1

    def input_text(self, text: str):
        words = self.create_word_list_from_text(text, self.config.min_word_size)
        print(f"Found {len(words)} words in input text.")
        self.all_words.extend(words)

    def input_files(self, path: str, input_extension: str, encoding: str):
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

    def process_files(self, file_paths, encoding):
        for file_path in file_paths:
            with open(file_path, "r", encoding=encoding) as f:
                lines = f.readlines()
                print(f"Lines: {lines}")
                cleaned_lines = self.clean_up(lines)
                print(f"Cleaned lines: {cleaned_lines}")
                for line in cleaned_lines:
                    words = self.create_word_list_from_text(line, self.config.min_word_size)
                    print(f"Words: {words}")
                    self.all_words.extend(words)

    def has_no_text(self, line) -> bool:
        line = line.strip()
        is_empty_or_numeric = not line or line.isnumeric()
        matches_timestamp = bool(re.match(r"^\d{1,2}:\d{2}:\d{2},\d{3}", line))
        contains_no_letters = not bool(re.search("[a-zA-Z]", line))
        return is_empty_or_numeric or matches_timestamp or contains_no_letters

    def is_lowercase_letter_or_comma(self, char: str):
        return char.isalpha() and char.lower() == char or char == ","

    def clean_up(self, lines):
        cleaner_lines = [
            re.sub("<.*?>", "", line).rstrip()
            for line in lines
            if not self.has_no_text(line)
        ]
        for i in range(1, len(cleaner_lines)):
            if self.is_lowercase_letter_or_comma(cleaner_lines[i][0]):
                cleaner_lines[i - 1] += " " + cleaner_lines.pop(i)
        return cleaner_lines

    def create_word_list_from_text(self, text, min_word_size):
        return [
            word.lower()
            for word in re.findall(r"\b\w+\b", text)
            if not self.has_no_text(word) and len(word) >= min_word_size
        ]

    def translate_chunk(self, chunk, input_lang, target_lang, wait_time=2) -> list[str]:
        translated_chunk = []
        for attempt in range(2):
            print(f"Attempt {attempt + 1}...")
            try:
                translated_chunk = str(ts.translate_text(
                    "\n".join(chunk),
                    translator="bing",
                    from_language=input_lang,
                    to_language=target_lang,
                )).split("\n")
            except Exception as e:
                if attempt < 1:
                    print(f"Translation failed. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Translation failed, error: {e}\nTry again later.")
        return translated_chunk

    def chunks(self, list:list[str], chunk_size:int):
        for i in range(0, len(list), chunk_size):
            yield list[i : i + chunk_size]

    def translate_dictionary(self, dictionary: dict[str,int], source_language, target_language, chunk_size):
        translated_dict: dict[str,str] = {}
        for chunk in self.chunks(list(dictionary.keys()), chunk_size):
            translated_words = self.translate_chunk(chunk, source_language, target_language)
            translated_dict.update(dict(zip(chunk, translated_words)))
            time.sleep(2)  # rate limiter
        return translated_dict

    def create_dictionary(self, words, min_appearance):
        word_count = Counter(words)
        word_counts = {
            word: count for word, count in word_count.items() if count >= min_appearance
        }
        return dict(sorted(word_counts.items(), key=lambda item: item[1], reverse=True))

    def run(self):
        words_dict: dict[str,int] = self.create_dictionary(self.all_words, self.config.min_appearance)
        print(f"Found {len(words_dict)} unique words")

        translated_dict = self.translate_dictionary(
            words_dict, self.config.subs_language, self.config.target_language, CHUNK_SIZE
        )

        for word, count in words_dict.items():
            translation = translated_dict.get(word, "")
            self.output.append(f"{count}, {word}, {translation}")

    def save_output_to_file(self, output_file):
        with open(output_file, "w") as f:
            if len(self.output) > 0:
                f.write("Count, Word, Translation\n")
                for line in self.output:
                    f.write(line + "\n")
    
    def get_output_as_json(self):
        response = []
        for line in self.output:
            line_items = line.split(",")
            if len(line_items) != 3:
                print(f"Error occurred while parsing output: Invalid number of items in line: {line}")
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