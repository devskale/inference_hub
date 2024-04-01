import os 
from litellm import completion 
from getparams import load_api_credentials, load_model_parameters

provider = 'huggingface'
model = 'mixtral'

api_key = load_api_credentials(provider)
model_params, api_url = load_model_parameters(provider, model)


user_message = input("Please enter your message: ")

#messages = [{ "content": "There's a llama in my garden 😱 What should I do?",
#             "role": "user"}]
messages=[
    {
      "role": "user",
      "content": user_message
    }
  ]

# e.g. Call 'facebook/blenderbot-400M-distill' hosted on HF Inference endpoints
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