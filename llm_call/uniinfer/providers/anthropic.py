"""
Anthropic provider implementation.
"""
import json
import requests
from typing import Dict, Any, Iterator, Optional

from ..core import ChatProvider, ChatCompletionRequest, ChatCompletionResponse, ChatMessage


class AnthropicProvider(ChatProvider):
    """
    Provider for Anthropic Claude API.
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Anthropic provider.
        
        Args:
            api_key (Optional[str]): The Anthropic API key.
        """
        super().__init__(api_key)
        self.base_url = "https://api.anthropic.com/v1"
        self.api_version = "2023-06-01"  # Current Anthropic API version
    
    def complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> ChatCompletionResponse:
        """
        Make a chat completion request to Anthropic.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional Anthropic-specific parameters.
            
        Returns:
            ChatCompletionResponse: The completion response.
            
        Raises:
            Exception: If the request fails.
        """
        if self.api_key is None:
            raise ValueError("Anthropic API key is required")
        
        endpoint = f"{self.base_url}/messages"
        
        # Convert our unified format to Anthropic's format
        # Anthropic expects messages in a specific format
        messages = []
        for msg in request.messages:
            # Map 'user' and 'assistant' roles directly
            # Map 'system' role to a special system message
            if msg.role == "system":
                system_content = msg.content
                continue
            else:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Prepare the request payload
        payload = {
            "messages": messages,
            "model": request.model or "claude-3-sonnet-20240229",  # Default model if none specified
            "temperature": request.temperature,
            "stream": False
        }
        
        # Add max_tokens if provided, Anthropic calls it max_tokens
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        
        # Add system message if it exists
        if 'system_content' in locals():
            payload["system"] = system_content
        
        # Add any provider-specific parameters
        payload.update(provider_specific_kwargs)
        
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key,
            "anthropic-version": self.api_version
        }
        
        response = requests.post(
            endpoint,
            headers=headers,
            data=json.dumps(payload)
        )
        
        # Handle error response
        if response.status_code != 200:
            error_msg = f"Anthropic API error: {response.status_code} - {response.text}"
            raise Exception(error_msg)
        
        # Parse the response
        response_data = response.json()
        
        # Extract the message content
        content = response_data["content"][0]["text"]
        
        message = ChatMessage(
            role="assistant",
            content=content
        )
        
        # Construct usage information
        usage = {
            "input_tokens": response_data.get("usage", {}).get("input_tokens", 0),
            "output_tokens": response_data.get("usage", {}).get("output_tokens", 0),
            "total_tokens": response_data.get("usage", {}).get("input_tokens", 0) + 
                           response_data.get("usage", {}).get("output_tokens", 0)
        }
        
        return ChatCompletionResponse(
            message=message,
            provider='anthropic',
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
        Stream a chat completion response from Anthropic.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional Anthropic-specific parameters.
            
        Returns:
            Iterator[ChatCompletionResponse]: An iterator of response chunks.
            
        Raises:
            Exception: If the request fails.
        """
        if self.api_key is None:
            raise ValueError("Anthropic API key is required")
        
        endpoint = f"{self.base_url}/messages"
        
        # Convert our unified format to Anthropic's format
        messages = []
        for msg in request.messages:
            if msg.role == "system":
                system_content = msg.content
                continue
            else:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Prepare the request payload
        payload = {
            "messages": messages,
            "model": request.model or "claude-3-sonnet-20240229",
            "temperature": request.temperature,
            "stream": True
        }
        
        # Add max_tokens if provided
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        
        # Add system message if it exists
        if 'system_content' in locals():
            payload["system"] = system_content
        
        # Add any provider-specific parameters
        payload.update(provider_specific_kwargs)
        
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.api_key,
            "anthropic-version": self.api_version
        }
        
        with requests.post(
            endpoint,
            headers=headers,
            data=json.dumps(payload),
            stream=True
        ) as response:
            # Handle error response
            if response.status_code != 200:
                error_msg = f"Anthropic API error: {response.status_code} - {response.text}"
                raise Exception(error_msg)
            
            # Process the streaming response
            for line in response.iter_lines():
                if line:
                    # Parse the JSON data from the stream
                    try:
                        data = line.decode('utf-8')
                        
                        # Skip empty lines or data: [DONE]
                        if not data or data == 'data: [DONE]':
                            continue
                        
                        # Remove 'data: ' prefix if present
                        if data.startswith('data: '):
                            data = data[6:]
                        
                        # Parse the JSON
                        event_data = json.loads(data)
                        
                        # Handle different event types
                        if event_data.get('type') == 'content_block_delta':
                            delta = event_data.get('delta', {})
                            content = delta.get('text', '')
                            
                            # Create a message for this chunk
                            message = ChatMessage(role="assistant", content=content)
                            
                            # Calculate approximate usage (Anthropic doesn't provide usage in stream)
                            usage = {
                                "input_tokens": 0,
                                "output_tokens": 0,
                                "total_tokens": 0
                            }
                            
                            yield ChatCompletionResponse(
                                message=message,
                                provider='anthropic',
                                model=event_data.get('model', request.model),
                                usage=usage,
                                raw_response=event_data
                            )
                    except json.JSONDecodeError:
                        # Skip invalid JSON lines
                        continue
