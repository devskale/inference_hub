from uniinfer import (
    ChatMessage,
    ChatCompletionRequest,
    ProviderFactory
)
from credgoo import get_api_key

from providers_configs import PROVIDER_CONFIGS


def main():
    user_message = input("Please enter your message: ")
    print('\n\n--')

    provider = "openrouter"

    # Initialize the provider using uniinfer
    uni = ProviderFactory().get_provider(
        name=provider,
        api_key=get_api_key(provider)
    )

    # Create a chat request using the user's message
    messages = [
        ChatMessage(role="user", content=user_message)
    ]
    request = ChatCompletionRequest(
        messages=messages,
        model=PROVIDER_CONFIGS[provider]['default_model'],
        streaming=True
    )

    # Make the request and print the response
    response_text = ""
    print("\n=== Response ===\n")
    for chunk in uni.stream_complete(request):
        content = chunk.message.content
        print(content, end="", flush=True)
        response_text += content


if __name__ == "__main__":
    main()
