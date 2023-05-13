import argparse
import re
import translators as ts
from collections import Counter


def is_time_stamp(line: str) -> bool:
    """
    Checks if a line starts with a timestamp.

    Args: line (str): The line to check.

    Returns: bool: True if the line starts with a timestamp, False otherwise.
    """
    return line[:2].isnumeric() and line[2] == ':'


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


def clean_up(lines: list) -> list:
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
            new_lines[-1] = new_lines[-1].strip() + ' ' + line
        else:
            # append line
            new_lines.append(re.sub('<.*?>', '', line))
    return new_lines


def translate_dictionary(input_dict: dict, input_lang: str, target_lang: str) -> dict:
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
    words = list(input_dict.keys())
    text = "\n".join(words)

    try:
        output = ts.translate_text(
            text,
            translator='bing',
            from_language=input_lang,
            to_language=target_lang
        )
    except Exception as e:
        print(f"Error: {e}")
        return {}

    translated_words = output.split("\n")
    translated_dict = {key: value for key,
                       value in zip(words, translated_words)}

    return translated_dict


def create_dictionary(words: list, min_appearance: int) -> dict:
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
    word_counts = Counter(words)

    # Filter words that appear at least min_appearance times
    word_counts = {
        word: count
        for word, count in word_counts.items()
        if count >= min_appearance
    }

    # Sort the dictionary by count in descending order
    words_dict = dict(sorted(word_counts.items(),
                      key=lambda item: item[1], reverse=True))

    return words_dict


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

    file_name = args.filename
    subs_language = args.subs_language
    target_language = args.target_language
    output_extension = args.output_extension
    min_appearance = args.min_appearance
    file_encoding = args.encoding

    # Open, read and clean up the file
    with open(file_name, encoding=file_encoding, errors='replace') as f:
        lines = f.readlines()
    new_lines = clean_up(lines)

    # Join the cleaned up lines into a single string
    text = ' '.join(new_lines)

    # Convert the text to lowercase and split it into words
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)

    # Create a dictionary of word counts and translate the words
    words_dict = create_dictionary(words, min_appearance)
    translated_dict = translate_dictionary(
        words_dict, subs_language, target_language)

    # Write the word counts and translations to a new file
    new_file_name = f"Dictionary [{file_name[:-4]}].{output_extension}"
    with open(new_file_name, 'w') as f:
        f.write(f"Count, Word, Translation\n")
        for word in words_dict:
            count = str(words_dict[word])
            f.write(f"{count}, {word}, {translated_dict[word]}\n")


if __name__ == '__main__':
    main()
