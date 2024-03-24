from openai import OpenAI
from os import getenv

# Assuming you're still using the same API key; otherwise, fetch it from the environment variable as needed.
OPENROUTER_API_KEY = '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'

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=OPENROUTER_API_KEY,
)

# Get user input dynamically
user_input = input("Please enter your message: ")

completion = client.chat.completions.create(
  extra_headers={
    "HTTP-Referer": 'skale.io', # Optional, for including your app on openrouter.ai rankings.
    "X-Title": 'skale.io', # Optional. Shows in rankings on openrouter.ai.
  },
  model="gryphe/mythomist-7b:free",
  messages=[
    {
      "role": "user",
      "content": user_input,
    },
  ],
)

print(completion.choices[0].message.content)
