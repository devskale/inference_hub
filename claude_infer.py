import anthropic
from getparams import load_api_credentials, load_model_parameters

provider = 'anthropic'
model = 'haiku'

api_key = load_api_credentials(provider)
model_params, api_url = load_model_parameters(provider, model)

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
        messages=[{"role": "user", "content": user_input}],
        **model_params,
    )

    print(message.content[0].text)
