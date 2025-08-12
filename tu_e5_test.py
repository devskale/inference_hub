import argparse
import os
import requests
from credgoo import get_api_key

# Set your API key
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
#api_key = get_api_key("tu")

API_BASE = "https://aqueduct.ai.datalab.tuwien.ac.at/v1"
TU_API_KEY = get_api_key("tu")

def create_embedding(model, text):
    """Send an embedding request"""
    url = f"{API_BASE}/embeddings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TU_API_KEY}"
    }
    data = {
        "model": model,
        "input": text
    }
    return requests.post(url, headers=headers, json=data, timeout=30)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TU Wien Inference Hub Client for Embeddings')
    parser.add_argument('--model', default="e5-mistral-7b", 
                        help='Model to use for embedding')
    parser.add_argument('--text', default="Hello, this is a test.", 
                        help='Text to embed')
    args = parser.parse_args()

    response = create_embedding(args.model, args.text)
    print("Status:", response.status_code)
    print("Response:", response.text)
