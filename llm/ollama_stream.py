import requests
import json

def stream_ai(prompt: str):
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": True
    }

    with requests.post(url, json=payload, stream=True) as r:
        for line in r.iter_lines():
            if not line:
                continue
            data = json.loads(line.decode("utf-8"))
            if "response" in data:
                yield data["response"]