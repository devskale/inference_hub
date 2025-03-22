from google import genai
from credgoo import get_api_key

client = genai.Client(api_key=get_api_key("gemini"))

response = client.models.generate_content(
    model="gemini-2.0-flash", contents="Explain how AI works in a few words"
)
print(response.text)


response = client.models.generate_content_stream(
    model="gemini-2.0-flash",
    contents=["Explain how AI works"]
)
for chunk in response:
    print(chunk.text, end="")
