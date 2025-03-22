"""
Example using the ArliAI provider.
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
    # Initialize the ArliAI provider
    if HAS_CREDGOO:
        api_key = get_api_key("arli")
        provider = ProviderFactory.get_provider("arli")  # API key will be fetched automatically
    else:
        # If credgoo is not available, prompt for API key
        api_key = input("Enter your ArliAI API key: ")
        provider = ProviderFactory.get_provider("arli", api_key=api_key)
    
    # Create a chat request
    messages = [
        ChatMessage(role="system", content="You are a helpful assistant."),
        ChatMessage(role="user", content="What are three interesting applications of reinforcement learning?")
    ]
    
    request = ChatCompletionRequest(
        messages=messages,
        model="Mistral-Nemo-12B-Instruct-2407",  # ArliAI model
        temperature=0.7,
        max_tokens=500
    )
    
    # Add ArliAI-specific parameters
    arli_params = {
        "repetition_penalty": 1.1,
        "top_p": 0.9,
        "top_k": 40,
    }
    
    print(f"Sending request to ArliAI (model: {request.model})...")
    
    try:
        # Get standard completion
        response = provider.complete(request, **arli_params)
        
        # Print the response
        print("\nResponse:")
        print(f"Model: {response.model}")
        print(f"Content: {response.message.content}")
        print(f"Usage: {response.usage}")
        
        # Now try streaming
        print("\n\nStreaming response:")
        request.streaming = True  # Enable streaming
        
        for chunk in provider.stream_complete(request, **arli_params):
            print(chunk.message.content, end="", flush=True)
        
        print("\n\nStreaming complete!")
    except Exception as e:
        print(f"Error using ArliAI: {str(e)}")


if __name__ == "__main__":
    main()
