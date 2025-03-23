"""
SambaNova provider implementation.
"""
from typing import Dict, Any, Iterator, Optional
import os

from ..core import ChatProvider, ChatCompletionRequest, ChatCompletionResponse, ChatMessage

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class SambanovaProvider(ChatProvider):
    """
    Provider for SambaNova AI API.
    
    SambaNova is an AI hardware and software provider with a focus on enterprise AI solutions.
    The API uses an OpenAI-compatible interface.
    """
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.sambanova.ai/v1", **kwargs):
        """
        Initialize the SambaNova provider.
        
        Args:
            api_key (Optional[str]): The SambaNova API key.
            base_url (str): The base URL for the SambaNova API.
            **kwargs: Additional configuration options.
        """
        super().__init__(api_key)
        self.base_url = base_url
        
        if not HAS_OPENAI:
            raise ImportError(
                "openai package is required for the SambanovaProvider. "
                "Install it with: pip install openai"
            )
        
        # Initialize the OpenAI client for SambaNova
        self.client = openai.OpenAI(
            api_key=self.api_key or os.environ.get("SAMBANOVA_API_KEY"),
            base_url=self.base_url
        )
    
    def complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> ChatCompletionResponse:
        """
        Make a chat completion request to SambaNova.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional SambaNova-specific parameters.
            
        Returns:
            ChatCompletionResponse: The completion response.
            
        Raises:
            Exception: If the request fails.
        """
        # Format messages for SambaNova - using standard format as in the test code
        messages = []
        for msg in request.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Prepare parameters
        params = {
            "model": request.model or "Meta-Llama-3.1-8B-Instruct",  # Updated default model
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
            content = ""
            raw_content = completion.choices[0].message.content
            
            # Handle different content formats
            if isinstance(raw_content, list):
                for item in raw_content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        content += item.get("text", "")
                    elif isinstance(item, str):
                        content += item
            else:
                content = raw_content
            
            message = ChatMessage(
                role=completion.choices[0].message.role,
                content=content
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
                provider='sambanova',
                model=params["model"],
                usage=usage,
                raw_response=raw_response
            )
        except Exception as e:
            raise Exception(f"SambaNova API error: {str(e)}")
    
    def stream_complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> Iterator[ChatCompletionResponse]:
        """
        Stream a chat completion response from SambaNova.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional SambaNova-specific parameters.
            
        Returns:
            Iterator[ChatCompletionResponse]: An iterator of response chunks.
            
        Raises:
            Exception: If the request fails.
        """
        # Format messages for SambaNova - using standard format as in the test code
        messages = []
        for msg in request.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Prepare parameters
        params = {
            "model": request.model or "Meta-Llama-3.1-8B-Instruct",  # Updated default model
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
                # Extract content from the chunk
                content = ""
                
                # The way to access content might differ based on the chunk structure
                try:
                    if hasattr(chunk.choices[0], 'delta'):
                        delta = chunk.choices[0].delta
                        
                        # Check if content is available in delta
                        if hasattr(delta, 'content'):
                            content = delta.content or ""
                except Exception:
                    # If there was an error accessing the content, try alternate methods
                    try:
                        # Try to get content directly from choices
                        content = chunk.choices[0].text
                    except:
                        pass
                
                # Skip empty content chunks
                if not content:
                    continue
                
                # Create a message for this chunk
                message = ChatMessage(role="assistant", content=content)
                
                # No usage stats in streaming mode
                usage = {}
                
                yield ChatCompletionResponse(
                    message=message,
                    provider='sambanova',
                    model=params["model"],
                    usage=usage,
                    raw_response={"delta": {"content": content}}
                )
        except Exception as e:
            raise Exception(f"SambaNova API streaming error: {str(e)}")
