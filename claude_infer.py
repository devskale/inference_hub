import anthropic

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key="sk...",
)


# Main loop for the chatbot
while True:
    # Get user input
    user_input = input("q: ")

    # If the user types "quit", exit the loop
    if user_input.lower() == "quit":
        break

    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": user_input}
        ]
    )
    print(message.content)
