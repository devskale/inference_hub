# openrouter.py
from openai import OpenAI
from getparams import load_api_credentials, load_model_parameters

class OpenRouter:
    def __init__(self, provider='openrouter', model='mistral7b'):
        self.provider = provider
        self.model = model
        self.api_key = self.load_api_credentials()
        self.model_parameters, self.api_url = self.load_model_parameters()
        self.client = self.initialize_client()

    def load_api_credentials(self):
        """Load API credentials for the provider."""
        return load_api_credentials(self.provider)

    def load_model_parameters(self):
        """Load model parameters and API URL for the specified model and provider."""
        return load_model_parameters(self.provider, self.model)

    def initialize_client(self):
        """Initialize the OpenAI client with the loaded API key and URL."""
        return OpenAI(
            base_url=self.api_url,
            api_key=self.api_key
        )

    def get_inference(self, user_message):
        """Perform inference using the specified user message."""
        completion = self.client.chat.completions.create(
            messages=[{"role": "user", "content": user_message}],
            **self.model_parameters,
            stream=True
        )

        response_content = ""
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                response_content += chunk.choices[0].delta.content

        return response_content
