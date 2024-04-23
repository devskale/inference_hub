# Chat with an intelligent assistant in your terminal
from openai import OpenAI
import argparse

model="dolphin-mistral:latest"
#model="phi3"

# Point to the local server
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")


history = [
    {"role": "system", "content": f"You are an intelligent assistant called {model}. You always provide well-reasoned answers that are both correct and helpful."},
]
user_message = {"role": "user", "content": ""}

# Argument parsing to allow for file input
parser = argparse.ArgumentParser(description="Process some commands.")
parser.add_argument("-s", "--sumfile", type=str, help="Input file that will be summarized.")
parser.add_argument("-ss", "--sumstring", type=str, help="Input String that will be summarized.")
parser.add_argument("-i", "--inputstring", type=str, help="Input string containing the message.")
args = parser.parse_args()

if args.inputstring:
    user_input = args.inputstring
elif args.sumstring:
    user_message["content"] += 'Please summarize concisely the following text: '
    user_input = args.sumstring
    print('Summarizing >>> ' + user_input[:100] + '...\n')
elif args.sumfile:
    user_message["content"] += 'Please summarize concisely the following article: '
    try:
        with open(args.sumfile, 'r') as file:
            user_input = file.read()
            print('Summarizing >>> ' + args.sumfile + user_input[:100] + '...\n')
    except FileNotFoundError:
        print(f"Error: The file {args.sumfile} was not found.")
        exit(1)
else:
    user_input = input('\nEnter your message: ')


user_message["content"] += user_input
history.append(user_message)
#print(history[1]["content"])
#exit()

completion = client.chat.completions.create(
    model=model,
    messages=history,
    temperature=0.7,
    stream=True,
)

new_message = {"role": "assistant", "content": ""}

for chunk in completion:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
        new_message["content"] += chunk.choices[0].delta.content

history.append(new_message)

# Uncomment to see chat history
# import json
# gray_color = "\033[90m"
# reset_color = "\033[0m"
# print(f"{gray_color}\n{'-'*20} History dump {'-'*20}\n")
# print(json.dumps(history, indent=2))
# print(f"\n{'-'*55}\n{reset_color}")

print()
#history.append({"role": "user", "content": input("> ")})