import argparse
from abc import ABC, abstractmethod
from huggingface_hub import InferenceClient, login
from openai import OpenAI
from getparams import load_api_credentials
import re
from ollama import AsyncClient
import asyncio

# List of document categories
DATEIKLASSEN = [
    "Angebot", "Referenzen", "Produktbeschreibung", "Zertifikat",
    "Firmenauskunft", "Finanzinformation", "Strafregisterauszug", "Versicherungsvertrag", 
    "Bestätigung", "Sonstiges"
]

# Prompts for different analysis modes
PROMPTS = {
    's': """
Basierend auf dem folgenden Inhalt, prüfe das Dokument. Erstelle Beschreibung und Dateinamen nach exakt folgendem Format. 
Das Dokument kann aufgrund des Scan Vorgangs einige Textfehler und geschwärzte textpassagen enthalten. Keine sonstigen Informationen oder Erklärungen hinzufügen:
Beschreibung: (Beschreibe kurz den Inhalt und fasse die Kernaussage zusammen. Nenne wichtige Details und Schlüsselwörter sowie den Dokumentersteller.)
Dateiname: (beschreibender Dateiname mit Endung .md)
  """,
    'k0': f"""
    Basierend auf dem folgenden Inhalt, kategorisiere den Inhalt in eine der folgenden Klassen:
    {', '.join(DATEIKLASSEN)}
    Antworte nur mit dem Namen der Klasse. Sollte keine der Klassen passen, antworte mit 'Sonstiges'.
    """,
    'k': f"""
    Basierend auf dem folgenden Inhalt, kategorisiere den Inhalt in eine Dokumentenkategorie:
    Antworte nur mit dem Namen der Kategorie.
    """
}

class ModelProvider(ABC):
    @abstractmethod
    async def setup(self):
        pass

    @abstractmethod
    async def analyze(self, content, mode):
        pass

class HuggingFaceProvider(ModelProvider):
    def __init__(self, model_id):
        self.model_id = model_id
        self.client = None

    async def setup(self):
        api_token = load_api_credentials('huggingface')
        login(api_token)
        self.client = InferenceClient(model=self.model_id)

    async def analyze(self, content, mode):
        full_prompt = f"{PROMPTS[mode]}\n\nInhalt:\n{content}\n\nAntwort:\n"
        messages = [
            {"role": "system", "content": "Du bist ein Assistent der Wiener Wohnen GmbH der OCR eingescannte Dokumente von Anbietern einer Ausschreibung analysiert."},
            {"role": "user", "content": full_prompt}
        ]
        full_response = ""
        print("Analyzing with HuggingFace (streaming response):")
        try:
            output = self.client.chat.completions.create(
                messages=messages,
                stream=True,
                max_tokens=512,
                temperature=0.01
            )
            for chunk in output:
                content = chunk.choices[0].delta.content
                if content:
                    print(content, end="", flush=True)
                    full_response += content
            print()  # New line after streaming is complete
            return full_response
        except Exception as e:
            print(f"Error during HuggingFace analysis: {e}")
            return f"Error: {str(e)}"
        

class OllamaProvider(ModelProvider):
    def __init__(self, model_name):
        self.model_name = model_name
        self.client = AsyncClient(
            #host='https://amp1.mooo.com:11444'
            host='http://localhost:11434'
            )

    async def setup(self):
        # AsyncClient doesn't require explicit setup
        pass

    async def analyze(self, content, mode):
        full_prompt = f"{PROMPTS[mode]}\n\nInhalt:\n{content}\n\nAntwort:\n"
        messages = [
            {"role": "system", "content": "Du bist ein Assistent der Wiener Wohnen GmbH und analysierst Anbieterdokumente einer Ausschreibung."},
            {"role": "user", "content": full_prompt}
        ]

        print("Analyzing with Ollama (streaming response):")
        full_response = ""
        try:
            async for part in await self.client.chat(model=self.model_name, messages=messages, stream=True):
                chunk_content = part['message']['content']
                print(chunk_content, end='', flush=True)
                full_response += chunk_content
            print()  # New line after streaming is complete
            return full_response
        except Exception as e:
            print(f"Error during Ollama analysis: {e}")
            return f"Error: {str(e)}"

class OpenAIProvider(ModelProvider):
    def __init__(self, model_name):
        self.model_name = model_name

    async def setup(self):
        api_token = load_api_credentials('openrouter')
        # Implement OpenAI setup (e.g., setting API key)
        self.client = OpenAI(
            api_key=api_token,
            base_url="https://openrouter.ai/api/v1")
        pass

    async def analyze(self, content, mode):
        full_prompt = f"{PROMPTS[mode]}\n\nInhalt:\n{content}\n\nAntwort:\n"
        messages = [
            {"role": "system", "content": "Du bist ein Assistent der Wiener Wohnen GmbH und analysierst und berichtigst OCR-gescannte Anbieterdokumente einer Ausschreibung."},
            {"role": "user", "content": full_prompt}
        ]
        full_response = ""
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=True)
        for chunk in completion:
            content = chunk.choices[0].delta.content
            if content:
                print(content, end="", flush=True)
                full_response += content
        print()  # New line after streaming is complete 
        return full_response

class GoogleProvider(ModelProvider):
    def __init__(self, model_name):
        self.model_name = model_name

    async def setup(self):
        # Implement Google AI setup
        pass

    async def analyze(self, content, mode):
        # Implement Google AI-specific analysis logic here
        return "Google AI analysis not implemented yet"

def read_file_content(filepath, n_chars):
    with open(filepath, 'r', encoding='utf-8') as file:
        content = re.sub(r'!\[.*?\]\(.*?\)', '', file.read(n_chars))
        #content = content.encode('ascii', 'ignore').decode()
        return content

def parse_arguments():
    parser = argparse.ArgumentParser(description="Analyze a file and suggest a filename and summary or classify it.")
    parser.add_argument("filepath", help="Path to the text file to analyze")
    parser.add_argument("-s", action="store_true", help="Generate filename and summary")
    parser.add_argument("-k", action="store_true", help="Classify the content")
    parser.add_argument("-v", action="store_true", help="Verbose Mode")
    parser.add_argument("-n", type=int, default=1000, help="Number of characters to read from the beginning of the file")
    parser.add_argument("--provider", choices=['huggingface', 'ollama', 'openai', 'google'], default='huggingface', help="Choose the model provider")
    parser.add_argument("--model", help="Specify the model name for the chosen provider")
    return parser.parse_args()

async def prompt_for_mode():
    return await asyncio.to_thread(input, "Choose analysis mode (s for summary, k for classification): ")


async def get_model_provider(provider_name, model_name):
    if provider_name == 'huggingface':
        return HuggingFaceProvider(model_name or "mistralai/Mistral-7B-Instruct-v0.3"), model_name or "mistralai/Mistral-7B-Instruct-v0.3"
    elif provider_name == 'ollama':
        return OllamaProvider(model_name or "llama3.2:3b"), model_name or "lama3.2:3b"
    elif provider_name == 'openai':
        return OpenAIProvider(model_name or "nousresearch/hermes-3-llama-3.1-405b:free"), model_name or "nousresearch/hermes-3-llama-3.1-405b:free"
    elif provider_name == 'google':
        return GoogleProvider(model_name or "gemini-pro"), model_name or "gemini-pro"
    else:
        raise ValueError(f"Unsupported provider: {provider_name}")



async def main():
    args = parse_arguments()
    
    provider, model_name = await get_model_provider(args.provider, args.model)
    await provider.setup()
    
    content = read_file_content(args.filepath, args.n)
    
    modes_to_run = []
    if args.s:
        modes_to_run.append('s')
    if args.k:
        modes_to_run.append('k')
    
    if not modes_to_run:
        mode = await prompt_for_mode()
        modes_to_run.append(mode.lower())
    
    for mode in modes_to_run:
        description = 'filename and summary' if mode == 's' else 'classification'
        print(f"\nGenerating {description}...")
        if args.v:
            print(f"Analyzing {args.filepath} with {provider.__class__.__name__}({model_name}):")
            print(f"Content: {content[:1000]}")
        result = await provider.analyze(content, mode)
#        print(result)

    
if __name__ == "__main__":
    asyncio.run(main())