"""
Example using the SambaNova provider.
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
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("OpenAI package not found. Install it with: pip install openai")


def main():
    if not HAS_OPENAI:
        print("OpenAI package not available. Exiting.")
        return

    # Parse arguments
    parser = argparse.ArgumentParser(description="Chat with a SambaNova model")
    parser.add_argument("--model", "-m", type=str, default="Meta-Llama-3.1-8B-Instruct", 
                        help="Model name (default: Meta-Llama-3.1-8B-Instruct)")
    parser.add_argument("--stream", "-s", action="store_true", 
                        help="Stream the response")
    parser.add_argument("--question", "-q", type=str, 
                        help="Question to ask (default: asking about SambaNova)")
    
    args = parser.parse_args()
    
    # Get API key
    if os.environ.get("SAMBANOVA_API_KEY"):
        api_key = os.environ.get("SAMBANOVA_API_KEY")
        print("Using SAMBANOVA_API_KEY from environment.")
    elif HAS_CREDGOO:
        try:
            api_key = get_api_key("sambanova")
            print(f"Using API key from credgoo for SambaNova.")
        except Exception as e:
            print(f"Failed to get SambaNova API key from credgoo: {str(e)}")
            api_key = input("Enter your SambaNova API key: ")
    else:
        api_key = input("Enter your SambaNova API key: ")
    
    from uniinfer import ChatMessage, ChatCompletionRequest, ProviderFactory
    provider = ProviderFactory.get_provider("sambanova", api_key=api_key)
    
    # Default question if none provided
    question = args.question or "What is SambaNova?"
    
    # Create chat messages
    messages = [
        ChatMessage(role="system", content="You are a helpful assistant with expertise in AI and computing technology."),
        ChatMessage(role="user", content=question)
    ]
    
    # Create the request
    request = ChatCompletionRequest(
        messages=messages,
        model=args.model,
        temperature=0.1,
    )
    
    # Add SambaNova-specific parameters
    sambanova_params = {
        "top_p": 0.1
    }
    
    print(f"Sending request to SambaNova (model: {args.model})...")
    
    try:
        if args.stream:
            # Streaming mode
            print("\nStreaming response:")
            for chunk in provider.stream_complete(request, **sambanova_params):
                print(chunk.message.content, end="", flush=True)
            print("\n\nStreaming complete!")
        else:
            # Standard completion
            response = provider.complete(request, **sambanova_params)
            
            # Print the response
            print("\nResponse:")
            print(f"Model: {response.model}")
            print(f"Content: {response.message.content}")
            print(f"Usage: {response.usage}")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nMake sure you have a valid SambaNova API key.")


if __name__ == "__main__":
    main()
