import argparse
import configparser
import json
import requests
from getparams import load_api_credentials, load_model_parameters



def invoke_api(api_key, api_url, model_parameters, user_input, choice="q"):
    """
    Makes a POST request to the specified URL with given headers and payload,
    parsing streaming JSON responses and printing content word by word.

    Parameters:
    - url: API endpoint URL
    - headers: Dictionary containing request headers
    - payload: Dictionary containing the request payload
    """
    headers = {
        "Authorization": api_key,
        "accept": "text/event-stream",
        "Content-Type": "application/json",
    }
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


    payload = {
        "messages": [{"content": model_input, "role": "user"}],
        **model_parameters,
    }

    try:
        response = requests.post(api_url, headers=headers,
                                 json=payload, stream=True)
        response.raise_for_status()

        buffer = []  # Initialize buffer for accumulating partial words
        for line in response.iter_lines():
            if line:
                # Parse and print each line of content; break if stream is done
                if not parse_and_print_streaming_response(line, buffer):
                    break

    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"An error occurred: {err}")



def parse_and_print_streaming_response(line, buffer):
    usage_info = None  # Initialize a variable to hold the usage data

    try:
        json_str = line.decode("utf-8").lstrip('data: ').strip()
        if json_str == "[DONE]":
            print(''.join(buffer), end='')
            buffer.clear()
            print("\nDONE.")
            return False

        data = json.loads(json_str)
        
        # Extract usage part and assign it to the variable
        usage_info = data.get("usage", None)

        content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")

        # Add new content to the buffer
        buffer.append(content)

        # Concatenate the buffer to form a complete string and split it by space
        # This maintains spaces between words and allows us to process complete words
        full_str = ''.join(buffer)
        words = full_str.split(' ')

        # Print all but the last word (which might be incomplete)
        for word in words[:-1]:
            print(word + ' ', end='')

        # The last word becomes the new buffer content
        buffer[:] = [words[-1]] if words[-1] else []

        # Optionally, you can handle or print the usage information here
        if usage_info:
            print(f"\nUsage Info: {usage_info}")  # This is just an example

        return True  # Continue streaming
    except json.JSONDecodeError:
        print("JSON decode error occurred.", end='')
        return True  # Continue streaming assuming transient error


def main():
    parser = argparse.ArgumentParser(
        description='Call LLM API with model parameters.')
    # default llm is mixtral7x8
    parser.add_argument('-llm', required=False,
                        default="ngc_mixtral", help='Name of the LLM model.')
    parser.add_argument('-q', '--question', required=False,
                        help='Question to ask the model.')
    parser.add_argument('-f', '--filename', required=False,
                        help='Filename input.')
    args = parser.parse_args()

    try:
        api_key, api_url = load_api_credentials(args.llm)
        model_parameters = load_model_parameters(args.llm)
        print(f"model_parameters {args.llm}")
        if args.filename:
            # Read content from the file specified by the user
            with open(args.filename, 'r', encoding='utf-8') as file:
                user_input = file.read().strip()
            print(f"\nFile content: {user_input[:50]}...")  # Print the first 50 characters for confirmation
            invoke_api(api_key, api_url, model_parameters, user_input)
            exit(0)
        elif args.question:
            user_input = args.question
            print(f"\nq: {user_input}")
            invoke_api(api_key, api_url, model_parameters, user_input)
            exit(0)
        while True:
            # ask for q question, ss short summary, ls long summary, t tweet, b bullet list, or e exit
            choice = input(f"Enter a question (q), short summary (s), long summary (l), tweet (t), bullet list (b), or exit (e): ")
            if choice == "e":
                break
            elif choice == "q" or choice == "s" or choice == "l" or choice == "t" or choice == "b":
                user_input = input(f"{choice}: ")
                # add 2 newlines to separate the input from the output
                print(f"\n--\n\n{choice} a: ", end='')
                invoke_api(api_key, api_url, model_parameters, user_input, choice)
                print("\n.")
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
