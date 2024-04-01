from openai import OpenAI
from getparams import load_api_credentials, load_model_parameters


provider = 'openrouter'
model = 'mistral7b'

api_key = load_api_credentials(provider)
model_parameters, api_url = load_model_parameters(provider, model)


client = OpenAI(
  base_url=api_url,
  api_key=api_key
)

# Get user input dynamically
user_message = input("Please enter your message: ")
print('\n\n--')

completion = client.chat.completions.create(
  messages=[
    {
      "role": "user",
      "content": user_message
    }
  ],
  **model_parameters,
  # model=MODEL,
  # temperature=0.5,
  # top_p=1,
  # max_tokens=1024,
  stream=True
)

for chunk in completion:
  if chunk.choices[0].delta.content is not None:
    print(chunk.choices[0].delta.content, end="")
