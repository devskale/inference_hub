from credgoo import get_api_key
from uniinfer import ChatMessage, ChatCompletionRequest, ProviderFactory
import sys
import os

# Add the parent directory to the Python path to make the llm_call package importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use direct import from the parent directory

providername = 'mistral'

# Get Mistral API key directly
mistral_api_key = get_api_key(providername)

# Initialize the Mistral provider with API key
provider = ProviderFactory.get_provider(providername, api_key=mistral_api_key)

# Create chat messages
messages = [
    ChatMessage(
        role='user', content='Hello, are you aware of yourself in a sense tha you are a bot? Do you think you are alive?'),
]

# Create chat completion request
request = ChatCompletionRequest(
    messages=messages,
    model='mistral-small-latest',
    temperature=0.7,
    max_tokens=200,
    streaming=False
)

# Get completion response
response = provider.complete(request)

# Print the response
print(f"Response: {response.message.content}")
print(f"Model: {response.model}")
print(f"Usage: {response.usage}")
