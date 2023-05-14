import argparse
import re
import translators as ts
from collections import Counter


def is_time_stamp(line: str) -> bool:
    """
    Checks if the given line starts with a timestamp.

    A timestamp is defined as a string at the start of the line in the format 'HH:MM:SS,MS', 
    where HH represents hours, MM represents minutes, SS represents seconds, and MS represents milliseconds.

    Args: line (str): The line to check.

    Returns: bool: True if the line starts with a timestamp, False otherwise.
    """
    pattern = r'^\d{1,2}:\d{2}:\d{2},\d{3}'
    return bool(re.match(pattern, line))


def has_letters(line: str) -> bool:
    """
    Checks if a line contains any letters.

    Args: line (str): The line to check.

    Returns: bool: True if the line contains any letters, False otherwise.
    """
    return bool(re.search('[a-zA-Z]', line))


def has_no_text(line: str) -> bool:
    """
    Checks if a line is empty, numeric, a timestamp, or contains no letters.

    Args: line (str): The line to check.

    Returns: bool: True if the line is empty, numeric, a timestamp, or contains no letters. False otherwise.
    """
    line = line.strip()
    return not line or line.isnumeric() or is_time_stamp(line) or not has_letters(line)


def is_lowercase_letter_or_comma(char: str) -> bool:
    """
    Checks if a character is a lowercase letter or a comma.

    Args: char (str): The character to check.

    Returns: bool: True if the character is a lowercase letter or a comma, False otherwise.
    """
    return char.isalpha() and char.lower() == char or char == ','


def clean_up(lines: list[str]) -> list[str]:
    """
    Cleans up a list of lines by removing non-text lines and combining text broken into multiple lines.

    Args: lines (list): The list of lines to clean up.

    Returns: list: The cleaned up list of lines.
    """
    new_lines = []
    for line in lines[1:]:
        if has_no_text(line):
            continue
        elif new_lines and is_lowercase_letter_or_comma(line[0]):
            # combine with previous line
            new_lines[-1] = f"{new_lines[-1].strip()} {line}"
        else:
            # append line
            new_lines.append(re.sub('<.*?>', '', line))
    return new_lines


def translate_dictionary(input_dict: dict, input_lang: str, target_lang: str) -> dict[str, str]:
    """
    Translates the keys of a dictionary from Spanish to a specified language 
    using a translation service. The translated words become the values in 
    the returned dictionary.

    Args:
        input_dict (dict): The dictionary to translate. Only the keys are translated.
        dest (str, optional): The destination language (ISO 639-1 code). 
                              Defaults to "en" (English).

    Returns:
        dict: A dictionary with the original words as keys and translated words as values.
    """
    words: list[str] = list(input_dict.keys())
    text: str = "\n".join(words)

    try:
        output: str = ts.translate_text(
            text,
            translator='bing',
            from_language=input_lang,
            to_language=target_lang
        )
    except Exception as e:
        print(f"Error: {e}")
        return {}

    translated_words: list[str] = output.split("\n")
    return {key: value for key, value in zip(words, translated_words)}


def create_dictionary(words: list, min_appearance: int) -> dict[str, int]:
    """
    Creates a dictionary from a list of words. Each unique word that appears 
    at least a certain number of times in the list becomes a key in the dictionary. 
    The values are the counts of each word. The dictionary is sorted in descending order 
    by count.

    Args:
        words (list): The list of words to count.
        min_appearance (int): The minimum number of appearances for a word to be included 
        in the dictionary.

    Returns:
        dict: A dictionary with words as keys and counts as values, sorted 
        in descending order by count.
    """
    # Count word occurrences
    word_counts: dict[str, int] = Counter(words)

    # Filter words that appear at least min_appearance times
    word_counts = {
        word: count
        for word, count in word_counts.items()
        if count >= min_appearance
    }

    # Return sorted dictionary by count in descending order
    return dict(sorted(word_counts.items(), key=lambda item: item[1], reverse=True))


def create_word_list_from_text(text: str) -> list[str]:
    """
    Extracts words from the given text and returns them as a list.

    Words are defined as sequences of alphanumeric characters. Non-word 
    lines (e.g. timestamps, lines with no alphabetic characters) are ignored.

    Args: text (str): The text to extract words from.

    Returns: list[str]: The list of words extracted from the text.
    """
    # Use list comprehension to generate the word list directly
    return [word for word in re.findall(r'\b\w+\b', text) if not has_no_text(word)]


def make_output_filename(filename: str, output_extension: str) -> str:
    """
    Creates an output filename by removing the original extension and 
    appending a new one.

    Args: filename (str): The original filename. output_extension (str): The new extension to append.

    Returns: str: The output filename.
    """
    # Strip the extension, add the prefix and the new extension
    return f"Dictionary [{filename.rsplit('.', 1)[0]}].{output_extension}"


def main():
    """
    The main function to clean up a text file, count the words, translate them, 
    and write the results to a new file.
    """

    # Initialize the ArgumentParser object
    parser = argparse.ArgumentParser()

    # Add arguments
    parser.add_argument(
        "filename", help="The name of the text file to process.")
    parser.add_argument("-s", "--subs_language", default='auto',
                        help="The language of the subtitles. Default is 'auto'.")
    parser.add_argument("-t", "--target_language", default='en',
                        help="The target language for the translation. Default is 'en'.")
    parser.add_argument("-o", "--output_extension", default='txt',
                        help="The extension for the output file. Default is 'txt'.")
    parser.add_argument("-m", "--min_appearance", type=int, default=4,
                        help="The minimum times a word should appear to be included. Default is 4.")
    parser.add_argument("-e", "--encoding", default='utf-8',
                        help="The encoding of the text file. Default is 'utf-8'. If you see a lot of [?]s replacing characters, try 'cp1252'.")

    # Parse the arguments
    args = parser.parse_args()

    # Open and read the file
    with open(args.filename, encoding=args.encoding, errors='replace') as f:
        lines: list[str] = f.readlines()

    # Combine cleaned lines into a single, lowercase string for easier text processing
    text: str = ' '.join(clean_up(lines)).lower()

    words = create_word_list_from_text(text)

    # Create a dictionary of word counts and translate the words
    words_dict = create_dictionary(words, args.min_appearance)
    translated_dict = translate_dictionary(
        words_dict, args.subs_language, args.target_language)

    # Write the word counts and translations to a new file
    output_filename = make_output_filename(
        args.filename, args.output_extension)
    with open(output_filename, 'w') as f:
        f.write(f"Count, Word, Translation\n")
        for word in words_dict:
            count = str(words_dict[word])
            translation: str = translated_dict.get(word, '')
            f.write(f"{count}, {word}, {translation}\n")


if __name__ == '__main__':
    main()
