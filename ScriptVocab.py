import argparse
import glob
import re
from collections import Counter
from pathlib import Path
import time
import translators as ts


class ScriptVocab:
    def __init__(self, args):
        self.path = args["path"]
        self.subs_language = args["subs_language"]
        self.target_language = args["target_language"]
        self.output = args["output"]
        self.input_extension = args["input_extension"]
        self.min_word_size = args["min_word_size"]
        self.min_appearance = args["min_appearance"]
        self.encoding = args["encoding"]

        self.filenames = self.create_list_of_files_to_process()
        self.all_words = []


    def create_list_of_files_to_process(self):
        path = Path(self.path)
        if path.is_file():
            return [path]
        if path.is_dir():
            return glob.glob(f"{path}/*.{self.input_extension}")

        raise FileNotFoundError(
            f"Error: The path {path} does not exist or is not a file or directory.")

    def process_files(self):
        print(f"Processing {len(self.filenames)} files...")
        for filename in self.filenames:
            with open(filename, encoding=self.encoding, errors='replace') as f:
                lines = f.readlines()
            text = ' '.join(self.clean_up(lines)).lower()
            print(text)
            words = self.create_word_list_from_text(text, self.min_word_size)
            print(f"Found {len(words)} words in {filename}")
            self.all_words.extend(words)

    def has_no_text(self, line):
        line = line.strip()
        is_empty_or_numeric = not line or line.isnumeric()
        matches_timestamp = bool(re.match(r'^\d{1,2}:\d{2}:\d{2},\d{3}', line))
        contains_no_letters = not bool(re.search('[a-zA-Z]', line))
        return is_empty_or_numeric or matches_timestamp or contains_no_letters

    def is_lowercase_letter_or_comma(self, char: str):
        return char.isalpha() and char.lower() == char or char == ','

    def clean_up(self, lines):
        new_lines = [re.sub('<.*?>', '', line)
                     for line in lines[1:] if not self.has_no_text(line)]
        for i in range(1, len(new_lines)):
            if self.is_lowercase_letter_or_comma(new_lines[i][0]):
                new_lines[i-1] += ' ' + new_lines.pop(i)
        return new_lines

    def create_word_list_from_text(self, text, min_word_size):
        return [word for word in re.findall(r'\b\w+\b', text) if not self.has_no_text(word) and len(word) > min_word_size]

    def translate_chunk(self, chunk, input_lang, target_lang, wait_time=2):
        for attempt in range(2):
            print(f"Attempt {attempt + 1}...")
            try:
                return ts.translate_text("\n".join(chunk),
                                         translator='bing',
                                         from_language=input_lang,
                                         to_language=target_lang).split("\n")
            except Exception as e:
                if attempt < 1:
                    print(
                        f"Translation failed. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise Exception(
                        f"Translation failed, error: {e}\nTry again later.")

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
            chunk = words[i:i+chunk_size]
            print(
                f"Translating chunk {i // chunk_size + 1} of {num_chunks}...")
            translated_words = self.translate_chunk(
                chunk, source_language, target_language, wait_time)
            translated_dict.update(dict(zip(chunk, translated_words)))

        return translated_dict

    def create_dictionary(self, words, min_appearance):
        word_count = Counter(words)
        word_counts = {word: count for word,
                       count in word_count.items() if count >= min_appearance}
        return dict(sorted(word_counts.items(), key=lambda item: item[1], reverse=True))

    def run(self):
        self.process_files()
        print(f"Found {len(self.all_words)} words in total.")
        words_dict = self.create_dictionary(
            self.all_words, self.min_appearance)
        print(
            f"Found {len(words_dict)} unique words appearing at least {self.min_appearance} times.")

        translated_dict = self.translate_dictionary(
            words_dict, self.subs_language, self.target_language)

        with open(self.output, 'w') as f:
            f.write("Count, Word, Translation\n")
            for word, count in words_dict.items():
                translation = translated_dict.get(word, '')
                f.write(f"{count}, {word}, {translation}\n")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "path", help="The path to the text file or directory to process.")
    parser.add_argument("-s", "--subs_language", default='auto',
                        help="The language of the subtitles. Default is 'auto'.")
    parser.add_argument("-t", "--target_language", default='en',
                        help="The target language for the translation. Default is 'en'.")
    parser.add_argument("-o", "--output", default='output.txt',
                        help="The name for the output file. Default is 'output.txt'.")
    parser.add_argument("-i", "--input_extension", default='txt',
                        help="The extension of the input files to process. Default is 'txt'.")
    parser.add_argument("-w", "--min_word_size", type=int, default=1,
                        help="Minimum word size to be included in the output.")
    parser.add_argument("-m", "--min_appearance", type=int, default=4,
                        help="The minimum times a word should appear to be included. Default is 4.")
    parser.add_argument("-e", "--encoding", default='utf-8',
                        help="The encoding of the text file. Default is 'utf-8'. If you see a lot of [?]s replacing characters, try 'cp1252'.")

    args = parser.parse_args()
    translator = ScriptVocab(dict(args._get_kwargs()))
    translator.run()


if __name__ == '__main__':
    main()
