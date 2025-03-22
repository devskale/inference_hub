"""
Example using the InternLM provider.
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
    # Initialize the InternLM provider
    if HAS_CREDGOO:
        api_key = get_api_key("internlm")
        provider = ProviderFactory.get_provider("internlm")  # API key will be fetched automatically
    else:
        # If credgoo is not available, prompt for API key
        api_key = input("Enter your InternLM API key: ")
        provider = ProviderFactory.get_provider("internlm", api_key=api_key)
    
    # Create a chat request
    messages = [
        ChatMessage(role="user", content="Hello, can you introduce yourself?")
    ]
    
    request = ChatCompletionRequest(
        messages=messages,
        model="internlm3-latest",  # Default InternLM model
        temperature=0.8,
        max_tokens=500
    )
    
    # Add InternLM-specific parameters
    internlm_params = {
        "top_p": 0.9
    }
    
    print(f"Sending request to InternLM API (model: {request.model})...")
    
    try:
        # Get standard completion
        response = provider.complete(request, **internlm_params)
        
        # Print the response
        print("\nResponse:")
        print(f"Model: {response.model}")
        print(f"Content: {response.message.content}")
        print(f"Usage: {response.usage}")
        
        # Now try streaming
        print("\n\nStreaming response:")
        request.streaming = True  # Enable streaming
        
        for chunk in provider.stream_complete(request, **internlm_params):
            print(chunk.message.content, end="", flush=True)
        
        print("\n\nStreaming complete!")
    except Exception as e:
        print(f"Error using InternLM: {str(e)}")


if __name__ == "__main__":
    main()
