import aiohttp
import asyncio
import json
from credgoo import get_api_key

api_token = get_api_key('chutes')


async def invoke_chute():
    #    api_token = "$CHUTES_API_TOKEN"  # Replace with your actual API token

    headers = {
        "Authorization": "Bearer " + api_token,
        "Content-Type": "application/json"
    }

    body = {
        "model": "deepseek-ai/DeepSeek-V3-0324",
        "messages": [
            {
                "role": "user",
                "content": "Tell me a 250 word story."
            }
        ],
        "stream": True,
        "max_tokens": 1024,
        "temperature": 0.7
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
                "https://llm.chutes.ai/v1/chat/completions",
                headers=headers,
                json=body
        ) as response:
            async for line in response.content:
                line = line.decode("utf-8").strip()
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        if data.strip():
                            json_data = json.loads(data)
                            if 'choices' in json_data and json_data['choices']:
                                content = json_data['choices'][0]['delta'].get(
                                    'content', '')
                                if content:
                                    print(content, end='', flush=True)
                    except json.JSONDecodeError:
                        print(f"Invalid JSON: {data}")
                    except Exception as e:
                        print(f"\nError: {e}")

if __name__ == "__main__":
    asyncio.run(invoke_chute())
