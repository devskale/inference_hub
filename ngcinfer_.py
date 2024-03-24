import argparse
import configparser
import json
import requests
from getparams import load_api_credentials, load_model_parameters



def invoke_api(api_key, api_url, model_parameters, user_input):
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
    payload = {
        "messages": [{"content": user_input, "role": "user"}],
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
    try:
        json_str = line.decode("utf-8").lstrip('data: ').strip()
        if json_str == "[DONE]":  # Check if the stream is done
            if buffer:  # Print any remaining content in the buffer
                # Ensure "a: " is printed only at the start of the first message
                output = ''.join(buffer).strip()
                if output:  # Check if there's actually content to print
                    print(output, end='')
            buffer.clear()  # Clear the buffer after printing
            return False

        data = json.loads(json_str)
        content = data.get("choices", [{}])[0].get(
            "delta", {}).get("content", "")

        # Add new content to the buffer
        buffer.extend(content)

        # Process buffer to print words as they are completed
        while ' ' in buffer:
            space_index = buffer.index(' ')
            word = ''.join(buffer[:space_index + 1])
            if buffer is not content:  # Avoid repeating "a: " for every piece of content
                print(word, end='')  # Print the completed word
            del buffer[:space_index + 1]  # Remove printed word from buffer

        return True  # Continue streaming
    except json.JSONDecodeError:
        # Handle JSON decoding errors gracefully
        return True  # Continue streaming assuming transient error


def main():
    parser = argparse.ArgumentParser(
        description='Call LLM API with model parameters.')
    # default llm is mixtral7x8
    parser.add_argument('-llm', required=False,
                        default="mixtral", help='Name of the LLM model.')
    parser.add_argument('-q', '--question', required=False,
                        help="""Question to ask the model. 
                            If not provided, the user will be prompted to enter a question.
                            If a valid textfile, eg input.txt is provided the question will be read from the file.""")
    args = parser.parse_args()

    try:
        api_key, api_url = load_api_credentials(args.llm)
        model_parameters = load_model_parameters(args.llm)
#        print(api_key, api_url, model_parameters)
        if args.question:
            user_input = args.question
            print(f"\nq: {user_input}")
        else:
            user_input = input("q: ")
        # add 2 newlines to separate the input from the output
        print("\n--\n\na: ", end='')
        invoke_api(api_key, api_url, model_parameters, user_input)
        print("\n.")
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
