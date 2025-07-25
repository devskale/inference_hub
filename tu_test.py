import argparse
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE = "https://aqueduct.ai.datalab.tuwien.ac.at/v1"
TU_API_KEY = os.getenv("TU_API_KEY")

def list_models():
    """Get available models from /v1/models endpoint"""
    url = f"{API_BASE}/models"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TU_API_KEY}"
    }
    response = requests.get(url, headers=headers, timeout=30)
    return response.json()

def chat_completion(model, message):
    """Send a chat completion request"""
    url = f"{API_BASE}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TU_API_KEY}"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": message}]
    }
    return requests.post(url, headers=headers, json=data, timeout=30)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TU Wien Inference Hub Client')
    parser.add_argument('--models', action='store_true', help='List available models')
    parser.add_argument('--model', default="openai/RedHatAI/DeepSeek-R1-0528-quantized.w4a16", 
                        help='Model to use for chat completion')
    parser.add_argument('--message', default="Hello, DeepSeek!", 
                        help='Message to send to the model')
    args = parser.parse_args()

    if args.models:
        print("Available models:")
        models = list_models()
        for model in models.get('data', []):
            print(f"- {model['id']}")
    else:
        response = chat_completion(args.model, args.message)
        print("Status:", response.status_code)
        print("Response:", response.text)