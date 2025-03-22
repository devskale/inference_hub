curl https://api.x.ai/v1/chat/completions -H "Content-Type: application/json" -H "Authorization: Bearer xai-sgV4BDt9sQbjnBGDMvZfRVnei9XfssQf2jXdMW8t5riXCPg4d9ijeKnt3yCwljQBQIJfKgysHeIMc14f" -d '{
  "messages": [
    {
      "role": "system",
      "content": "You are a test assistant."
    },
    {
      "role": "user",
      "content": "Testing. Just say hi and hello world and nothing else."
    }
  ],
  "model": "grok-beta",
  "stream": false,
  "temperature": 0
}'