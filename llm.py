import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"


def stream_llm(prompt):
    r = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": True
        },
        stream=True
    )

    full = ""

    for line in r.iter_lines():
        if line:
            try:
                data = json.loads(line.decode())
                token = data.get("response", "")
                full += token
                print(token, end="", flush=True)
                yield token
            except:
                pass

    print()