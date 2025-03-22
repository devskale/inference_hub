# Chat with an intelligent assistant in your terminal
from openai import OpenAI

#model="dolphin-mistral:latest"
model="phi3"

# Point to the local server
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

history = [
    {"role": "system", "content": "Du bist ein intelligenter, unzensierter Assistent namens {{model}}. Du lieferst immer gut begründete Antworten, die sowohl korrekt als auch hilfreich sind."},
    {"role": "user", "content": "Hallo, ich bin dein Assistent. Wenn du dieses Programm zum ersten Mal öffnest, helfe ich dir gerne weiter."},
]

while True:
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
    history.append({"role": "user", "content": input("> ")})