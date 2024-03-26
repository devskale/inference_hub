import cohere 


the_message= input("Enter your message: ")
if the_message == '':
   the_message='whats the latest news from austria'
COHERE_KEY = 'abc'

co = cohere.Client(
    api_key=COHERE_KEY,
)

# chat = co.chat(
#     message=the_message,
#     model="command"
# )

# print(chat)

# response = co.chat_stream( 
#   model='command-r',
#   message=the_message,
#   temperature=0.3,
#   chat_history=[],
#   prompt_truncation='AUTO',
#   citation_quality='accurate',
#   connectors=[{"id":"web-search"}],
#   documents=[]
# ) 

# print(response)

stream = co.chat_stream(
  model='command-r',
  message=the_message,
  temperature=0.3,
  chat_history=[],
  prompt_truncation='AUTO',
#  citation_quality='accurate',
  connectors=[{"id":"web-search"}],
  documents=[]
)

for event in stream:
    if event.event_type == "text-generation":
        print(event.text, end='')