"""
NVIDIA GPU Cloud (NGC) provider implementation.
Uses OpenAI-compatible API.
"""
from typing import Dict, Any, Iterator, Optional, List

from ..core import ChatProvider, ChatCompletionRequest, ChatCompletionResponse, ChatMessage
from ..errors import map_provider_error

# Try to import the OpenAI package
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class NGCProvider(ChatProvider):
    """
    Provider for NVIDIA GPU Cloud (NGC) API.
    NGC provides an OpenAI-compatible API for various models.
    """
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://integrate.api.nvidia.com/v1", **kwargs):
        """
        Initialize the NGC provider.
        
        Args:
            api_key (Optional[str]): The NGC API key (required if outside NGC environment).
            base_url (str): The base URL for the NGC API.
            **kwargs: Additional provider-specific configuration parameters.
        """
        super().__init__(api_key)
        
        if not HAS_OPENAI:
            raise ImportError(
                "The 'openai' package is required to use the NGC provider. "
                "Install it with 'pip install openai>=1.0.0'"
            )
        
        # Initialize the OpenAI client with NGC-specific configuration
        self.client = OpenAI(
            base_url=base_url,
            api_key=self.api_key  # May be None if running within NGC environment
        )
        
        # Save any additional configuration
        self.config = kwargs
    
    def complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> ChatCompletionResponse:
        """
        Make a chat completion request to NGC.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional NGC-specific parameters.
            
        Returns:
            ChatCompletionResponse: The completion response.
            
        Raises:
            Exception: If the request fails.
        """
        try:
            # Convert our messages format to the format expected by OpenAI-compatible APIs
            messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
            
            # Prepare parameters
            params = {
                "model": request.model,
                "messages": messages,
                "temperature": request.temperature,
                "stream": False,
            }
            
            # Add max_tokens if provided
            if request.max_tokens is not None:
                params["max_tokens"] = request.max_tokens
                
            # Add any provider-specific parameters
            for key, value in provider_specific_kwargs.items():
                params[key] = value
            
            # Make the API call
            response = self.client.chat.completions.create(**params)
            
            # Extract the response content
            content = response.choices[0].message.content
            
            # Create a ChatMessage from the response
            message = ChatMessage(
                role="assistant",
                content=content
            )
            
            # Create usage information
            usage = {
                "prompt_tokens": response.usage.prompt_tokens if hasattr(response, "usage") and hasattr(response.usage, "prompt_tokens") else 0,
                "completion_tokens": response.usage.completion_tokens if hasattr(response, "usage") and hasattr(response.usage, "completion_tokens") else 0,
                "total_tokens": response.usage.total_tokens if hasattr(response, "usage") and hasattr(response.usage, "total_tokens") else 0
            }
            
            return ChatCompletionResponse(
                message=message,
                provider='ngc',
                model=request.model,
                usage=usage,
                raw_response=response
            )
            
        except Exception as e:
            # Map the error to a standardized format
            mapped_error = map_provider_error("ngc", e)
            raise mapped_error
    
    def stream_complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> Iterator[ChatCompletionResponse]:
        """
        Stream a chat completion response from NGC.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional NGC-specific parameters.
            
        Returns:
            Iterator[ChatCompletionResponse]: An iterator of response chunks.
            
        Raises:
            Exception: If the request fails.
        """
        try:
            # Convert our messages format to the format expected by OpenAI-compatible APIs
            messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
            
            # Prepare parameters
            params = {
                "model": request.model,
                "messages": messages,
                "temperature": request.temperature,
                "stream": True,
            }
            
            # Add max_tokens if provided
            if request.max_tokens is not None:
                params["max_tokens"] = request.max_tokens
                
            # Add any provider-specific parameters
            for key, value in provider_specific_kwargs.items():
                params[key] = value
            
            # Make the streaming API call
            stream = self.client.chat.completions.create(**params)
            
            # Process the streaming response
            for chunk in stream:
                # Check if there is content in this chunk
                if hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content:
                    # Create a message for this chunk
                    message = ChatMessage(
                        role="assistant",
                        content=chunk.choices[0].delta.content
                    )
                    
                    # Create a response for this chunk
                    yield ChatCompletionResponse(
                        message=message,
                        provider='ngc',
                        model=request.model,
                        usage={},
                        raw_response=chunk
                    )
                    
        except Exception as e:
            # Map the error to a standardized format
            mapped_error = map_provider_error("ngc", e)
            raise mapped_error
