from fastapi import FastAPI, UploadFile, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from script_vocab.script_vocab import ScriptVocab, scriptVocabConfig

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_config(
    subs_language: str = Query("auto", description="Input language"),
    target_language: str = Query("en", description="Target language"),
    min_word_size: int = Query(2, description="Minimum word size"),
    min_appearance: int = Query(1, description="Minimum word appearance"),
) -> scriptVocabConfig:
    return scriptVocabConfig(
        subs_language=subs_language,
        target_language=target_language,
        min_word_size=min_word_size,
        min_appearance=min_appearance,
    )


@app.get("/translate_text")
async def translate_text(
    text: str,
    config: scriptVocabConfig = Depends(create_config),
):
    return process_text(config, text)


@app.post("/translate_file/")
async def translate_file(
    file: UploadFile,
    config: scriptVocabConfig = Depends(create_config),
):
    content = await file.read()
    return process_text(config, str(content))


def process_text(config: scriptVocabConfig, text: str):
    with ScriptVocab(config) as script_vocab:
        print(f"Translating e: {text}")
        script_vocab.input_text(text)
        print("Running script", script_vocab.all_words)
        script_vocab.run()
        response = script_vocab.get_output_as_json()
    return JSONResponse(content=response, media_type="application/json; charset=utf-8")
