# Import uniinfer components
from uniinfer import (
    ChatMessage,
    ChatCompletionRequest,
    ProviderFactory,
    ChatProvider
)
from credgoo import get_api_key
import argparse
# Cloudflare API Details

from providers_config import PROVIDER_CONFIGS


def main():
    # Initialize argument parser
    parser = argparse.ArgumentParser(description='UniInfer example script')
    parser.add_argument('-l', '--list', action='store_true',
                        help='List available providers')
    parser.add_argument('-p', '--provider', type=str, default='stepfun',
                        help='Specify which provider to use')
    parser.add_argument('-q', '--query', type=str,
                        help='Specify the query to send to the provider')
    parser.add_argument('-m', '--model', type=str,
                        help='Specify which model to use')
    parser.add_argument('-f', '--file', type=str,
                        help='Specify a file to use as context')
    parser.add_argument('-t', '--tokens', type=int, default=4000,
                        help='Specify token limit for file context (default: 4000)')
    args = parser.parse_args()

    if args.list:
        providers = ProviderFactory.list_providers()
        print("Available providers:")
        for provider in providers:
            print(f"- {provider}")
        return

    provider = args.provider

    # Initialize the provider factory
    uni = ProviderFactory().get_provider(
        name=provider,
        api_key=get_api_key(provider),
        # account_id=PROVIDER_CONFIGS[provider].get('extra_params', {}).get('account_id', None)
    )

    prompt = args.query if args.query else "Erkläre mir bitte wie Transformer in maschinellem Lernen funktionieren in einfachen Worten und auf deutsch."

    if args.file:
        try:
            with open(args.file, 'r') as f:
                file_content = f.read()
                # Simple token estimation (4 chars ~ 1 token)
                max_chars = args.tokens * 4
                if len(file_content) > max_chars:
                    file_content = file_content[:max_chars]
                prompt = f"File context: {file_content}\n\nUser query: {prompt}"
        except Exception as e:
            print(f"Error reading file: {e}")

    model = args.model if args.model else PROVIDER_CONFIGS[provider]['default_model']
    print(
        f"Prompt: {prompt} ( {provider}@{model} )")
    # Create a simple chat request
    messages = [
        ChatMessage(role="user", content=prompt)
    ]
    request = ChatCompletionRequest(
        messages=messages,
        model=model,
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
