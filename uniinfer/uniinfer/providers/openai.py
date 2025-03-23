"""
OpenAI provider implementation.
"""
import json
import requests
from typing import Dict, Any, Iterator, Optional

from ..core import ChatProvider, ChatCompletionRequest, ChatCompletionResponse, ChatMessage


class OpenAIProvider(ChatProvider):
    """
    Provider for OpenAI API.
    """
    def __init__(self, api_key: Optional[str] = None, organization: Optional[str] = None):
        """
        Initialize the OpenAI provider.
        
        Args:
            api_key (Optional[str]): The OpenAI API key.
            organization (Optional[str]): The OpenAI organization ID.
        """
        super().__init__(api_key)
        self.base_url = "https://api.openai.com/v1"
        self.organization = organization
    
    def complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> ChatCompletionResponse:
        """
        Make a chat completion request to OpenAI.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional OpenAI-specific parameters.
            
        Returns:
            ChatCompletionResponse: The completion response.
            
        Raises:
            Exception: If the request fails.
        """
        if self.api_key is None:
            raise ValueError("OpenAI API key is required")
        
        endpoint = f"{self.base_url}/chat/completions"
        
        # Prepare the request payload
        payload = {
            "model": request.model or "gpt-3.5-turbo",  # Default model if none specified
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
            "temperature": request.temperature,
        }
        
        # Add max_tokens if provided
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        
        # Add any provider-specific parameters (like functions, tools, etc.)
        payload.update(provider_specific_kwargs)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Add organization header if provided
        if self.organization:
            headers["OpenAI-Organization"] = self.organization
        
        response = requests.post(
            endpoint,
            headers=headers,
            data=json.dumps(payload)
        )
        
        # Handle error response
        if response.status_code != 200:
            error_msg = f"OpenAI API error: {response.status_code} - {response.text}"
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
            provider='openai',
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
        Stream a chat completion response from OpenAI.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional OpenAI-specific parameters.
            
        Returns:
            Iterator[ChatCompletionResponse]: An iterator of response chunks.
            
        Raises:
            Exception: If the request fails.
        """
        if self.api_key is None:
            raise ValueError("OpenAI API key is required")
        
        endpoint = f"{self.base_url}/chat/completions"
        
        # Prepare the request payload
        payload = {
            "model": request.model or "gpt-3.5-turbo",
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
        
        # Add organization header if provided
        if self.organization:
            headers["OpenAI-Organization"] = self.organization
        
        with requests.post(
            endpoint,
            headers=headers,
            data=json.dumps(payload),
            stream=True
        ) as response:
            # Handle error response
            if response.status_code != 200:
                error_msg = f"OpenAI API error: {response.status_code} - {response.text}"
                raise Exception(error_msg)
            
            # Process the streaming response
            for line in response.iter_lines():
                if line:
                    # Parse the JSON data from the stream
                    try:
                        line = line.decode('utf-8')
                        
                        # Skip empty lines, data: [DONE], or invalid lines
                        if not line or line == 'data: [DONE]' or not line.startswith('data: '):
                            continue
                        
                        # Parse the data portion
                        data_str = line[6:]  # Remove 'data: ' prefix
                        data = json.loads(data_str)
                        
                        if len(data['choices']) > 0:
                            choice = data['choices'][0]
                            
                            # Skip if content not present
                            if 'delta' not in choice or 'content' not in choice['delta'] or not choice['delta']['content']:
                                continue
                            
                            # Get content from delta
                            content = choice['delta']['content']
                            
                            # Create a message for this chunk
                            message = ChatMessage(
                                role=choice['delta'].get('role', 'assistant'),
                                content=content
                            )
                            
                            # Usage stats typically not provided in stream chunks
                            usage = {}
                            
                            yield ChatCompletionResponse(
                                message=message,
                                provider='openai',
                                model=data.get('model', request.model),
                                usage=usage,
                                raw_response=data
                            )
                    except json.JSONDecodeError:
                        # Skip invalid JSON lines
                        continue
                    except Exception as e:
                        # Skip other errors in individual chunks
                        continue
