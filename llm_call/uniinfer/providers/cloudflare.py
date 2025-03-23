"""
Cloudflare Workers AI provider implementation.
"""
import json
import requests
from typing import Dict, Any, Iterator, Optional, List

from ..core import ChatProvider, ChatCompletionRequest, ChatCompletionResponse, ChatMessage
from ..errors import map_provider_error, AuthenticationError


class CloudflareProvider(ChatProvider):
    """
    Provider for Cloudflare Workers AI.
    """
    def __init__(self, api_key: Optional[str] = None, account_id: Optional[str] = None, **kwargs):
        """
        Initialize the Cloudflare Workers AI provider.
        
        Args:
            api_key (Optional[str]): The Cloudflare API token.
            account_id (Optional[str]): The Cloudflare account ID.
            **kwargs: Additional provider-specific configuration parameters.
        """
        super().__init__(api_key)
        
        if not api_key:
            raise AuthenticationError("Cloudflare API token is required")
        
        if not account_id:
            raise ValueError("Cloudflare account ID is required")
        
        self.account_id = account_id
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Save any additional configuration
        self.config = kwargs
    
    def _prepare_messages(self, messages: List[ChatMessage]) -> str:
        """
        Prepare messages for Cloudflare Workers AI.
        
        Args:
            messages (List[ChatMessage]): The messages to convert.
            
        Returns:
            str: The formatted prompt for Workers AI.
        """
        # Extract system message if present
        system_content = None
        for msg in messages:
            if msg.role == "system":
                system_content = msg.content
                break
        
        # For chat models, format as a conversation
        formatted_messages = []
        for msg in messages:
            if msg.role == "system":
                continue  # System message will be handled separately
            
            # Format based on role
            if msg.role == "user":
                formatted_messages.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                formatted_messages.append(f"Assistant: {msg.content}")
        
        # Add a final prompt for the assistant to respond
        formatted_messages.append("Assistant:")
        
        # Combine with system message if present
        if system_content:
            prompt = f"System: {system_content}\n\n" + "\n".join(formatted_messages)
        else:
            prompt = "\n".join(formatted_messages)
            
        return prompt
    
    def complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> ChatCompletionResponse:
        """
        Make a chat completion request to Cloudflare Workers AI.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional Cloudflare-specific parameters.
            
        Returns:
            ChatCompletionResponse: The completion response.
            
        Raises:
            Exception: If the request fails.
        """
        try:
            # Get the model from the request
            model = request.model or "@cf/meta/llama-2-7b-chat-int8"
            
            # Prepare the messages
            prompt = self._prepare_messages(request.messages)
            
            # Prepare the request data
            data = {
                "model": model,
                "prompt": prompt,
            }
            
            # Add temperature if provided
            if request.temperature is not None:
                data["temperature"] = request.temperature
            
            # Add max_tokens if provided
            if request.max_tokens is not None:
                data["max_tokens"] = request.max_tokens
            
            # Add any provider-specific parameters
            for key, value in provider_specific_kwargs.items():
                data[key] = value
            
            # Make the API call
            response = requests.post(
                f"{self.base_url}/{model.replace('@', '')}",
                headers=self.headers,
                json=data
            )
            
            # Check for errors
            if response.status_code != 200:
                error_msg = f"Cloudflare API error: {response.status_code} - {response.text}"
                raise Exception(error_msg)
            
            # Parse the response
            response_data = response.json()
            
            # Extract the completion text
            if "result" in response_data and "response" in response_data["result"]:
                content = response_data["result"]["response"]
            else:
                content = ""
            
            # Create a ChatMessage from the response
            message = ChatMessage(
                role="assistant",
                content=content
            )
            
            # Create usage information (Cloudflare may not provide detailed token counts)
            usage = {}
            if "result" in response_data and "usage" in response_data["result"]:
                usage = response_data["result"]["usage"]
            else:
                usage = {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            
            return ChatCompletionResponse(
                message=message,
                provider='cloudflare',
                model=model,
                usage=usage,
                raw_response=response_data
            )
            
        except Exception as e:
            # Map the error to a standardized format
            mapped_error = map_provider_error("cloudflare", e)
            raise mapped_error
    
    def stream_complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> Iterator[ChatCompletionResponse]:
        """
        Stream a chat completion response from Cloudflare Workers AI.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional Cloudflare-specific parameters.
            
        Returns:
            Iterator[ChatCompletionResponse]: An iterator of response chunks.
            
        Raises:
            Exception: If the request fails.
        """
        try:
            # Get the model from the request
            model = request.model or "@cf/meta/llama-2-7b-chat-int8"
            
            # Prepare the messages
            prompt = self._prepare_messages(request.messages)
            
            # Prepare the request data
            data = {
                "model": model,
                "prompt": prompt,
                "stream": True,
            }
            
            # Add temperature if provided
            if request.temperature is not None:
                data["temperature"] = request.temperature
            
            # Add max_tokens if provided
            if request.max_tokens is not None:
                data["max_tokens"] = request.max_tokens
            
            # Add any provider-specific parameters
            for key, value in provider_specific_kwargs.items():
                data[key] = value
            
            # Make the streaming API call
            with requests.post(
                f"{self.base_url}/{model.replace('@', '')}",
                headers=self.headers,
                json=data,
                stream=True
            ) as response:
                # Check for errors
                if response.status_code != 200:
                    error_msg = f"Cloudflare API error: {response.status_code} - {response.text}"
                    raise Exception(error_msg)
                
                # Process the streaming response
                for line in response.iter_lines():
                    if line:
                        try:
                            line_text = line.decode('utf-8')
                            
                            # Skip empty lines
                            if not line_text or line_text == "data: [DONE]":
                                continue
                            
                            # Remove "data: " prefix if present
                            if line_text.startswith('data: '):
                                line_text = line_text[6:]
                            
                            # Parse the JSON
                            chunk_data = json.loads(line_text)
                            
                            # Extract the chunk text
                            if "result" in chunk_data and "response" in chunk_data["result"]:
                                chunk_text = chunk_data["result"]["response"]
                            else:
                                continue
                            
                            # Create a message for this chunk
                            message = ChatMessage(
                                role="assistant",
                                content=chunk_text
                            )
                            
                            # Create a response for this chunk
                            yield ChatCompletionResponse(
                                message=message,
                                provider='cloudflare',
                                model=model,
                                usage={},
                                raw_response=chunk_data
                            )
                            
                        except json.JSONDecodeError:
                            # Skip invalid JSON lines
                            continue
                    
        except Exception as e:
            # Map the error to a standardized format
            mapped_error = map_provider_error("cloudflare", e)
            raise mapped_error
