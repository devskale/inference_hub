"""
Mistral AI provider implementation.
"""
import json
import requests
from typing import Dict, Any, Iterator, Optional

from ..core import ChatProvider, ChatCompletionRequest, ChatCompletionResponse, ChatMessage


class MistralProvider(ChatProvider):
    """
    Provider for Mistral AI API.
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Mistral provider.
        
        Args:
            api_key (Optional[str]): The Mistral API key.
        """
        super().__init__(api_key)
        self.base_url = "https://api.mistral.ai/v1"
    
    def complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> ChatCompletionResponse:
        """
        Make a chat completion request to Mistral AI.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional Mistral-specific parameters.
            
        Returns:
            ChatCompletionResponse: The completion response.
            
        Raises:
            Exception: If the request fails.
        """
        if self.api_key is None:
            raise ValueError("Mistral API key is required")
        
        endpoint = f"{self.base_url}/chat/completions"
        
        # Prepare the request payload
        payload = {
            "model": request.model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
            "temperature": request.temperature,
            "stream": False
        }
        
        # Add max_tokens if provided
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        
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
            error_msg = f"Mistral API error: {response.status_code} - {response.text}"
            raise Exception(error_msg)
        
        # Parse the response
        response_data = response.json()
        choice = response_data['choices'][0]
        message = ChatMessage(
            role=choice['message']['role'],
            content=choice['message']['content']
        )
        
        return ChatCompletionResponse(
            message=message,
            provider='mistral',
            model=response_data.get('model', request.model),
            usage=response_data.get('usage', {}),
            raw_response=response_data
        )
    
    def stream_complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> Iterator[ChatCompletionResponse]:
        """
        Stream a chat completion response from Mistral AI.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional Mistral-specific parameters.
            
        Returns:
            Iterator[ChatCompletionResponse]: An iterator of response chunks.
            
        Raises:
            Exception: If the request fails.
        """
        if self.api_key is None:
            raise ValueError("Mistral API key is required")
        
        endpoint = f"{self.base_url}/chat/completions"
        
        # Prepare the request payload
        payload = {
            "model": request.model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
            "temperature": request.temperature,
            "stream": True
        }
        
        # Add max_tokens if provided
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        
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
                error_msg = f"Mistral API error: {response.status_code} - {response.text}"
                raise Exception(error_msg)
            
            # Process the streaming response
            for line in response.iter_lines():
                if line:
                    # Parse the JSON data from the stream
                    try:
                        data = line.decode('utf-8')
                        if data.startswith('data: '):
                            data = data[6:]  # Remove 'data: ' prefix
                        
                        # Skip empty lines or [DONE]
                        if not data or data == '[DONE]':
                            continue
                        
                        chunk = json.loads(data)
                        
                        if 'choices' in chunk:
                            choice = chunk['choices'][0]
                            role = choice['delta'].get('role', 'assistant')
                            content = choice['delta'].get('content', '')
                            
                            # Create a message for this chunk
                            message = ChatMessage(role=role, content=content)
                            
                            yield ChatCompletionResponse(
                                message=message,
                                provider='mistral',
                                model=chunk.get('model', request.model),
                                usage=chunk.get('usage', {}),
                                raw_response=chunk
                            )
                    except json.JSONDecodeError:
                        # Skip invalid JSON lines
                        continue
