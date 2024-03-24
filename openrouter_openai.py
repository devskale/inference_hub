from openai import OpenAI
from getparams import load_api_credentials, load_model_parameters

# Assuming OPENROUTER_API_KEY remains the same; otherwise, it should be securely fetched.
OPENROUTER_API_KEY = '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'
MODEL = 'mistralai/mistral-7b-instruct:free'
#MODEL = "gryphe/mythomist-7b:free"


client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=OPENROUTER_API_KEY
)

# Get user input dynamically
user_message = input("Please enter your message: ")
print('\n\n--')

completion = client.chat.completions.create(
  model=MODEL,
  messages=[
    {
      "role": "user",
      "content": user_message
    }
  ],
  temperature=0.5,
  top_p=1,
  max_tokens=1024,
  stream=True
)

for chunk in completion:
  if chunk.choices[0].delta.content is not None:
    print(chunk.choices[0].delta.content, end="")
