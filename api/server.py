from typing import Annotated

from fastapi import FastAPI, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from script_vocab.script_vocab import ScriptVocab, ScriptVocabConfig

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
    min_appearance: Annotated[int, Form()] = 1
):
    config = ScriptVocabConfig(
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

def process_text(config: ScriptVocabConfig, text: str):
    with ScriptVocab(config) as script_vocab:
        script_vocab.input_text(text)
        print("Running script", script_vocab.all_words)
        script_vocab.run()
        response = script_vocab.get_output_as_json()
    return JSONResponse(content=response, media_type="application/json; charset=utf-8")
