from credgoo import get_api_key
import inquirer
import requests
import json

models = {
    'arli': {
        'model_short': 'mistral-nemo',
        'default': True,
        'model_fullname': 'Mistral-Nemo-12B-Instruct-2407',
        'params': {
            'temperature': 0.7,
            'max_tokens': 1024,
            'repetition_penalty': 1.1,
            'top_p': 0.9,
            'top_k': 40,
            'stream': False
        },
        'url': 'https://api.arliai.com/v1/chat/completions'  # Correct API endpoint
    }
}


if __name__ == '__main__':
    # Example usage
    provider = 'arli'
    api_key = get_api_key('arli')

    print(f"Model: {models[provider]['model_short']}  @{provider}")

    # Initialize conversation with system message
    conversation = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

    # Simple chat interface
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            break

        # Add user message to conversation
        conversation.append({"role": "user", "content": user_input})

        # Prepare request payload
        payload = {
            "model": models[provider]['model_fullname'],
            "messages": conversation,
            **models[provider]['params']
        }

        # Convert payload to JSON string
        payload_json = json.dumps(payload)

        # Make API request
        try:
            print(f"Sending request to: {models[provider]['url']}")

            response = requests.request(
                "POST",
                models[provider]['url'],
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f"Bearer {api_key}"
                },
                data=payload_json
            )

            print(f"Status code: {response.status_code}")

            if response.status_code == 200:
                # Parse the JSON response
                response_json = response.json()

                # Extract assistant response
                assistant_message = response_json['choices'][0]['message']['content']
                conversation.append(
                    {"role": "assistant", "content": assistant_message})

                print(f"\nAI: {assistant_message}")
            else:
                print(f"Error: {response.status_code}")
                print(f"Response: {response.text}")

        except Exception as e:
            print(f"\nError: {e}")
