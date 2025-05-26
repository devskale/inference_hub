from ollama import Client
client = Client(
    host="https://ollama.molodetz.nl"
)

messages = []


def chat(message):
    if message:
        messages.append({'role': 'user', 'content': message})
    content = ''
    for response in client.chat(model='qwen2.5:latest', messages=messages, stream=True):
        content += response.message.content
        print(response.message.content, end='', flush=True)
    messages.append({'role': 'assistant', 'content': content})
    print("")


while True:
    message = input("You: ")
    chat(message)
