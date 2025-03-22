"""
Google Gemini provider implementation.
"""
from typing import Dict, Any, Iterator, Optional, List

from ..core import ChatProvider, ChatCompletionRequest, ChatCompletionResponse, ChatMessage
from ..errors import map_provider_error

# Try to import the google.genai package
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False


class GeminiProvider(ChatProvider):
    """
    Provider for Google Gemini API.
    """
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the Gemini provider.
        
        Args:
            api_key (Optional[str]): The Gemini API key.
            **kwargs: Additional provider-specific configuration parameters.
        """
        super().__init__(api_key)
        
        if not HAS_GENAI:
            raise ImportError(
                "The 'google.genai' package is required to use the Gemini provider. "
                "Install it with 'pip install google-generativeai'"
            )
        
        # Initialize the Gemini client
        self.client = genai.Client(api_key=self.api_key)
        
        # Save any additional configuration
        self.config = kwargs
        
    def _prepare_content_and_config(self, request: ChatCompletionRequest) -> tuple:
        """
        Prepare content and config for Gemini API from our messages.
        
        Args:
            request (ChatCompletionRequest): The request to prepare for.
            
        Returns:
            tuple: (content, config) for the Gemini API.
        """
        # Extract all messages
        messages = request.messages
        
        # Look for system message
        system_message = None
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
                break
        
        # Prepare config with generation parameters
        config_params = {}
        if request.temperature is not None:
            config_params["temperature"] = request.temperature
        if request.max_tokens is not None:
            config_params["max_output_tokens"] = request.max_tokens
        
        # Add system message to config if present
        if system_message:
            config_params["system_instruction"] = system_message
        
        # Create the config object
        config = types.GenerateContentConfig(**config_params)
        
        # Prepare the content based on non-system messages
        # For simple queries with just one user message, use a simple string
        if len(messages) == 1 and messages[0].role == "user":
            content = messages[0].content
        else:
            # For more complex exchanges, format as a conversation
            content = []
            for msg in messages:
                if msg.role == "system":
                    # System messages handled in config
                    continue
                elif msg.role == "user":
                    content.append({"role": "user", "parts": [{"text": msg.content}]})
                elif msg.role == "assistant":
                    content.append({"role": "model", "parts": [{"text": msg.content}]})
        
        return content, config
    
    def complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> ChatCompletionResponse:
        """
        Make a chat completion request to Gemini.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional Gemini-specific parameters.
            
        Returns:
            ChatCompletionResponse: The completion response.
            
        Raises:
            Exception: If the request fails.
        """
        if self.api_key is None:
            raise ValueError("Gemini API key is required")
        
        try:
            # Get the model from the request or use a default
            model = request.model or "gemini-1.5-pro"
            
            # Prepare the content and config
            content, config = self._prepare_content_and_config(request)
            
            # Make the API call
            response = self.client.models.generate_content(
                model=model,
                contents=content,
                config=config
            )
            
            # Extract response text
            content = response.text if hasattr(response, "text") else ""
            
            # Create a ChatMessage from the response
            message = ChatMessage(
                role="assistant",
                content=content
            )
            
            # Create usage information (Gemini doesn't provide detailed token counts)
            usage = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
            
            return ChatCompletionResponse(
                message=message,
                provider='gemini',
                model=model,
                usage=usage,
                raw_response=response
            )
            
        except Exception as e:
            # Map the error to a standardized format
            mapped_error = map_provider_error("gemini", e)
            raise mapped_error
    
    def stream_complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> Iterator[ChatCompletionResponse]:
        """
        Stream a chat completion response from Gemini.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional Gemini-specific parameters.
            
        Returns:
            Iterator[ChatCompletionResponse]: An iterator of response chunks.
            
        Raises:
            Exception: If the request fails.
        """
        if self.api_key is None:
            raise ValueError("Gemini API key is required")
        
        try:
            # Get the model from the request or use a default
            model = request.model or "gemini-1.5-pro"
            
            # Prepare the content and config
            content, config = self._prepare_content_and_config(request)
            
            # Make the streaming API call
            stream = self.client.models.generate_content_stream(
                model=model,
                contents=content,
                config=config
            )
            
            # Process the streaming response
            for chunk in stream:
                if hasattr(chunk, "text"):
                    # Create a message for this chunk
                    message = ChatMessage(
                        role="assistant",
                        content=chunk.text
                    )
                    
                    # Create a response for this chunk
                    yield ChatCompletionResponse(
                        message=message,
                        provider='gemini',
                        model=model,
                        usage={},
                        raw_response=chunk
                    )
                    
        except Exception as e:
            # Map the error to a standardized format
            mapped_error = map_provider_error("gemini", e)
            raise mapped_error
