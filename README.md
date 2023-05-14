# ScriptVocab

ScriptVocab is a Python application designed to help language learners boost their vocabulary before watching a movie or TV series. The application processes the script of the media, counts the frequency of each word, and translates the most used words from the script's original language to the learner's target language. The output is a handy vocabulary list to study, which can help learners understand more during the show.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Libraries: `re`, `translators`, `collections.Counter`

### Installing

1. Clone the repository
```sh
git clone https://github.com/Kafelixon/ScriptVocab.git
```
2. Install required Python packages
```sh
pip install translators
```

### Usage

Simple usage:
```sh
python3 ScriptVocab.py filename
```
Additional help:
```sh
positional arguments:
  filename              The name of the text file to process.

optional arguments:
  -h, --help            show this help message and exit
  -s SUBS_LANGUAGE, --subs_language SUBS_LANGUAGE
                        The language of the subtitles. Default is 'auto'.
  -t TARGET_LANGUAGE, --target_language TARGET_LANGUAGE
                        The target language for the translation. Default is 'en'.
  -o OUTPUT_EXTENSION, --output_extension OUTPUT_EXTENSION
                        The extension for the output file. Default is 'txt'.
  -m MIN_APPEARANCE, --min_appearance MIN_APPEARANCE
                        The minimum times a word should appear to be included. Default is 4.
  -e ENCODING, --encoding ENCODING
                        The encoding of the text file. Default is 'utf-8'. If you see a lot of [?]s replacing characters, try 'cp1252'.```
```

## Features to be added 

- multiple subtitle files as input 
- maybe GUI 

## Authors

- Peter Kafel

## License

This project is licensed under the MIT License.
