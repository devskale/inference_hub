"""
Example using the OpenAI provider.
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
    # Initialize the OpenAI provider
    if HAS_CREDGOO:
        api_key = get_api_key("openai")
        provider = ProviderFactory.get_provider("openai")  # API key will be fetched automatically
    else:
        # If credgoo is not available, prompt for API key
        api_key = input("Enter your OpenAI API key: ")
        provider = ProviderFactory.get_provider("openai", api_key=api_key)
    
    # Create a chat request
    messages = [
        ChatMessage(role="system", content="You are a helpful assistant that writes concise responses."),
        ChatMessage(role="user", content="What are the most promising applications of LLMs in healthcare?")
    ]
    
    request = ChatCompletionRequest(
        messages=messages,
        model="gpt-4",  # Specify GPT-4 model
        temperature=0.7,
        max_tokens=200
    )
    
    print("Sending request to OpenAI...")
    
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
