"""import requests
import json

# Cloudflare API Details
API_URL = "https://api.cloudflare.com/client/v4/accounts/1ee331dfd225ac49d67c521a73ca7fe8/ai/run/"
MODEL_NAME = "@cf/meta/llama-3-8b-instruct"  # Change to the model you need
API_TOKEN = "kOn01mvCkCLmI3Elu46hhLdInJo3WiZJob9NIPaj"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

data = {
    "prompt": "What is Cloudflare AI?",
    "max_tokens": 100,
    "stream": True  # Enable streaming mode
}

response = requests.post(API_URL + MODEL_NAME,
                         headers=headers, json=data, stream=True)

if response.status_code == 200:
    print("Response Stream:")
    for chunk in response.iter_lines():
        if chunk:
            print(chunk.decode("utf-8"))
else:
    print("Error:", response.status_code, response.text)

"""

import requests
import json

# Cloudflare API Details
API_URL = "https://api.cloudflare.com/client/v4/accounts/1ee331dfd225ac49d67c521a73ca7fe8/ai/run/"
MODEL_NAME = "@cf/meta/llama-3-8b-instruct"  # Change to the model you need
API_TOKEN = "kOn01mvCkCLmI3Elu46hhLdInJo3WiZJob9NIPaj"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

data = {
    "prompt": "What is Cloudflare AI?",
    "max_tokens": 100,
    "stream": True  # Enable streaming mode
}

response = requests.post(API_URL + MODEL_NAME,
                         headers=headers, json=data, stream=True)

if response.status_code == 200:
    print("Response Stream:")
    for chunk in response.iter_lines():
        if chunk:
            try:
                chunk_data = chunk.decode("utf-8").strip()
                if chunk_data.startswith("data: "):
                    # Remove "data: " prefix
                    chunk_data = chunk_data[len("data: "):]
                json_chunk = json.loads(chunk_data)  # Parse JSON
                if "response" in json_chunk:
                    print(json_chunk["response"], end="", flush=True)
            except json.JSONDecodeError:
                continue  # Ignore malformed chunks
else:
    print("Error:", response.status_code, response.text)
