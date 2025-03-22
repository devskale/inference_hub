"""
Example using the OpenRouter provider.
"""
from uniinfer import ChatMessage, ChatCompletionRequest, ProviderFactory
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


def main():
    # Initialize the OpenRouter provider
    if HAS_CREDGOO:
        api_key = get_api_key("openrouter")
        # API key will be fetched automatically
        provider = ProviderFactory.get_provider("openrouter")
    else:
        # If credgoo is not available, prompt for API key
        api_key = input("Enter your OpenRouter API key: ")
        provider = ProviderFactory.get_provider("openrouter", api_key=api_key)

    # Create a chat request
    messages = [
        ChatMessage(role="system",
                    content="You are a helpful, tech-savvy assistant."),
        ChatMessage(
            role="user", content="Explain the concept of vector databases and how they relate to LLMs.")
    ]

    # OpenRouter lets you use models from different providers with a prefix
    # For example: "openai/gpt-4", "anthropic/claude-3-opus-20240229", etc.
    request = ChatCompletionRequest(
        messages=messages,
        # Specify the model with provider prefix
        model="moonshotai/moonlight-16b-a3b-instruct:free",
        temperature=0.7,
        max_tokens=250
    )

    print(f"Sending request to OpenRouter (model: {request.model})...")

    # For standard completion
    try:
        response = provider.complete(request)

        # Print the response
        print("\nResponse:")
        # This will show the actual model used
        print(f"Model: {response.model}")
        print(f"Content: {response.message.content}")
        print(f"Usage: {response.usage}")

        # For streaming
        print("\n\nStreaming response:")
        request.streaming = True  # Enable streaming

        for chunk in provider.stream_complete(request):
            print(chunk.message.content, end="", flush=True)

        print("\n\nStreaming complete!")
    except Exception as e:
        print(f"Error using OpenRouter: {str(e)}")


if __name__ == "__main__":
    main()
