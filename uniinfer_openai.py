from credgoo import get_api_key
from openai import OpenAI

provider = 'arli'
model = 'Mistral-Nemo-12B-Instruct-2407'

provider = 'groq'
model = 'qwen-qwq-32b'

baseurl = 'http://localhost:8000/v1'


api_key = get_api_key(provider)

client = OpenAI(
    base_url=baseurl,
    api_key=api_key,
)

# Get user input dynamically
# user_message = input("Please enter your message: ")
user_message = "what temperature has the sun"
print('\n\n--')


completion = client.chat.completions.create(
    model=f"{provider}@{model}",  # Specify the model here
    messages=[{"role": "user",
               "content": user_message}],
    stream=True  # Enable streaming
)


for chunk in completion:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
