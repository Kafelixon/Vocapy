from fastapi import FastAPI
from fastapi.responses import JSONResponse

from script_vocab.script_vocab import ScriptVocab, scriptVocabConfig

app = FastAPI()


@app.get("/translate_text/{text}")
async def translate_text(text: str):
    config = scriptVocabConfig(
        subs_language="auto", target_language="ja", min_word_size=2, min_appearance=1
    )
    with ScriptVocab(config) as script_vocab:
        script_vocab.input_text(text)
        script_vocab.run()
        response = script_vocab.get_output_as_json()
    
    return JSONResponse(content=response, media_type="application/json; charset=utf-8")
