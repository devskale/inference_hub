"""
Upstage provider implementation.
"""
from typing import Dict, Any, Iterator, Optional
import os

from ..core import ChatProvider, ChatCompletionRequest, ChatCompletionResponse, ChatMessage

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class UpstageProvider(ChatProvider):
    """
    Provider for Upstage AI Solar API.
    
    Upstage AI offers Solar models through an OpenAI-compatible API.
    """
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.upstage.ai/v1/solar", **kwargs):
        """
        Initialize the Upstage provider.
        
        Args:
            api_key (Optional[str]): The Upstage API key.
            base_url (str): The base URL for the Upstage API.
            **kwargs: Additional configuration options.
        """
        super().__init__(api_key)
        self.base_url = base_url
        
        if not HAS_OPENAI:
            raise ImportError(
                "openai package is required for the UpstageProvider. "
                "Install it with: pip install openai"
            )
        
        # Initialize the OpenAI client for Upstage
        self.client = openai.OpenAI(
            api_key=self.api_key or os.environ.get("UPSTAGE_API_KEY"),
            base_url=self.base_url
        )
    
    def complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> ChatCompletionResponse:
        """
        Make a chat completion request to Upstage.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional Upstage-specific parameters.
            
        Returns:
            ChatCompletionResponse: The completion response.
            
        Raises:
            Exception: If the request fails.
        """
        # Format messages for Upstage
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Prepare parameters
        params = {
            "model": request.model or "solar-pro",  # Default model
            "messages": messages,
            "temperature": request.temperature,
            "stream": False
        }
        
        # Add max_tokens if provided
        if request.max_tokens is not None:
            params["max_tokens"] = request.max_tokens
        
        # Add any provider-specific parameters
        params.update(provider_specific_kwargs)
        
        try:
            # Make the chat completion request
            completion = self.client.chat.completions.create(**params)
            
            # Extract the response content
            message = ChatMessage(
                role=completion.choices[0].message.role,
                content=completion.choices[0].message.content
            )
            
            # Extract usage information
            usage = {}
            if hasattr(completion, 'usage'):
                usage = {
                    "prompt_tokens": completion.usage.prompt_tokens,
                    "completion_tokens": completion.usage.completion_tokens,
                    "total_tokens": completion.usage.total_tokens
                }
            
            # Create raw response
            try:
                raw_response = completion.model_dump_json()
            except AttributeError:
                # Fallback to a simple dict
                raw_response = {
                    "choices": [{"message": {"role": message.role, "content": message.content}}],
                    "model": params["model"],
                    "usage": usage
                }
            
            return ChatCompletionResponse(
                message=message,
                provider='upstage',
                model=params["model"],
                usage=usage,
                raw_response=raw_response
            )
        except Exception as e:
            raise Exception(f"Upstage API error: {str(e)}")
    
    def stream_complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> Iterator[ChatCompletionResponse]:
        """
        Stream a chat completion response from Upstage.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional Upstage-specific parameters.
            
        Returns:
            Iterator[ChatCompletionResponse]: An iterator of response chunks.
            
        Raises:
            Exception: If the request fails.
        """
        # Format messages for Upstage
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Prepare parameters
        params = {
            "model": request.model or "solar-pro",
            "messages": messages,
            "temperature": request.temperature,
            "stream": True
        }
        
        # Add max_tokens if provided
        if request.max_tokens is not None:
            params["max_tokens"] = request.max_tokens
        
        # Add any provider-specific parameters
        params.update(provider_specific_kwargs)
        
        try:
            # Make the streaming request
            stream = self.client.chat.completions.create(**params)
            
            for chunk in stream:
                if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
                    content = chunk.choices[0].delta.content
                    
                    # Skip empty content
                    if not content:
                        continue
                    
                    # Create a message for this chunk
                    message = ChatMessage(role="assistant", content=content)
                    
                    # No usage stats in streaming mode
                    usage = {}
                    
                    yield ChatCompletionResponse(
                        message=message,
                        provider='upstage',
                        model=params["model"],
                        usage=usage,
                        raw_response={"delta": {"content": content}}
                    )
        except Exception as e:
            raise Exception(f"Upstage API streaming error: {str(e)}")
