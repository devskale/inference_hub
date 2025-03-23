"""
InternLM provider implementation.
"""
import json
import requests
from typing import Dict, Any, Iterator, Optional

from ..core import ChatProvider, ChatCompletionRequest, ChatCompletionResponse, ChatMessage

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


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
        
        # Initialize OpenAI client if available (preferred method)
        self.client = None
        if HAS_OPENAI:
            self.client = OpenAI(
                api_key=self.api_key,  # No need for 'Bearer' prefix
                base_url=f"{self.base_url}/"
            )
    
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
        
        # Use OpenAI client if available (preferred method)
        if HAS_OPENAI and self.client:
            return self._complete_with_openai(request, **provider_specific_kwargs)
        else:
            # Fallback to direct API calls
            return self._complete_with_requests(request, **provider_specific_kwargs)
    
    def _complete_with_openai(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> ChatCompletionResponse:
        """Use the OpenAI client for completion."""
        try:
            # Prepare parameters
            params = {
                "model": request.model or "internlm3-latest",
                "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
                "temperature": request.temperature,
            }
            
            # Add max_tokens if provided
            if request.max_tokens is not None:
                params["max_tokens"] = request.max_tokens
                
            # Add n if not provided
            if "n" not in provider_specific_kwargs:
                params["n"] = 1
                
            # Add top_p if not provided
            if "top_p" not in provider_specific_kwargs:
                params["top_p"] = 0.9
            
            # Add any provider-specific parameters
            params.update(provider_specific_kwargs)
            
            # Make the request
            completion = self.client.chat.completions.create(**params)
            
            # Extract response
            message = ChatMessage(
                role=completion.choices[0].message.role,
                content=completion.choices[0].message.content
            )
            
            # Extract usage
            usage = {
                "prompt_tokens": completion.usage.prompt_tokens,
                "completion_tokens": completion.usage.completion_tokens,
                "total_tokens": completion.usage.total_tokens
            }
            
            # Convert to dict for raw_response
            raw_response = json.loads(completion.model_dump_json())
            
            return ChatCompletionResponse(
                message=message,
                provider='internlm',
                model=params["model"],
                usage=usage,
                raw_response=raw_response
            )
        except Exception as e:
            raise Exception(f"InternLM API error (OpenAI client): {str(e)}")
    
    def _complete_with_requests(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> ChatCompletionResponse:
        """Use direct requests for completion."""
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
            # Important: InternLM API expects just the token without "Bearer "
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
        
        # Use OpenAI client if available (preferred method)
        if HAS_OPENAI and self.client:
            yield from self._stream_with_openai(request, **provider_specific_kwargs)
        else:
            # Fallback to direct API calls
            yield from self._stream_with_requests(request, **provider_specific_kwargs)
    
    def _stream_with_openai(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> Iterator[ChatCompletionResponse]:
        """Use the OpenAI client for streaming."""
        try:
            # Prepare parameters
            params = {
                "model": request.model or "internlm3-latest",
                "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
                "temperature": request.temperature,
                "stream": True
            }
            
            # Add max_tokens if provided
            if request.max_tokens is not None:
                params["max_tokens"] = request.max_tokens
                
            # Add n if not provided
            if "n" not in provider_specific_kwargs:
                params["n"] = 1
                
            # Add top_p if not provided
            if "top_p" not in provider_specific_kwargs:
                params["top_p"] = 0.9
            
            # Add any provider-specific parameters
            params.update(provider_specific_kwargs)
            
            # Make the streaming request
            stream = self.client.chat.completions.create(**params)
            
            for chunk in stream:
                if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
                    content = chunk.choices[0].delta.content
                    if content:
                        # Create a message for this chunk
                        message = ChatMessage(role="assistant", content=content)
                        
                        # No detailed usage stats in streaming mode
                        usage = {}
                        
                        # Convert to dict for raw_response
                        try:
                            raw_response = json.loads(chunk.model_dump_json())
                        except:
                            raw_response = {"delta": {"content": content}}
                        
                        yield ChatCompletionResponse(
                            message=message,
                            provider='internlm',
                            model=params["model"],
                            usage=usage,
                            raw_response=raw_response
                        )
        except Exception as e:
            raise Exception(f"InternLM API error (OpenAI client): {str(e)}")
    
    def _stream_with_requests(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> Iterator[ChatCompletionResponse]:
        """Use direct requests for streaming."""
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
            
            # Process the streaming response using recommended chunk_size and delimiter
            for chunk in response.iter_lines(chunk_size=8192, decode_unicode=False, delimiter=b'\n'):
                if not chunk:
                    continue
                
                decoded = chunk.decode('utf-8')
                
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
