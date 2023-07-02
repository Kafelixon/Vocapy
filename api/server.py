from fastapi import FastAPI
from fastapi.responses import JSONResponse

from script_vocab.script_vocab import ScriptVocab, scriptVocabConfig

app = FastAPI()

config = scriptVocabConfig(
    subs_language="auto", target_language="pl", min_word_size=2, min_appearance=1
)
script_vocab = ScriptVocab(config)


@app.get("/translate_text/{text}")
async def translate_text(text: str):
    script_vocab.input_text(text)
    script_vocab.run()
    response = []
    for line in script_vocab.output:
        print(line)
        occurrences, original_text, translated_text = [
            item.strip() for item in line.split(",")
        ]

        obj = {
            "occurrences": occurrences,
            "original_text": original_text,
            "translated_text": translated_text,
        }
        response.append(obj)
    return JSONResponse(content=response, media_type="application/json; charset=utf-8")
