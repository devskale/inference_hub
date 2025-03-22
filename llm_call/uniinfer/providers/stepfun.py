"""
StepFun provider implementation.
"""
from typing import Dict, Any, Iterator, Optional

from ..core import ChatProvider, ChatCompletionRequest, ChatCompletionResponse, ChatMessage

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class StepFunProvider(ChatProvider):
    """
    Provider for StepFun API (阶跃星辰).
    
    StepFun is a China-based LLM provider that uses the OpenAI client format.
    """
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.stepfun.com/v1", **kwargs):
        """
        Initialize the StepFun provider.
        
        Args:
            api_key (Optional[str]): The StepFun API key.
            base_url (str): The base URL for the StepFun API.
            **kwargs: Additional configuration options.
        """
        super().__init__(api_key)
        self.base_url = base_url
        
        if not HAS_OPENAI:
            raise ImportError(
                "openai package is required for the StepFunProvider. "
                "Install it with: pip install openai"
            )
        
        # Initialize the OpenAI client for StepFun
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> ChatCompletionResponse:
        """
        Make a chat completion request to StepFun.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional StepFun-specific parameters.
            
        Returns:
            ChatCompletionResponse: The completion response.
            
        Raises:
            Exception: If the request fails.
        """
        if self.api_key is None:
            raise ValueError("StepFun API key is required")
        
        # Prepare messages in the OpenAI format
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Prepare parameters
        params = {
            "model": request.model or "step-1-8k",  # Default model
            "messages": messages,
            "temperature": request.temperature,
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
                raw_response = {
                    "choices": [{"message": message.to_dict()}],
                    "model": params["model"],
                    "usage": usage
                }
            
            return ChatCompletionResponse(
                message=message,
                provider='stepfun',
                model=params["model"],
                usage=usage,
                raw_response=raw_response
            )
        except Exception as e:
            raise Exception(f"StepFun API error: {str(e)}")
    
    def stream_complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> Iterator[ChatCompletionResponse]:
        """
        Stream a chat completion response from StepFun.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional StepFun-specific parameters.
            
        Returns:
            Iterator[ChatCompletionResponse]: An iterator of response chunks.
            
        Raises:
            Exception: If the request fails.
        """
        if self.api_key is None:
            raise ValueError("StepFun API key is required")
        
        # Prepare messages in the OpenAI format
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Prepare parameters
        params = {
            "model": request.model or "step-1-8k",  # Default model
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
                    if content:
                        # Create a message for this chunk
                        message = ChatMessage(role="assistant", content=content)
                        
                        # No detailed usage stats in streaming mode
                        usage = {}
                        
                        yield ChatCompletionResponse(
                            message=message,
                            provider='stepfun',
                            model=params["model"],
                            usage=usage,
                            raw_response={"chunk": {"content": content}}
                        )
        except Exception as e:
            raise Exception(f"StepFun API streaming error: {str(e)}")
