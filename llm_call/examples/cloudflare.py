import requests
import json
from credgoo import get_api_key
# Cloudflare API Details
ACCOUNT_ID = "1ee331dfd225ac49d67c521a73ca7fe8"
API_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/"
MODEL_NAME = "@cf/meta/llama-3-8b-instruct"  # Change to the model you need
API_TOKEN = get_api_key("cloudflare")

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
