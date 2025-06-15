import argparse
from ollama import Client

client = Client(
    host="https://ollama.molodetz.nl"
)

messages = []


def chat(message):
    """
    Sends a message to the Ollama client and prints the streamed response.
    Appends user and assistant messages to the global messages list.
    """
    if message:
        messages.append({'role': 'user', 'content': message})
    content = ''
    for response in client.chat(model='qwen2.5:3b', messages=messages, stream=True):
        content += response.message.content
        print(response.message.content, end='', flush=True)
    messages.append({'role': 'assistant', 'content': content})
    print("")


def main():
    """
    Parses command-line arguments and runs the chat in interactive or test mode.
    """
    parser = argparse.ArgumentParser(description="Ollama chat client with interactive and test modes.")
    parser.add_argument('-i', '--interactive', action='store_true', help='Run in interactive chat mode.')
    parser.add_argument('-t', '--test', type=str, help='Feed a standard test message to the client and return the answer.')

    args = parser.parse_args()

    if args.interactive:
        print("Starting interactive chat. Type 'exit' to quit.")
        while True:
            user_message = input("You: ")
            if user_message.lower() == 'exit':
                break
            chat(user_message)
    elif args.test:
        print(f"Sending test message: {args.test}")
        chat(args.test)
    else:
        print("Please specify either -i for interactive mode or -t for a test message.")
        parser.print_help()


if __name__ == "__main__":
    main()
