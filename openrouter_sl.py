from openai import OpenAI
from os import getenv
#from dotenv import load_dotenv, find_dotenv
import timeit
import streamlit as st
from getparams import load_api_credentials, load_model_parameters

#load_dotenv(find_dotenv())
provider = 'openrouter'
model = 'mistral7b'

api_key = load_api_credentials(provider)
model_parameters, api_url = load_model_parameters(provider, model)
OPENROUTER_API_KEY = api_key


def main():
    # gets API Key from environment variable OPENAI_API_KEY
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    user_query = st.text_input("Enter your query")

    if st.button('Submit'):
        startTime = timeit.default_timer()
        completion = client.chat.completions.create(
            extra_headers={
                # "HTTP-Referer": $YOUR_SITE_URL, # Optional, for including your app on openrouter.ai rankings.
                # "X-Title": $YOUR_APP_NAME, # Optional. Shows in rankings on openrouter.ai.
            },
            model="mistralai/mistral-7b-instruct:free",
            messages=[
                {
                    "role": "user",
                    "content": user_query,
                },
            ],
        )

        endTime = timeit.default_timer()
        st.write(completion.choices[0].message.content)
        st.write(f"\n\nQuery execution time: {endTime - startTime:.3f} s.")        

if __name__ == "__main__":
    main()