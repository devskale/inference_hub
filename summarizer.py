import asyncio
from ollama import AsyncClient

class Summarizer:
    def __init__(self):
        self.client = AsyncClient()

    async def summarize(self, user_input: str, summary_type: str = 'bullet'):
        if summary_type == 'paragraph':
            message_content = 'Write a one paragraph summary for this article:\n BEGIN_OF_ARTICLE:' + user_input + 'END_OF_ARTICLE.'
        elif summary_type == 'long':
            message_content = 'Write a long summary for this article:\n BEGIN_OF_ARTICLE:\n' + user_input + 'END_OF_ARTICLE.'
        elif summary_type == 'bullet':
            message_content = 'Liste die Top 5 Headlines aus dem gesamten Context dieser News Website :\n BEGIN_OF_CONTEXT:\n' + user_input + 'END_OF_CONTEXT'
        else:
            raise ValueError("Unsupported summary type. Choose 'paragraph' or 'long'.")
        
        message = {'role': 'user', 'content': message_content}
        response_parts = []
        async for part in await self.client.chat(model='dolphin-mistral', messages=[message], stream=True):
            response_parts.append(part['message']['content'])
        return ''.join(response_parts)

    def run_summarize(self, user_input: str, summary_type: str = 'paragraph'):
        return asyncio.run(self.summarize(user_input, summary_type))
