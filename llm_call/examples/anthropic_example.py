"""
Example using the Anthropic provider.
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
    # Initialize the Anthropic provider
    if HAS_CREDGOO:
        api_key = get_api_key("anthropic")
        provider = ProviderFactory.get_provider("anthropic")  # API key will be fetched automatically
    else:
        # If credgoo is not available, prompt for API key
        api_key = input("Enter your Anthropic API key: ")
        provider = ProviderFactory.get_provider("anthropic", api_key=api_key)
    
    # Create a chat request with a system message
    messages = [
        ChatMessage(role="system", content="You are a knowledgeable assistant that specializes in science."),
        ChatMessage(role="user", content="Explain in simple terms how nuclear fusion works.")
    ]
    
    request = ChatCompletionRequest(
        messages=messages,
        model="claude-3-sonnet-20240229",  # Specify Claude model
        temperature=0.7,
        max_tokens=300
    )
    
    print("Sending request to Anthropic Claude...")
    
    # For standard completion
    response = provider.complete(request)
    
    # Print the response
    print("\nResponse:")
    print(f"Model: {response.model}")
    print(f"Content: {response.message.content}")
    print(f"Usage: {response.usage}")

    # For streaming
    print("\n\nStreaming response:")
    request.streaming = True  # Enable streaming
    
    for chunk in provider.stream_complete(request):
        print(chunk.message.content, end="", flush=True)
    
    print("\n\nStreaming complete!")

if __name__ == "__main__":
    main()
