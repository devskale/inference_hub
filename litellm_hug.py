import os 
from litellm import completion 
from getparams import load_api_credentials, load_model_parameters

provider = 'huggingface'
model = 'mixtral'

api_key = load_api_credentials(provider)
model_params, api_url = load_model_parameters(provider, model)


user_message = input("Please enter your message: ")


messages=[
    {
      "role": "user",
      "content": user_message
    }
  ]

response = completion(
  model='huggingface/mistralai/Mixtral-8x7B-Instruct-v0.1', 
  messages=messages, 
  max_tokens=model_params['max_tokens'],
  api_base=api_url,
  stream=True
)

for chunk in response:
  if chunk.choices[0].delta.content is not None:
    print(chunk.choices[0].delta.content, end="")