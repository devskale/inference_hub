"""
Simple example using the Mistral provider.
"""
import sys
import os

# Add the parent directory to the Python path to make the uniinfer package importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from credgoo import get_api_key
    HAS_CREDGOO = True
except ImportError:
    HAS_CREDGOO = False
    print("credgoo not found, you'll need to provide an API key manually")

from uniinfer import ChatMessage, ChatCompletionRequest, ProviderFactory

def main():
    # Initialize the Mistral provider
    if HAS_CREDGOO:
        api_key = get_api_key("mistral")
        provider = ProviderFactory.get_provider("mistral")  # API key will be fetched automatically
    else:
        # If credgoo is not available, prompt for API key
        api_key = input("Enter your Mistral API key: ")
        provider = ProviderFactory.get_provider("mistral", api_key=api_key)
    
    # Create a simple chat request
    messages = [
        ChatMessage(role="user", content="Tell me a brief joke about programming.")
    ]
    
    request = ChatCompletionRequest(
        messages=messages,
        model="mistral-small-latest",
        temperature=0.7,
        max_tokens=100
    )
    
    # Get completion response
    print("Sending request to Mistral AI...")
    response = provider.complete(request)
    
    # Print the response
    print("\nResponse:")
    print(f"Model: {response.model}")
    print(f"Content: {response.message.content}")
    print(f"Usage: {response.usage}")

if __name__ == "__main__":
    main()
