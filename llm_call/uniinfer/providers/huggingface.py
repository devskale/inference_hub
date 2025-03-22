"""
HuggingFace Inference provider implementation.
"""
from typing import Dict, Any, Iterator, Optional

from ..core import ChatProvider, ChatCompletionRequest, ChatCompletionResponse, ChatMessage

try:
    from huggingface_hub import InferenceClient
    HAS_HUGGINGFACE = True
except ImportError:
    HAS_HUGGINGFACE = False


class HuggingFaceProvider(ChatProvider):
    """
    Provider for HuggingFace Inference API.
    """
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the HuggingFace provider.
        
        Args:
            api_key (Optional[str]): The HuggingFace API key.
            **kwargs: Additional configuration options.
        """
        super().__init__(api_key)
        
        if not HAS_HUGGINGFACE:
            raise ImportError(
                "huggingface_hub package is required for the HuggingFaceProvider. "
                "Install it with: pip install huggingface_hub"
            )
        
        # Initialize the HuggingFace InferenceClient
        self.client = InferenceClient(
            token=self.api_key
        )
    
    def complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> ChatCompletionResponse:
        """
        Make a chat completion request to HuggingFace Inference API.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional HuggingFace-specific parameters.
            
        Returns:
            ChatCompletionResponse: The completion response.
            
        Raises:
            Exception: If the request fails.
        """
        if self.api_key is None:
            raise ValueError("HuggingFace API key is required")
        
        if not request.model:
            raise ValueError("Model must be specified for HuggingFace Inference")
        
        try:
            # Format messages for the text_generation API
            # We'll extract the last user message for simplicity
            last_message = None
            for msg in reversed(request.messages):
                if msg.role == "user":
                    last_message = msg.content
                    break
            
            if last_message is None:
                raise ValueError("No user message found in the request")
            
            # Make the completion request using text_generation
            completion = self.client.text_generation(
                prompt=last_message,
                model=request.model,
                max_new_tokens=request.max_tokens or 500,
                temperature=request.temperature or 0.7,
                **provider_specific_kwargs
            )
            
            # Create a message from the completion
            message = ChatMessage(
                role="assistant",
                content=completion
            )
            
            # Create simple usage information (HuggingFace doesn't provide detailed usage)
            usage = {
                "prompt_tokens": len(last_message.split()),
                "completion_tokens": len(completion.split()),
                "total_tokens": len(last_message.split()) + len(completion.split())
            }
            
            # Create raw response data
            raw_response = {
                "model": request.model,
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": completion
                        }
                    }
                ],
                "usage": usage
            }
            
            return ChatCompletionResponse(
                message=message,
                provider='huggingface',
                model=request.model,
                usage=usage,
                raw_response=raw_response
            )
        except Exception as e:
            raise Exception(f"HuggingFace Inference API error: {str(e)}")
    
    def stream_complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> Iterator[ChatCompletionResponse]:
        """
        Stream a chat completion response from HuggingFace Inference API.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional HuggingFace-specific parameters.
            
        Returns:
            Iterator[ChatCompletionResponse]: An iterator of response chunks.
            
        Raises:
            Exception: If the request fails.
        """
        if self.api_key is None:
            raise ValueError("HuggingFace API key is required")
        
        if not request.model:
            raise ValueError("Model must be specified for HuggingFace Inference")
        
        try:
            # Format messages for the text_generation API
            # We'll extract the last user message for simplicity
            last_message = None
            for msg in reversed(request.messages):
                if msg.role == "user":
                    last_message = msg.content
                    break
            
            if last_message is None:
                raise ValueError("No user message found in the request")
            
            # Make the streaming request using text_generation with stream=True
            stream = self.client.text_generation(
                prompt=last_message,
                model=request.model,
                max_new_tokens=request.max_tokens or 500,
                temperature=request.temperature or 0.7,
                stream=True,
                **provider_specific_kwargs
            )
            
            for chunk in stream:
                # Create a message for this chunk
                message = ChatMessage(
                    role="assistant",
                    content=chunk
                )
                
                # Stream chunks don't have usage information
                usage = {}
                
                # Create raw response structure
                raw_response = {
                    "model": request.model,
                    "choices": [
                        {
                            "delta": {
                                "content": chunk
                            }
                        }
                    ]
                }
                
                yield ChatCompletionResponse(
                    message=message,
                    provider='huggingface',
                    model=request.model,
                    usage=usage,
                    raw_response=raw_response
                )
        except Exception as e:
            raise Exception(f"HuggingFace Inference API error: {str(e)}")
