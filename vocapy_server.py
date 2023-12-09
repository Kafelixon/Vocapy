"""
This module contains a FastAPI server that provides an endpoint 
for translating text from one language to another using Vocapy.

The server provides a POST endpoint at /translate that accepts the following parameters:
- text: Text to translate.
- file: File containing text to translate.
- subs_language: Language of the text to translate.
- target_language: Language to translate the text to.
- min_word_size: Minimum size of a word to be included in the translation.
- min_appearance: Minimum number of times a word must appear to be included in the translation.

The endpoint returns a JSON response containing the translated text.
"""

from typing import Annotated

from fastapi import FastAPI, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from vocapy import Vocapy, VocapyConfig

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/translate")
async def translate_text(
    text: Annotated[str, Form()] = "",
    file: UploadFile | None = None,
    subs_language: Annotated[str, Form()] = "auto",
    target_language: Annotated[str, Form()] = "en",
    min_word_size: Annotated[int, Form()] = 2,
    min_appearance: Annotated[int, Form()] = 1,
):
    """
    Translates text from one language to another using Vocapy.

    Args:
        text (Annotated[str, Form()], optional): Defaults to "".
            Text to translate.
        file (UploadFile | None, optional): Defaults to None.
            File containing text to translate.
        subs_language (Annotated[str, Form()], optional): Defaults to "auto".
            Language of the text to translate.
        target_language (Annotated[str, Form()], optional): Defaults to "en".
            Language to translate the text to.
        min_word_size (Annotated[int, Form()], optional): Defaults to 2.
            Minimum size of a word to be included in the translation.
        min_appearance (Annotated[int, Form()], optional): Defaults to 1.
            Minimum number of times a word must appear to be included in the translation.

    Raises:
        ValueError: If no text or file is provided.

    Returns:
        JSONResponse: JSON response containing the translated text.
    """
    config = VocapyConfig(
        subs_language=subs_language,
        target_language=target_language,
        min_word_size=min_word_size,
        min_appearance=min_appearance,
    )
    if file:
        content = await file.read()
        text = str(content)
    print(f"Config {subs_language} {target_language} {min_word_size} {min_appearance}")
    if not text:
        raise ValueError("No text or file provided")
    return process_text(config, text)


def process_text(config: VocapyConfig, text: str):
    """
    Processes the text using Vocapy.

    Args:
        config (VocapyConfig): Configuration for Vocapy.
        text (str): Text to process.

    Returns:
        JSONResponse: JSON response containing the processed text.
    """
    with Vocapy(config) as vocapy:
        vocapy.input_text(text)
        print("Running script", vocapy.all_words)
        vocapy.run()
        response = vocapy.get_output_as_json()
    return JSONResponse(content=response, media_type="application/json; charset=utf-8")
