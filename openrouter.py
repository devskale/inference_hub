from openai import OpenAI
from os import getenv
from getparams import load_api_credentials, load_model_parameters


provider = 'openrouter'
model = 'mistral7b'

api_key = load_api_credentials(provider)
model_parameters, api_url = load_model_parameters(provider, model)

client = OpenAI(
  base_url=api_url,
  api_key=api_key,
)

# Get user input dynamically
user_input = input("Please enter your message: ")

completion = client.chat.completions.create(
  extra_headers={
    "HTTP-Referer": 'skale.io', # Optional, for including your app on openrouter.ai rankings.
    "X-Title": 'skale.io', # Optional. Shows in rankings on openrouter.ai.
  },
  messages=[
    {
      "role": "user",
      "content": user_input,
    },
  ],
  **model_parameters,
#  model="gryphe/mythomist-7b:free",
#  model=model_parameters['model'],
#  max_tokens=model_parameters['max_tokens'],
#  temperature=model_parameters['temperature'],
)

print(completion.choices[0].message.content)
