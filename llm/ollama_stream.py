import requests
import json

def stream_ai(prompt: str):
    url = "http://localhost:11434/api/generate"

    system_prompt = "You are Jarvis, a helpful AI assistant. Answer questions directly and concisely."

    payload = {
        "model": "llama3",
        "prompt": f"{system_prompt} {prompt}",
        "stream": True
    }

    with requests.post(url, json=payload, stream=True) as r:
        for line in r.iter_lines():
            if not line:
                continue
            data = json.loads(line.decode("utf-8"))

            if "response" in data:
                yield data["response"]
