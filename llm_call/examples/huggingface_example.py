"""
Example using the HuggingFace Inference provider.
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
    from uniinfer import ChatMessage, ChatCompletionRequest, ProviderFactory, HuggingFaceProvider
    HAS_HUGGINGFACE = True
except ImportError:
    HAS_HUGGINGFACE = False
    print("HuggingFace provider not available. Install huggingface_hub package with:")
    print("pip install huggingface_hub")


def main():
    if not HAS_HUGGINGFACE:
        print("HuggingFace provider not available. Exiting.")
        return
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Chat with a HuggingFace model")
    parser.add_argument("--model", "-m", type=str, default="mistralai/Mistral-7B-Instruct-v0.3", 
                        help="Model name (default: mistralai/Mistral-7B-Instruct-v0.3)")
    parser.add_argument("--max_tokens", type=int, default=500, 
                        help="Maximum number of tokens to generate (default: 500)")
    parser.add_argument("--temperature", type=float, default=0.7, 
                        help="Temperature for generation (default: 0.7)")
    parser.add_argument("--question", "-q", type=str, 
                        default="What is the capital of France?",
                        help="Question to ask (default: 'What is the capital of France?')")
    parser.add_argument("--stream", "-s", action="store_true", 
                        help="Use streaming mode")
    
    args = parser.parse_args()
    
    # Initialize the HuggingFace provider
    if HAS_CREDGOO:
        api_key = get_api_key("huggingface")
        provider = ProviderFactory.get_provider("huggingface", api_key=api_key)
    else:
        # If credgoo is not available, prompt for API key
        api_key = input("Enter your HuggingFace API key: ")
        provider = ProviderFactory.get_provider("huggingface", api_key=api_key)
    
    # Create a chat request
    messages = [
        ChatMessage(role="user", content=args.question)
    ]
    
    # Set up the request
    request = ChatCompletionRequest(
        messages=messages,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens
    )
    
    print(f"Sending request to HuggingFace Inference API (model: {args.model})...")
    
    try:
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
    except Exception as e:
        print(f"Error using HuggingFace: {str(e)}")


if __name__ == "__main__":
    main()
