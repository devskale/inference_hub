import anthropic

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key="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",
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
