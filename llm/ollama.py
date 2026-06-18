import requests
import json
import config

def stream(prompt):
    r = requests.post(
        config.OLLAMA_URL,
        json={"model": config.MODEL, "prompt": prompt, "stream": True},
        stream=True
    )

    for line in r.iter_lines():
        if line:
            try:
                yield json.loads(line.decode()).get("response", "")
            except:
                pass