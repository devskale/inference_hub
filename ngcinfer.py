import argparse
import json
from uniinfer import (
    ChatMessage,
    ChatCompletionRequest,
    ProviderFactory
)
from credgoo import get_api_key
from providers_config import PROVIDER_CONFIGS


def invoke_api(provider_name, model_parameters, user_input, choice="q"):
    """
    Makes a request to the LLM provider using uniinfer and streams the response.

    Parameters:
    - provider_name: Name of the provider to use
    - model_parameters: Dictionary containing model parameters
    - user_input: User's input text
    - choice: Type of prompt to use (q=question, s=summary, etc.)
    """
    # Initialize the provider using uniinfer
    uni = ProviderFactory().get_provider(
        name=provider_name,
        api_key=get_api_key(provider_name),
        account_id=PROVIDER_CONFIGS.get(provider_name, {}).get(
            'extra_params', {}).get('account_id', None)
    )
    if choice == "q":
        model_input = user_input
    elif choice == "s":
        model_input = "Write a one paragraph summary for this article: "+user_input
    elif choice == "l":
        model_input = "Write a long elaborative summary spanning over several paragraphs for this article: "+user_input
    elif choice == "t":
        model_input = "Write a short tweet pointing to this article in the articles original language: "+user_input
    elif choice == "b":
        model_input = "Write a bullet list summarizing this article in the articles original language: "+user_input

    # Create a chat request
    messages = [ChatMessage(role="user", content=model_input)]

    # Get the model name from provider config or use a default
    model_name = PROVIDER_CONFIGS.get(provider_name, {}).get(
        'default_model', 'default_model')

    # Create the request with model parameters
    request = ChatCompletionRequest(
        messages=messages,
        model=model_name,
        streaming=True,
        **model_parameters
    )

    try:
        # Stream the response
        buffer = []  # Initialize buffer for accumulating partial words
        response_text = ""

        for chunk in uni.stream_complete(request):
            content = chunk.message.content
            response_text += content

            # Add new content to the buffer
            buffer.append(content)

            # Concatenate the buffer to form a complete string and split it by space
            # This maintains spaces between words and allows us to process complete words
            full_str = ''.join(buffer)
            words = full_str.split(' ')

            # Print all but the last word (which might be incomplete)
            for word in words[:-1]:
                print(word + ' ', end='', flush=True)

            # The last word becomes the new buffer content
            buffer[:] = [words[-1]] if words[-1] else []

    except Exception as err:
        print(f"\nAn error occurred: {err}")


def main():
    parser = argparse.ArgumentParser(
        description='Call LLM API with model parameters.')
    # default llm is ngc
    parser.add_argument('-llm', required=False,
                        default="ngc", help='Name of the LLM provider.')
    parser.add_argument('-q', '--question', required=False,
                        help='Question to ask the model.')
    parser.add_argument('-f', '--filename', required=False,
                        help='Filename input.')
    args = parser.parse_args()

    try:
        # Get the provider name
        provider_name = args.llm

        # Check if provider exists in config
        if provider_name not in PROVIDER_CONFIGS:
            print(f"Provider '{provider_name}' not found in configuration.")
            return

        # Get model parameters (empty dict as default)
        model_parameters = {}

        print(
            f"Using provider: {provider_name} with model: {PROVIDER_CONFIGS[provider_name]['default_model']}")

        if args.filename:
            # Read content from the file specified by the user
            with open(args.filename, 'r', encoding='utf-8') as file:
                user_input = file.read().strip()
            # Print the first 50 characters for confirmation
            print(f"\nFile content: {user_input[:50]}...")
            invoke_api(provider_name, model_parameters, user_input)
            exit(0)
        elif args.question:
            user_input = args.question
            print(f"\nq: {user_input}")
            invoke_api(provider_name, model_parameters, user_input)
            exit(0)
        while True:
            # ask for q question, ss short summary, ls long summary, t tweet, b bullet list, or e exit
            choice = input(
                f"Enter a question (q), short summary (s), long summary (l), tweet (t), bullet list (b), or exit (e): ")
            if choice == "e":
                break
            elif choice == "q" or choice == "s" or choice == "l" or choice == "t" or choice == "b":
                user_input = input(f"{choice}: ")
                # add 2 newlines to separate the input from the output
                print(f"\n--\n\n{choice} a: ", end='')
                invoke_api(provider_name, model_parameters, user_input, choice)
                print("\n.")
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
