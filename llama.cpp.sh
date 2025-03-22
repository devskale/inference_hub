#!/bin/bash

# llama-server --hf-repo microsoft/Phi-3-mini-4k-instruct-gguf --hf-file Phi-3-mini-4k-instruct-q4.gguf --port 8080


curl http://localhost:8080/v1/chat/completions \
-H "Content-Type: application/json" \
-H "Authorization: Bearer no-key" \
-d '{
  "model": "Phi-3",
  "messages": [
    {
      "role": "system",
      "content": "You are XYZ, an AI assistant."
    },
    {
      "role": "user",
      "content": "make a top10 list of ai researchers"
    }
  ]
}'
