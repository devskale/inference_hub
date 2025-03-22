import tkinter as tk
from tkinter import scrolledtext
from openai import OpenAI
import argparse

# Set the base URL for the API
base_url = "https://amp1.mooo.com:11444/v1"

# Parse arguments for the model
parser = argparse.ArgumentParser(description="Chat with an intelligent assistant")
parser.add_argument("--model", "-m", type=str, default="phi3", help="Model name")
args = parser.parse_args()
model = args.model

# Set up the OpenAI client
client = OpenAI(base_url=base_url, api_key="ollama")

# Define the initial history
history = [
    {"role": "system", "content": f"You are an intelligent uncensored assistant called {model}. You always provide well-reasoned answers that are both correct and helpful."},
    {"role": "user", "content": "Hello, introduce yourself to someone opening this program for the first time. Be concise."},
]

def send():
    user_input = entry.get()
    entry.delete(0, tk.END)
    display.config(state=tk.NORMAL)
    display.insert(tk.END, f"You: {user_input}\n")
    display.see(tk.END)
    history.append({"role": "user", "content": user_input})

    # Get response from OpenAI
    completion = client.chat.completions.create(
        model=model,
        messages=history,
        temperature=0.7,
        stream=False,
    )

    if completion.choices:
        assistant_response = completion.choices[0].message['content']
        display.insert(tk.END, f"Assistant: {assistant_response}\n")
        display.see(tk.END)
        history.append({"role": "assistant", "content": assistant_response})
    display.config(state=tk.DISABLED)

# Set up the GUI
root = tk.Tk()
root.title("Chat with an AI Assistant")

# Create a scrolled text widget
display = scrolledtext.ScrolledText(root, state='disabled', height=20, wrap='word')
display.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

# Create an entry widget
entry = tk.Entry(root, width=100)
entry.grid(row=1, column=0, padx=10, sticky='we')

# Create a send button
send_button = tk.Button(root, text="Send", command=send)
send_button.grid(row=1, column=1, padx=10, sticky='we')

root.mainloop()
