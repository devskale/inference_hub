import cohere 
from getparams import load_api_credentials, load_model_parameters


the_message= input("Enter your message: ")
if the_message == '':
   the_message='whats the latest news from austria'

#COHERE_KEY = 'abc'

provider = 'cohere'
model = 'command-r'

api_key = load_api_credentials(provider)
params, api_url = load_model_parameters(provider, model)

co = cohere.Client(
    api_key=api_key,
)

stream = co.chat_stream(
  message=the_message,
  connectors=[{"id":"web-search"}],
  documents=[],
  chat_history=[],
  model=model,
  temperature=0.3,
  prompt_truncation='AUTO',
)

for event in stream:
    if event.event_type == "text-generation":
        print(event.text, end='')