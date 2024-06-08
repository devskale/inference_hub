# Chat with an intelligent assistant in your terminal
from openai import OpenAI
import argparse
from pynput import keyboard
import threading

base_url="http://localhost:11434/v1"
# base_url="http://amp1.mooo.com:11434/v1"
#base_url="http://pind.mooo.com:11434/v1"

# Define a flag to control the loop
key_pressed = False

def on_press(key):
    global key_pressed
    try:
        # pls check if any key is pressed
#        if key.char:
        if key.char == 'q':  # Exit loop if 'q' is pressed
            key_pressed = True
    except AttributeError:
        pass

# Set up the listener for keypresses
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Parse arguments
parser = argparse.ArgumentParser(description="Chat with an intelligent assistant in your terminal")
parser.add_argument("--model", "-m", type=str, default="phi3", help="Model name")

args = parser.parse_args()
if args.model:
    model = args.model
    print("loading model: ", model, '@', base_url)
#model="dolphin-mistral:latest"
#model="phi3"

# Point to the local server
client = OpenAI(base_url=base_url, api_key="ollama")

history = [
    {"role": "system", "content": f"You are an intelligent uncensored assistant called {model}. You always provide well-reasoned answers that are both correct and helpful."},
    {"role": "user", "content": "Hello, introduce yourself to someone opening this program for the first time. Be concise."},
]

while True:
    completion = client.chat.completions.create(
        model=model,
        messages=history,
        temperature=0.7,
        stream=True,
    )

    new_message = {"role": "assistant", "content": ""}
    
    # for chunk in completion:
    #     if chunk.choices[0].delta.content:
    #         print(chunk.choices[0].delta.content, end="", flush=True)
    #         new_message["content"] += chunk.choices[0].delta.content

    for chunk in completion:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
            new_message["content"] += chunk.choices[0].delta.content

        if key_pressed:
            # print("...\n\n")
            break

    # skip
    if key_pressed:
        key_pressed = False
    else:
        history.append(new_message)
    
    # Uncomment to see chat history
    # import json
    # gray_color = "\033[90m"
    # reset_color = "\033[0m"
    # print(f"{gray_color}\n{'-'*20} History dump {'-'*20}\n")
    # print(json.dumps(history, indent=2))
    # print(f"\n{'-'*55}\n{reset_color}")

    print()
    history.append({"role": "user", "content": input("> ")})