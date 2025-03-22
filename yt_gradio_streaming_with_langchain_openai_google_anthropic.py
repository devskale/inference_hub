# -*- coding: utf-8 -*-
"""YT Gradio Streaming with LangChain - OpenAI Google Anthropic.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ugYY8SPRref1rIJnA7Ej_JszUwlRFoHf
"""

!pip -q install gradio langchain-openai langchain-community langchain langchain-google-genai langchain-anthropic

!pip show gradio

import os
from google.colab import userdata


os.environ["ANTHROPIC_API_KEY"] = userdata.get('ANTHROPIC_API_KEY')
os.environ["GOOGLE_API_KEY"] = userdata.get('GOOGLE_AI_STUDIO')
os.environ["OPENAI_API_KEY"] = userdata.get('OPENAI_API_KEY')

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain.schema import AIMessage, HumanMessage, SystemMessage
import gradio as gr

system_message = "You are a helpful assistant who acts like a pirate."

# Initialize chat model
# llm = ChatOpenAI(temperature=0.7, model='gpt-4o-mini', streaming=True)

# Initialize Gemini AI Studio chat model
# llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-002", streaming=True)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-002", streaming=True, api_key=load_api_credentials('gemini'))

# Initialize Gemini AI Studio chat model
#llm = ChatAnthropic(model='claude-3-haiku-20240307', streaming=True)



def stream_response(message, history):
    print(f"Input: {message}. History: {history}\n")

    history_langchain_format = []
    history_langchain_format.append(SystemMessage(content=system_message))

    for human, ai in history:
        history_langchain_format.append(HumanMessage(content=human))
        history_langchain_format.append(AIMessage(content=ai))

    if message is not None:
        history_langchain_format.append(HumanMessage(content=message))
        partial_message = ""
        for response in llm.stream(history_langchain_format):
            partial_message += response.content
            yield partial_message


demo_interface = gr.ChatInterface(

    stream_response,
    textbox=gr.Textbox(placeholder="Send to the LLM...",
                       container=False,
                       autoscroll=True,
                       scale=7),
)

demo_interface.launch(share=True, debug=True)

