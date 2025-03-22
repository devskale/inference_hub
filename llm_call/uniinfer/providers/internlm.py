"""
InternLM provider implementation.
"""
import json
import requests
from typing import Dict, Any, Iterator, Optional

from ..core import ChatProvider, ChatCompletionRequest, ChatCompletionResponse, ChatMessage


class InternLMProvider(ChatProvider):
    """
    Provider for InternLM API.
    """
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://chat.intern-ai.org.cn/api/v1", **kwargs):
        """
        Initialize the InternLM provider.
        
        Args:
            api_key (Optional[str]): The InternLM API key.
            base_url (str): The base URL for the InternLM API.
            **kwargs: Additional configuration options.
        """
        super().__init__(api_key)
        self.base_url = base_url
    
    def complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> ChatCompletionResponse:
        """
        Make a chat completion request to InternLM.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional InternLM-specific parameters.
            
        Returns:
            ChatCompletionResponse: The completion response.
            
        Raises:
            Exception: If the request fails.
        """
        if self.api_key is None:
            raise ValueError("InternLM API key is required")
        
        endpoint = f"{self.base_url}/chat/completions"
        
        # Prepare the request payload
        payload = {
            "model": request.model or "internlm3-latest",  # Default to internlm3-latest if no model specified
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
            "temperature": request.temperature,
            "stream": False,
            "n": 1,
        }
        
        # Add max_tokens if provided
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        
        # Default InternLM parameters
        if "top_p" not in provider_specific_kwargs:
            payload["top_p"] = 0.9
        
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
            error_msg = f"InternLM API error: {response.status_code} - {response.text}"
            raise Exception(error_msg)
        
        # Parse the response
        response_data = response.json()
        
        # Handle potential error in response data
        if response_data.get("object") == "error":
            error_msg = f"InternLM API logical error: {response_data}"
            raise Exception(error_msg)
        
        # Extract the message content
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
            provider='internlm',
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
        Stream a chat completion response from InternLM.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional InternLM-specific parameters.
            
        Returns:
            Iterator[ChatCompletionResponse]: An iterator of response chunks.
            
        Raises:
            Exception: If the request fails.
        """
        if self.api_key is None:
            raise ValueError("InternLM API key is required")
        
        endpoint = f"{self.base_url}/chat/completions"
        
        # Prepare the request payload
        payload = {
            "model": request.model or "internlm3-latest",
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
            "temperature": request.temperature,
            "stream": True,
            "n": 1,
        }
        
        # Add max_tokens if provided
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        
        # Default InternLM parameters
        if "top_p" not in provider_specific_kwargs:
            payload["top_p"] = 0.9
        
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
                error_msg = f"InternLM API error: {response.status_code} - {response.text}"
                raise Exception(error_msg)
            
            # Process the streaming response
            for line in response.iter_lines():
                if not line:
                    continue
                
                decoded = line.decode('utf-8')
                
                # Handle special format of InternLM responses
                if not decoded.startswith("data:"):
                    raise Exception(f"InternLM API error message: {decoded}")
                
                # Extract JSON data
                decoded = decoded.strip("data:").strip()
                
                # Check for end of stream
                if decoded == "[DONE]":
                    break
                
                # Parse JSON
                try:
                    data = json.loads(decoded)
                except json.JSONDecodeError:
                    continue
                
                # Check for error
                if data.get("object") == "error":
                    raise Exception(f"InternLM API logical error: {data}")
                
                # Extract delta content
                delta = data.get("choices", [{}])[0].get("delta", {})
                content = delta.get("content", "")
                
                # Skip empty content
                if not content:
                    continue
                
                # Create a message for this chunk
                message = ChatMessage(role="assistant", content=content)
                
                # No detailed usage stats in streaming mode
                usage = {}
                
                yield ChatCompletionResponse(
                    message=message,
                    provider='internlm',
                    model=data.get('model', request.model),
                    usage=usage,
                    raw_response=data
                )
