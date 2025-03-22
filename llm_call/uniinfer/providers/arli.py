"""
ArliAI provider implementation.
"""
import json
import requests
from typing import Dict, Any, Iterator, Optional

from ..core import ChatProvider, ChatCompletionRequest, ChatCompletionResponse, ChatMessage


class ArliAIProvider(ChatProvider):
    """
    Provider for ArliAI API.
    """
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the ArliAI provider.
        
        Args:
            api_key (Optional[str]): The ArliAI API key.
            **kwargs: Additional configuration options.
        """
        super().__init__(api_key)
        self.base_url = "https://api.arliai.com/v1"
    
    def complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> ChatCompletionResponse:
        """
        Make a chat completion request to ArliAI.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional ArliAI-specific parameters.
            
        Returns:
            ChatCompletionResponse: The completion response.
            
        Raises:
            Exception: If the request fails.
        """
        if self.api_key is None:
            raise ValueError("ArliAI API key is required")
        
        endpoint = f"{self.base_url}/chat/completions"
        
        # Prepare the request payload
        payload = {
            "model": request.model or "Mistral-Nemo-12B-Instruct-2407",  # Default model if none specified
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
            "temperature": request.temperature,
            "stream": False
        }
        
        # Add max_tokens if provided
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        
        # ArliAI default parameters
        if "repetition_penalty" not in provider_specific_kwargs:
            payload["repetition_penalty"] = 1.1
        if "top_p" not in provider_specific_kwargs:
            payload["top_p"] = 0.9
        if "top_k" not in provider_specific_kwargs:
            payload["top_k"] = 40
        
        # Add any provider-specific parameters
        payload.update(provider_specific_kwargs)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = requests.post(
            endpoint,
            headers=headers,
            data=json.dumps(payload)
        )
        
        # Handle error response
        if response.status_code != 200:
            error_msg = f"ArliAI API error: {response.status_code} - {response.text}"
            raise Exception(error_msg)
        
        # Parse the response
        response_data = response.json()
        
        # Extract the message content from choices
        choice = response_data.get("choices", [{}])[0]
        message_data = choice.get("message", {})
        
        message = ChatMessage(
            role=message_data.get("role", "assistant"),
            content=message_data.get("content", "")
        )
        
        # Extract usage information
        usage = response_data.get("usage", {})
        
        return ChatCompletionResponse(
            message=message,
            provider='arli',
            model=response_data.get('model', request.model),
            usage=usage,
            raw_response=response_data
        )
    
    def stream_complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> Iterator[ChatCompletionResponse]:
        """
        Stream a chat completion response from ArliAI.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional ArliAI-specific parameters.
            
        Returns:
            Iterator[ChatCompletionResponse]: An iterator of response chunks.
            
        Raises:
            Exception: If the request fails.
        """
        if self.api_key is None:
            raise ValueError("ArliAI API key is required")
        
        endpoint = f"{self.base_url}/chat/completions"
        
        # Prepare the request payload
        payload = {
            "model": request.model or "Mistral-Nemo-12B-Instruct-2407",
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
            "temperature": request.temperature,
            "stream": True
        }
        
        # Add max_tokens if provided
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        
        # ArliAI default parameters
        if "repetition_penalty" not in provider_specific_kwargs:
            payload["repetition_penalty"] = 1.1
        if "top_p" not in provider_specific_kwargs:
            payload["top_p"] = 0.9
        if "top_k" not in provider_specific_kwargs:
            payload["top_k"] = 40
        
        # Add any provider-specific parameters
        payload.update(provider_specific_kwargs)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        with requests.post(
            endpoint,
            headers=headers,
            data=json.dumps(payload),
            stream=True
        ) as response:
            # Handle error response
            if response.status_code != 200:
                error_msg = f"ArliAI API error: {response.status_code} - {response.text}"
                raise Exception(error_msg)
            
            # Process the streaming response
            for line in response.iter_lines():
                if line:
                    # Parse the JSON data from the stream
                    try:
                        line = line.decode('utf-8')
                        
                        # Skip empty lines or '[DONE]'
                        if not line or line == 'data: [DONE]':
                            continue
                        
                        # Remove 'data: ' prefix if present
                        if line.startswith('data: '):
                            line = line[6:]
                        
                        data = json.loads(line)
                        
                        # Skip if no choices or deltas
                        if 'choices' not in data or not data['choices']:
                            continue
                        
                        choice = data['choices'][0]
                        
                        # Handle different streaming formats (delta or message)
                        content = ""
                        role = "assistant"
                        
                        if 'delta' in choice:
                            delta = choice['delta']
                            content = delta.get('content', '')
                            role = delta.get('role', 'assistant')
                        elif 'message' in choice:
                            message = choice['message']
                            content = message.get('content', '')
                            role = message.get('role', 'assistant')
                        
                        # Skip empty content
                        if not content:
                            continue
                        
                        # Create a message for this chunk
                        message = ChatMessage(role=role, content=content)
                        
                        # Usage stats typically not provided in stream chunks
                        usage = {}
                        
                        yield ChatCompletionResponse(
                            message=message,
                            provider='arli',
                            model=data.get('model', request.model),
                            usage=usage,
                            raw_response=data
                        )
                    except json.JSONDecodeError:
                        # Skip invalid JSON lines
                        continue
