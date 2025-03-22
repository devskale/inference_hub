"""
AI21 provider implementation.
"""
from typing import Dict, Any, Iterator, Optional
import os

from ..core import ChatProvider, ChatCompletionRequest, ChatCompletionResponse, ChatMessage

try:
    from ai21 import AI21Client
    from ai21.models.chat import ChatMessage as AI21ChatMessage
    HAS_AI21 = True
except ImportError:
    HAS_AI21 = False


class AI21Provider(ChatProvider):
    """
    Provider for AI21 API.

    AI21 offers Jamba language models through its own client library.
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the AI21 provider.

        Args:
            api_key (Optional[str]): The AI21 API key.
            **kwargs: Additional configuration options.
        """
        super().__init__(api_key)

        if not HAS_AI21:
            raise ImportError(
                "ai21 package is required for the AI21Provider. "
                "Install it with: pip install ai21"
            )

        # Initialize the AI21 client
        self.client = AI21Client(
            api_key=self.api_key or os.environ.get("AI21_API_KEY")
        )

    def complete(
        self,
        request: ChatCompletionRequest,
        **provider_specific_kwargs
    ) -> ChatCompletionResponse:
        """
        Make a chat completion request to AI21.

        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional AI21-specific parameters.

        Returns:
            ChatCompletionResponse: The completion response.

        Raises:
            Exception: If the request fails.
        """
        # Convert messages to AI21 format
        messages = []
        for msg in request.messages:
            messages.append(
                AI21ChatMessage(content=msg.content, role=msg.role)
            )

        # Prepare parameters
        params = {
            "model": request.model or "jamba-mini-1.6-2025-03",  # Default model
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
            content = completion.choices[0].message.content
            role = completion.choices[0].message.role

            message = ChatMessage(
                role=role,
                content=content
            )

            # Extract usage information (if available)
            usage = {}
            if hasattr(completion, 'usage'):
                usage = {
                    "prompt_tokens": getattr(completion.usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(completion.usage, "completion_tokens", 0),
                    "total_tokens": getattr(completion.usage, "total_tokens", 0)
                }

            # Create raw response
            try:
                if hasattr(completion, "model_dump"):
                    raw_response = completion.model_dump()
                else:
                    # Fallback to a simple dict
                    raw_response = {
                        "message": {"role": role, "content": content},
                        "model": params["model"],
                        "usage": usage
                    }
            except Exception:
                # Fallback to a simple dict
                raw_response = {
                    "message": {"role": role, "content": content},
                    "model": params["model"],
                    "usage": usage
                }

            return ChatCompletionResponse(
                message=message,
                provider='ai21',
                model=params["model"],
                usage=usage,
                raw_response=raw_response
            )
        except Exception as e:
            raise Exception(f"AI21 API error: {str(e)}")

    def stream_complete(
        self,
        request: ChatCompletionRequest,
        **provider_specific_kwargs
    ) -> Iterator[ChatCompletionResponse]:
        """
        Stream a chat completion response from AI21.

        Note: As of the current version, AI21 doesn't support streaming directly through their
        synchronous client. This method implements a simple fallback that returns the full
        response as a single chunk.

        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional AI21-specific parameters.

        Returns:
            Iterator[ChatCompletionResponse]: An iterator with a single response chunk.

        Raises:
            Exception: If the request fails.
        """
        # For now, AI21 doesn't support streaming in the same way as other providers
        # So we'll just return the full response as a single chunk
        try:
            response = self.complete(request, **provider_specific_kwargs)

            # Return the full response as a single chunk
            yield response
        except Exception as e:
            raise Exception(f"AI21 API streaming error: {str(e)}")
