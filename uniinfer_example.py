# Import uniinfer components
from uniinfer import (
    ChatMessage,
    ChatCompletionRequest,
    ProviderFactory,
    ChatProvider
)
from credgoo import get_api_key
# Cloudflare API Details

from providers_config import PROVIDER_CONFIGS


def main():
    # Initialize the provider factory

    provider = "stepfun"

    # Initialize the provider factory
    uni = ProviderFactory().get_provider(
        name=provider,
        api_key=get_api_key(provider),
        # account_id=PROVIDER_CONFIGS[provider].get('extra_params', {}).get('account_id', None)
    )

    prompt = "Explain how transformers work in machine learning in simple words very briefly."
    print(
        f"Prompt: {prompt} ( {provider}@{PROVIDER_CONFIGS[provider]['default_model']} )")
    # Create a simple chat request
    messages = [
        ChatMessage(role="user", content=prompt)
    ]
    request = ChatCompletionRequest(
        messages=messages,
        model=PROVIDER_CONFIGS[provider]['default_model'],
        streaming=True
    )
    # Make the request
    response_text = ""
    print("\n=== Response ===\n")
    for chunk in uni.stream_complete(request):
        content = chunk.message.content
        print(content, end="", flush=True)
        response_text += content


if __name__ == "__main__":
    main()
