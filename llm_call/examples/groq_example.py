"""
Example using the Groq provider.
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

try:
    from uniinfer import GroqProvider
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False
    print("Groq provider not available. Install groq package with:")
    print("pip install groq")


def main():
    if not HAS_GROQ:
        print("Groq provider not available. Exiting.")
        return

    # Parse arguments
    parser = argparse.ArgumentParser(description="Chat with a Groq model")
    parser.add_argument("--model", "-m", type=str, default="llama-3.1-8b", 
                        help="Model name (default: llama-3.1-8b)")
    parser.add_argument("--stream", "-s", action="store_true", 
                        help="Stream the response")
    parser.add_argument("--question", "-q", type=str, 
                        help="Question to ask (default: asking about Groq's advantages)")
    
    args = parser.parse_args()
    
    # Initialize the Groq provider
    if HAS_CREDGOO:
        try:
            api_key = get_api_key("groq")
            print(f"Using API key from credgoo for Groq.")
        except Exception as e:
            print(f"Failed to get Groq API key from credgoo: {str(e)}")
            api_key = input("Enter your Groq API key: ")
    else:
        api_key = input("Enter your Groq API key: ")
    
    from uniinfer import ChatMessage, ChatCompletionRequest, ProviderFactory
    provider = ProviderFactory.get_provider("groq", api_key=api_key)
    
    # Default question if none provided
    question = args.question or "What makes Groq unique among LLM providers?"
    
    # Create chat messages
    messages = [
        ChatMessage(role="system", content="You are a helpful assistant with expertise in AI and LLM technology."),
        ChatMessage(role="user", content=question)
    ]
    
    # Create the request
    request = ChatCompletionRequest(
        messages=messages,
        model=args.model,
        temperature=0.7,
        max_tokens=500
    )
    
    print(f"Sending request to Groq (model: {args.model})...")
    
    if args.stream:
        # Streaming mode
        print("\nStreaming response:")
        for chunk in provider.stream_complete(request):
            print(chunk.message.content, end="", flush=True)
        print("\n\nStreaming complete!")
    else:
        # Standard completion
        response = provider.complete(request)
        
        # Print the response
        print("\nResponse:")
        print(f"Model: {response.model}")
        print(f"Content: {response.message.content}")
        print(f"Usage: {response.usage}")


if __name__ == "__main__":
    main()
