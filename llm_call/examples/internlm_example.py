"""
Example using the InternLM provider.
"""
import sys
import os
import argparse

# Add the parent directory to the Python path to make the uniinfer package importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from credgoo import get_api_key
    HAS_CREDGOO = True
except ImportError:
    HAS_CREDGOO = False
    print("credgoo not found, you'll need to provide an API key manually")

# Check if OpenAI client is available (recommended for InternLM)
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("OpenAI client not found. For better compatibility with InternLM, install it with:")
    print("pip install openai")

from uniinfer import ChatMessage, ChatCompletionRequest, ProviderFactory

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="Chat with an InternLM model")
    parser.add_argument("--model", "-m", type=str, default="internlm3-latest", 
                       help="Model name (default: internlm3-latest)")
    parser.add_argument("--question", "-q", type=str, default="Hello, can you introduce yourself?",
                       help="Question to ask")
    parser.add_argument("--api_key", "-k", type=str, default=None,
                       help="InternLM API key (if not using credgoo)")
    args = parser.parse_args()
    
    # Initialize the InternLM provider
    if args.api_key:
        api_key = args.api_key
    elif HAS_CREDGOO:
        try:
            api_key = get_api_key("internlm")
            print("Using API key from credgoo for InternLM.")
        except Exception as e:
            print(f"Failed to get InternLM API key from credgoo: {str(e)}")
            api_key = input("Enter your InternLM API key: ")
    else:
        api_key = input("Enter your InternLM API key: ")
    
    provider = ProviderFactory.get_provider("internlm", api_key=api_key)
    
    # Create a chat request
    messages = [
        ChatMessage(role="user", content=args.question)
    ]
    
    request = ChatCompletionRequest(
        messages=messages,
        model=args.model,
        temperature=0.8,
        max_tokens=500
    )
    
    # Add InternLM-specific parameters
    internlm_params = {
        "top_p": 0.9
    }
    
    print(f"Sending request to InternLM API (model: {args.model})...")
    print(f"Using OpenAI client: {HAS_OPENAI}")
    
    try:
        # Get standard completion
        print("\nStandard completion:")
        response = provider.complete(request, **internlm_params)
        
        # Print the response
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
        print("\nNote: Make sure you have the correct API key format. The InternLM API requires a token that starts with 'eyJ0eXBlIjoiSl...'")


if __name__ == "__main__":
    main()
