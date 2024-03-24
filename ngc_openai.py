from openai import OpenAI
from getparams import load_api_credentials, load_model_parameters


client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = "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"
)

# Get user input dynamically
user_message = input("Please enter your message: ")
print('\n\n--')


completion = client.chat.completions.create(
  model="mistralai/mixtral-8x7b-instruct-v0.1",
  messages=[{"role":"user",
             "content":user_message}],
  temperature=0.5,
  top_p=1,
  max_tokens=1024,
  stream=True
)

for chunk in completion:
  if chunk.choices[0].delta.content is not None:
    print(chunk.choices[0].delta.content, end="")

