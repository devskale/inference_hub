import os
from mistralai import Mistral
from credgoo import get_api_key

from credgoo import get_api_key

api_key = get_api_key("mistral")
model = "mistral-small-latest"

client = Mistral(api_key=api_key)

stream_response = client.chat.stream(
    model=model,
    messages=[
        {
            "role": "user",
            "content": "Welcher ist der beste Schweizer Käse?",
        },
    ]
)

for chunk in stream_response:
    print(chunk.data.choices[0].delta.content, end='', flush=True)
