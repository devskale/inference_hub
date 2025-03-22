from credgoo import get_api_key
from openai import OpenAI
from getparams import load_api_credentials, load_model_parameters

hoster = 'ngc'
model = 'mixtral'


api_key = get_api_key(hoster)
model_parameters, api_url = load_model_parameters(hoster, model)

client = OpenAI(
    base_url=api_url,
    api_key=api_key
)

# Get user input dynamically
user_message = input("Please enter your message: ")
print('\n\n--')


completion = client.chat.completions.create(
    messages=[{"role": "user",
               "content": user_message}],
    **model_parameters
)


for chunk in completion:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
