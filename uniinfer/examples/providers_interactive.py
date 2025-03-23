"""
Interactive example to select a provider and ask a question with streaming output.

This script uses the inquirer library for interactive prompts.
"""
from uniinfer import ChatMessage, ChatCompletionRequest, ProviderFactory
from providers_config import get_all_providers, get_provider_config, add_provider
import sys
import os
import inquirer
import time
from providers_config import (
    HAS_HUGGINGFACE, HAS_COHERE, HAS_MOONSHOT, HAS_OPENAI,
    HAS_GROQ, HAS_AI21, HAS_GENAI
)
# Add the parent directory to the Python path to make the uniinfer package importable
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from credgoo import get_api_key
    HAS_CREDGOO = True
except ImportError:
    HAS_CREDGOO = False
    print("Note: credgoo not found, you'll need to provide API keys manually")

# Provider configurations
PROVIDER_CONFIGS = get_all_providers()

DEFAULT_QUESTION = "Explain how transformers work in machine learning in simple terms very briefly."


def select_provider():
    """
    Prompt the user to select a provider from the list of available providers.

    Returns:
        str: The selected provider ID.
    """
    # Create a list of provider choices
    choices = [
        (f"{config['name']} ({provider_id})", provider_id)
        for provider_id, config in PROVIDER_CONFIGS.items()
    ]

    questions = [
        inquirer.List('provider',
                      message="Select a provider:",
                      choices=choices,
                      carousel=True)
    ]

    answers = inquirer.prompt(questions)
    return answers['provider']


def get_provider_instance(provider_id):
    # Remove the [provider_id] indexing
    config = get_provider_config(provider_id)
    provider_kwargs = config.get('extra_params', {})
    model = config['default_model']

    # Handle API key for providers that need one
    if config['needs_api_key']:
        if HAS_CREDGOO:
            try:
                api_key = get_api_key(provider_id)
                print(f"Using API key from credgoo for {config['name']}.")
            except Exception as e:
                print(f"Failed to get API key from credgoo: {str(e)}")
                api_key = inquirer.text(
                    message=f"Enter your {config['name']} API key:"
                )
        else:
            api_key = inquirer.text(
                message=f"Enter your {config['name']} API key:"
            )

    # Handle Cloudflare account ID first
    if provider_id == 'cloudflare':
        account_id = config.get('extra_params', {}).get('account_id')
        if not account_id:
            raise ValueError("Cloudflare account ID is required")
        provider_kwargs['account_id'] = account_id

        # Initialize provider for Cloudflare
        provider = ProviderFactory.get_provider(
            provider_id, api_key=api_key, **provider_kwargs)
    # Handle API keys for other providers that require them
    elif config['needs_api_key']:
        # Initialize provider for all API key cases
        provider = ProviderFactory.get_provider(
            provider_id, api_key=api_key, **provider_kwargs)
    else:
        # For providers like Ollama that don't need an API key
        provider = ProviderFactory.get_provider(provider_id, **provider_kwargs)

    return provider, model


def get_user_question():
    """
    Get the user's question.

    Returns:
        str: The user's question.
    """
    question = inquirer.text(
        message="What's your question? (press Enter for default):",
    )

    if not question:
        question = DEFAULT_QUESTION
        print(f"Using default question: {question}")

    return question


def main():
    """Main function to run the interactive provider example."""
    print("=== UniInfer Interactive Provider Example ===\n")

    # Get the user to select a provider
    provider_id = select_provider()
    config = PROVIDER_CONFIGS[provider_id]
    print(f"\nYou selected: {config['name']}")

    # Get the provider instance
    try:
        provider, model = get_provider_instance(provider_id)
    except Exception as e:
        print(f"Error initializing provider: {str(e)}")
        return

    # Get the user's question
    question = get_user_question()

    # Create the request
    messages = [
        ChatMessage(role="system",
                    content="You are a helpful, knowledgeable assistant."),
        ChatMessage(role="user", content=question)
    ]

    request = ChatCompletionRequest(
        messages=messages,
        model=model,
        temperature=0.7,
        streaming=True
    )

    # Provider-specific parameters
    provider_specific_params = {}
    if provider_id == 'arli':
        provider_specific_params = {
            "repetition_penalty": 1.1,
            "top_p": 0.9,
            "top_k": 40,
        }
    elif provider_id == 'internlm':
        provider_specific_params = {
            "top_p": 0.9
        }

    # Execute the request
    print("\n=== Response ===\n")
    try:
        # Stream the response
        start_time = time.time()
        response_text = ""

        for chunk in provider.stream_complete(request, **provider_specific_params):
            content = chunk.message.content
            print(content, end="", flush=True)
            response_text += content

        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        print(f"\n\n=== Completed in {elapsed_time:.2f} seconds ===")

        # Ask if the user wants to save the response
        save_response = inquirer.confirm(
            message="Would you like to save this response to a file?",
            default=False
        )

        if save_response:
            filename = inquirer.text(
                message="Enter filename (or press Enter for default):",
                default=f"{provider_id}_response.txt"
            )

            with open(filename, 'w') as f:
                f.write(f"Question: {question}\n\n")
                f.write(f"Response from {config['name']} ({model}):\n\n")
                f.write(response_text)

            print(f"Response saved to {filename}")

    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Make sure the provider is correctly configured and accessible.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation canceled by user.")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
