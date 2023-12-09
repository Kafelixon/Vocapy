[![Codacy Badge](https://app.codacy.com/project/badge/Grade/7744bddf5a4b45ae918776a5137cd0ce)](https://www.codacy.com/gh/Kafelixon/Vocapy/dashboard?utm_source=github.com\&utm_medium=referral\&utm_content=Kafelixon/Vocapy\&utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/7744bddf5a4b45ae918776a5137cd0ce)](https://app.codacy.com/gh/Kafelixon/Vocapy/dashboard?utm_source=gh\&utm_medium=referral\&utm_content=\&utm_campaign=Badge_coverage)
[![CodeFactor](https://www.codefactor.io/repository/github/kafelixon/webwatchnotify/badge)](https://www.codefactor.io/repository/github/kafelixon/webwatchnotify)

# Vocapy

Vocapy is a Python application designed to help language learners boost their vocabulary before watching a movie or TV series. The application processes the script of the media, counts the frequency of each word, and translates the most used words from the script's original language to the learner's target language. The output is a handy vocabulary list to study, which can help learners understand more during the show.

## Getting Started

### Prerequisites

*   Python 3.8 or higher
*   pip

### Installing

1.  Clone the repository

    ```sh
    git clone https://github.com/Kafelixon/Vocapy.git
    ```

2.  Install required Python packages

    ```sh
    pip install -r requirements.txt
    ```

### Usage

Simple usage:

```sh
python3 -m cli.main filename
```

Additional help:

```sh
positional arguments:
  path                  The path to the text file or directory to process.

optional arguments:
  -h, --help            show this help message and exit
  -s SUBS_LANGUAGE, --subs_language SUBS_LANGUAGE
                        The language of the subtitles. Default is 'auto'.
  -t TARGET_LANGUAGE, --target_language TARGET_LANGUAGE
                        The target language for the translation. Default is 'en'.
  -o OUTPUT, --output OUTPUT
                        The name for the output file. Default is 'output.txt'.
  -i INPUT_EXTENSION, --input_extension INPUT_EXTENSION
                        The extension of the input files to process. Default is 'txt'.
  -w MIN_WORD_SIZE, --min_word_size MIN_WORD_SIZE
                        Minimum word size to be included in the output.
  -m MIN_APPEARANCE, --min_appearance MIN_APPEARANCE
                        The minimum times a word should appear to be included. Default is 4.
  -e ENCODING, --encoding ENCODING
                        The encoding of the text file. Default is 'utf-8'. If you see a lot of [?]s replacing characters,
                        try 'cp1252'.
```

## Features to be added

*   Add dictionary definitions to words in output

*   Frontend for API

## Authors

*   Peter Kafel

## License

This project is licensed under the MIT License.
