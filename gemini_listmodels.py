import google.generativeai as genai
import os
from dotenv import load_dotenv
from credgoo import get_api_key

# Set your API key
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
api_key = get_api_key("gemini")


def list_available_gemini_models(api_key: str = api_key):
    """Lists all supported Gemini models from the Google Generative AI API."""

    genai.configure(api_key=api_key)
    models = genai.list_models()

    print("Available Gemini Models:\n")
    for model in models:
        if "gemini" in model.name.lower():
            print(f"  - {model.name} : {model.description}")


if __name__ == "__main__":
    list_available_gemini_models(api_key)
