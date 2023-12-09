import argparse
from vocapy import Vocapy, VocapyConfig


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("path", help="The path to the text file or directory to process.")
    parser.add_argument(
        "-s",
        "--subs_language",
        default="auto",
        help="The language of the subtitles. Default is 'auto'.",
    )
    parser.add_argument(
        "-t",
        "--target_language",
        default="en",
        help="The target language for the translation. Default is 'en'.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="output.txt",
        help="The name for the output file. Default is 'output.txt'.",
    )
    parser.add_argument(
        "-i",
        "--input_extension",
        default="txt",
        help="The extension of the input files to process. Default is 'txt'.",
    )
    parser.add_argument(
        "-w",
        "--min_word_size",
        type=int,
        default=1,
        help="Minimum word size to be included in the output.",
    )
    parser.add_argument(
        "-m",
        "--min_appearance",
        type=int,
        default=4,
        help="The minimum times a word should appear to be included. Default is 4.",
    )
    parser.add_argument(
        "-e",
        "--encoding",
        default="utf-8",
        help="The encoding of the text file. Default is 'utf-8'.",
    )

    args = parser.parse_args()
    vocapy_config = VocapyConfig(
        subs_language=args.subs_language,
        target_language=args.target_language,
        min_word_size=args.min_word_size,
        min_appearance=args.min_appearance,
    )
    translator = Vocapy(vocapy_config)
    translator.input_files(args.path, args.input_extension, args.encoding)
    translator.run()
    translator.save_output_to_file(args.output)


if __name__ == "__main__":
    main()
