import asyncio
import argparse
from ollama import AsyncClient


def check_command(user_input):
    initial_chars = user_input[:3]
    if initial_chars == "/s ":
        command = '/s'
    elif initial_chars == "/t ":
        command = '/t'
    elif initial_chars == "/l ":
        command = '/l'
    elif initial_chars == "/n ":
        command = '/n'
    else:
        command = '/q'
    return command


async def chat(command: str, user_input: str):
    if command == '/q':
        message = {'role': 'user', 'content': user_input}
    elif command == '/s':
        message = {'role': 'user', 'content': 'Write a one paragraph summary for this article:\n BEGIN_OF_ARTICLE:' +
                   user_input + 'END_OF_ARTICLE.'}
    elif command == '/l':
        message = {'role': 'user', 'content': 'Write a long summary for this article:\n BEGIN_OF_ARTICLE:\n' +
                   user_input + 'END_OF_ARTICLE.'}
    elif command == '/t':
        message = {'role': 'user', 'content': 'Write a short engaging tweet pointing to this article, use emojis if appropriate.:\n BEGIN_OF_ARTICLE' +
                   user_input + '\n END_OF_ARTICLE. return only the tweet.'}
    elif command == '/n':
        message = {'role': 'user', 'content': 'Improve this text for better readability:\n BEGIN_OF_TEXT:\n' +
                   user_input + '\nEND_OF_TEXT. \nreturn only the improved text.'}

    ollamaClient = AsyncClient(
        host='https://amp1.mooo.com:11444'
        #        host='localhost:11434'
    )
    async for part in await ollamaClient.chat(
            model='gemma3:4b', messages=[message],
            stream=True):
        print(part['message']['content'], end='', flush=True)

# Argument parsing to allow for file input
parser = argparse.ArgumentParser(description="Process some commands.")
parser.add_argument("-f", "--file", type=str,
                    help="Input file containing the message.")
args = parser.parse_args()

if args.file:
    try:
        with open(args.file, 'r') as file:
            user_input = file.read()
    except FileNotFoundError:
        print(f"Error: The file {args.file} was not found.")
        exit(1)
else:
    user_input = input(
        '\nEnter your message /s(ummarize) /t(weet) /l(ongsummary) /n(icify) : ')

while True:
    if user_input == '':
        user_input = input(
            '\nEnter your message /s(ummarize) /t(weet) /l(ongsummary) /n(icify) : ')

    command = check_command(user_input)
    if command != '/q':
        user_input = user_input[3:]

    # calculate the number of tokens / maxtokens (=32k)
    tokennum = len(user_input) / 4
    maxtokens = 32000
    tokenpercent = tokennum / maxtokens * 100
    if tokennum > maxtokens:
        print(
            f"Error: The input text is too long {tokennum}. The maximum number of tokens is {maxtokens}.")
        exit(1)
    print(
        f'{command} chars: {str(len(user_input))},   tokens: {str(len(user_input)/4)}   {tokenpercent}%\n{user_input[:50]} ... {user_input[(len(user_input)-50):]}----\n')
    asyncio.run(chat(command, user_input))
    user_input = ''
