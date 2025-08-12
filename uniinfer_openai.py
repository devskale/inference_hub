import argparse
import json
from credgoo import get_api_key
from openai import OpenAI

def chat_completion(client, model, message):
    """Send a chat completion request"""
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": message}],
        stream=True
    )
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")

def create_embedding(client, model, text):
    """Send an embedding request"""
    response = client.embeddings.create(
        model=model,
        input=text
    )
    print(response)

if __name__ == "__main__":
    with open('config.json', 'r') as f:
        config = json.load(f)

    parser = argparse.ArgumentParser(description='Universal Inference Client')
    parser.add_argument('--mode', default="chat", choices=['chat', 'embedding'], help='Mode to run: chat or embedding')
    parser.add_argument('--provider', default=config.get('default_provider'), help='Provider to use')
    parser.add_argument('--model', help='Model to use')
    parser.add_argument('--message', default="what temperature has the sun", help='Message to send for chat completion')
    parser.add_argument('--text', default="Hello, this is a test.", help='Text to embed')
    parser.add_argument('--baseurl', default=config.get('default_baseurl'), help='Base URL for the API')
    args = parser.parse_args()

    model = args.model
    if not model:
        if args.mode == 'embedding':
            model = config.get('embedding_model')
        else:
            model = config.get('default_model')


    api_key = get_api_key(args.provider)

    client = OpenAI(
        base_url=args.baseurl,
        api_key=api_key,
    )

    if args.mode == 'chat':
        print('\n\n--')
        chat_completion(client, model, args.message)
    elif args.mode == 'embedding':
        create_embedding(client, model, args.text)
