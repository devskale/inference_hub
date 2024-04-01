import anthropic
from getparams import load_api_credentials, load_model_parameters

api_key, api_url = load_api_credentials('anthropic')
model = 'claude-3-haiku-20240307'

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=api_key,
)


# Main loop for the chatbot
while True:
    # Get user input
    user_input = input("q: ")

    # If the user types "quit", exit the loop
    if user_input.lower() == "quit":
        break

    message = client.messages.create(
        model=model,
        max_tokens=1024,
        temperature=0.5,
        top_p=0.4,
        messages=[
            {"role": "user", "content": user_input}
        ]
    )
    print(message.content[0].text)
