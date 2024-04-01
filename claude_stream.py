#!/usr/bin/env -S poetry run python


import asyncio

from anthropic import AsyncAnthropic
from getparams import load_api_credentials, load_model_parameters

hoster = 'anthropic'
model = 'haiku'

api_key = load_api_credentials(hoster)
params, api_url = load_model_parameters(hoster, model)

client = AsyncAnthropic(
    api_key=api_key,
)

async def main() -> None:
    user_input = input("q: ")
    async with client.messages.stream(
        messages=[
            {
                "role": "user",
                "content": user_input,
            }
        ],
        **params,
    ) as stream:
        async for text in stream.text_stream:
            print(text, end="", flush=True)
        print()

    # you can still get the accumulated final message outside of
    # the context manager, as long as the entire stream was consumed
    # inside of the context manager
    accumulated = await stream.get_final_message()
#    print("accumulated message: ", accumulated.model_dump_json(indent=2))

asyncio.run(main())