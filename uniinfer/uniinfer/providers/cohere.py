"""
Cohere provider implementation.
"""
from typing import Dict, Any, Iterator, Optional

from ..core import ChatProvider, ChatCompletionRequest, ChatCompletionResponse, ChatMessage

try:
    import cohere
    HAS_COHERE = True
except ImportError:
    HAS_COHERE = False


class CohereProvider(ChatProvider):
    """
    Provider for Cohere API.
    """
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the Cohere provider.
        
        Args:
            api_key (Optional[str]): The Cohere API key.
            **kwargs: Additional configuration options.
        """
        super().__init__(api_key)
        
        if not HAS_COHERE:
            raise ImportError(
                "cohere package is required for the CohereProvider. "
                "Install it with: pip install cohere"
            )
        
        # Initialize the Cohere client
        self.client = cohere.ClientV2(api_key=self.api_key)
    
    def complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> ChatCompletionResponse:
        """
        Make a chat completion request to Cohere.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional Cohere-specific parameters.
            
        Returns:
            ChatCompletionResponse: The completion response.
            
        Raises:
            Exception: If the request fails.
        """
        if self.api_key is None:
            raise ValueError("Cohere API key is required")
        
        # Convert messages to Cohere format
        cohere_messages = []
        for msg in request.messages:
            cohere_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Prepare parameters
        params = {
            "model": request.model or "command-r-plus-08-2024",  # Default model
            "messages": cohere_messages,
        }
        
        # Handle temperature (Cohere uses temperature differently)
        if request.temperature is not None:
            params["temperature"] = request.temperature
        
        # Add max_tokens if provided
        if request.max_tokens is not None:
            params["max_tokens"] = request.max_tokens
        
        # Add any provider-specific parameters
        params.update(provider_specific_kwargs)
        
        try:
            # Make the chat completion request
            response = self.client.chat(**params)
            
            # Extract the response content
            content = response.text
            
            # Create a ChatMessage
            message = ChatMessage(
                role="assistant",
                content=content
            )
            
            # Create usage information
            usage = {
                "input_tokens": getattr(response, "input_tokens", 0),
                "output_tokens": getattr(response, "output_tokens", 0),
                "total_tokens": getattr(response, "input_tokens", 0) + getattr(response, "output_tokens", 0)
            }
            
            # Create raw response for debugging
            raw_response = {
                "model": params["model"],
                "text": content,
                "usage": usage
            }
            
            return ChatCompletionResponse(
                message=message,
                provider='cohere',
                model=params["model"],
                usage=usage,
                raw_response=raw_response
            )
        except Exception as e:
            raise Exception(f"Cohere API error: {str(e)}")
    
    def stream_complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> Iterator[ChatCompletionResponse]:
        """
        Stream a chat completion response from Cohere.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional Cohere-specific parameters.
            
        Returns:
            Iterator[ChatCompletionResponse]: An iterator of response chunks.
            
        Raises:
            Exception: If the request fails.
        """
        if self.api_key is None:
            raise ValueError("Cohere API key is required")
        
        # Convert messages to Cohere format
        cohere_messages = []
        for msg in request.messages:
            cohere_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Prepare parameters
        params = {
            "model": request.model or "command-r-plus-08-2024",  # Default model
            "messages": cohere_messages,
        }
        
        # Handle temperature (Cohere uses temperature differently)
        if request.temperature is not None:
            params["temperature"] = request.temperature
        
        # Add max_tokens if provided
        if request.max_tokens is not None:
            params["max_tokens"] = request.max_tokens
        
        # Add any provider-specific parameters
        params.update(provider_specific_kwargs)
        
        try:
            # Make the streaming request
            stream = self.client.chat_stream(**params)
            
            # Process stream events
            for event in stream:
                if event.type == "content-delta":
                    # Extract delta content
                    content = event.delta.message.content.text
                    
                    # Create a message for this chunk
                    message = ChatMessage(
                        role="assistant",
                        content=content
                    )
                    
                    # No detailed usage stats in streaming mode
                    usage = {}
                    
                    # Create a simple raw response
                    raw_response = {
                        "model": params["model"],
                        "delta": {
                            "content": content
                        }
                    }
                    
                    yield ChatCompletionResponse(
                        message=message,
                        provider='cohere',
                        model=params["model"],
                        usage=usage,
                        raw_response=raw_response
                    )
        except Exception as e:
            raise Exception(f"Cohere API streaming error: {str(e)}")
