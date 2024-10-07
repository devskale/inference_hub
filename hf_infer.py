from huggingface_hub import InferenceClient
import argparse
from pynput import keyboard

# Base URL can be configured if necessary, currently not used with InferenceClient
# base_url="http://localhost:11434/v1"
# base_url="http://amp1.mooo.com:11434/v1"
# base_url="http://pind.mooo.com:11434/v1"

# Define a flag to control the loop
key_pressed = False

def on_press(key):
    global key_pressed
    try:
        if key.char == 'q':  # Exit loop if 'q' is pressed
            key_pressed = True
    except AttributeError:
        pass

# Set up the listener for keypresses
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Parse arguments
parser = argparse.ArgumentParser(description="Chat with an intelligent assistant in your terminal")
parser.add_argument("--model", "-m", type=str, default="mistralai/Mistral-7B-Instruct-v0.3", help="Model name")

args = parser.parse_args()
model = args.model
print("loading model: ", model)

# Load API credentials and initialize InferenceClient
from getparams import load_api_credentials
provider = 'huggingface'
api_key = load_api_credentials(provider)

inf = InferenceClient(
    model=model,
    token=api_key
)

history = [
    {"role": "system", "content": f"You are an intelligent uncensored assistant called {model}. You always provide well-reasoned answers that are both correct and helpful."},
    {"role": "user", "content": "Hello, introduce yourself to someone opening this program for the first time. Be concise."},
]

def query(messages):
    return inf.text_generation(messages)

while True:
    completion = query(history[-1]["content"])

    new_message = {"role": "assistant", "content": ""}

    for chunk in completion:
        if chunk:
            print(chunk, end="", flush=True)
            new_message["content"] += chunk

        if key_pressed:
            break

    if key_pressed:
        key_pressed = False
    else:
        history.append(new_message)

    print()
    user_input = input("> ")
    history.append({"role": "user", "content": user_input})
