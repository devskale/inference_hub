"""
Example using the Ollama provider.
"""
from uniinfer import ChatMessage, ChatCompletionRequest, ProviderFactory
import sys
import os

# Add the parent directory to the Python path to make the uniinfer package importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    # Initialize the Ollama provider with the default localhost URL
    # provider = ProviderFactory.get_provider("ollama")

    # Or connect to a custom Ollama endpoint
    provider = ProviderFactory.get_provider(
        "ollama", base_url="https://amp1.mooo.com:11444")

    print(f"Connecting to Ollama at {provider.base_url}...")

    # Create a chat request
    messages = [
        ChatMessage(
            role="system", content="You are a helpful AI assistant that provides concise answers."),
        ChatMessage(
            role="user", content="What are three key differences between Python and JavaScript?")
    ]

    # Note: You need to specify a model that's available in your Ollama instance
    request = ChatCompletionRequest(
        messages=messages,
        model="gemma3:4b",  # or another model you have pulled in Ollama
        temperature=0.7,
        max_tokens=300
    )

    try:
        print(f"   Model: {request.model}...")

        if False:
            # Get completion response
            response = provider.complete(request)

            # Print the response
            print("\nResponse:")
            print(f"Model: {response.model}")
            print(f"Content: {response.message.content}")
            print(f"Usage: {response.usage}")

        # Now try streaming
        print("\n\nStreaming response:")

        # Update the request for streaming
        request.streaming = True

        for chunk in provider.stream_complete(request):
            print(chunk.message.content, end="", flush=True)

        print("\n\nStreaming complete!")

    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nNote: Make sure Ollama is running at the specified URL and you have the specified model pulled.")
        print("To pull a model, run: ollama pull llama2")


if __name__ == "__main__":
    main()
