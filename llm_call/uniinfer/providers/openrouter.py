"""
OpenRouter provider implementation.

OpenRouter is a unified API to access multiple AI models from different providers.
"""
import json
import requests
from typing import Dict, Any, Iterator, Optional

from ..core import ChatProvider, ChatCompletionRequest, ChatCompletionResponse, ChatMessage


class OpenRouterProvider(ChatProvider):
    """
    Provider for OpenRouter API.

    OpenRouter provides a unified interface to access multiple AI models from
    different providers, including Anthropic, OpenAI, and more.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenRouter provider.

        Args:
            api_key (Optional[str]): The OpenRouter API key.
        """
        super().__init__(api_key)
        self.base_url = "https://openrouter.ai/api/v1"

    def complete(
        self,
        request: ChatCompletionRequest,
        **provider_specific_kwargs
    ) -> ChatCompletionResponse:
        """
        Make a chat completion request to OpenRouter.

        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional OpenRouter-specific parameters.

        Returns:
            ChatCompletionResponse: The completion response.

        Raises:
            Exception: If the request fails.
        """
        if self.api_key is None:
            raise ValueError("OpenRouter API key is required")

        endpoint = f"{self.base_url}/chat/completions"

        # Prepare the request payload
        payload = {
            # Default model if none specified
            "model": request.model or "moonshotai/moonlight-16b-a3b-instruct:free",
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
            "temperature": request.temperature,
        }

        # Add max_tokens if provided
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens

        # Add any provider-specific parameters
        payload.update(provider_specific_kwargs)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/uniinfer",  # Required by OpenRouter
            "X-Title": "UniInfer"  # Application name for OpenRouter
        }

        response = requests.post(
            endpoint,
            headers=headers,
            data=json.dumps(payload)
        )

        # Handle error response
        if response.status_code != 200:
            error_msg = f"OpenRouter API error: {response.status_code} - {response.text}"
            raise Exception(error_msg)

        # Parse the response
        response_data = response.json()
        choice = response_data['choices'][0]
        message = ChatMessage(
            role=choice['message']['role'],
            content=choice['message']['content']
        )

        # Get the actual model used from the response
        actual_model = response_data.get('model', request.model)

        return ChatCompletionResponse(
            message=message,
            provider='openrouter',
            model=actual_model,
            usage=response_data.get('usage', {}),
            raw_response=response_data
        )

    def stream_complete(
        self,
        request: ChatCompletionRequest,
        **provider_specific_kwargs
    ) -> Iterator[ChatCompletionResponse]:
        """
        Stream a chat completion response from OpenRouter.

        Args:
            request (ChatCompletionRequest): The request to make.
            **provider_specific_kwargs: Additional OpenRouter-specific parameters.

        Returns:
            Iterator[ChatCompletionResponse]: An iterator of response chunks.

        Raises:
            Exception: If the request fails.
        """
        if self.api_key is None:
            raise ValueError("OpenRouter API key is required")

        endpoint = f"{self.base_url}/chat/completions"

        # Prepare the request payload
        payload = {
            "model": request.model or "moonshotai/moonlight-16b-a3b-instruct:free",
            "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
            "temperature": request.temperature,
            "stream": True
        }

        # Add max_tokens if provided
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens

        # Add any provider-specific parameters
        payload.update(provider_specific_kwargs)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/uniinfer",
            "X-Title": "UniInfer"
        }

        with requests.post(
            endpoint,
            headers=headers,
            data=json.dumps(payload),
            stream=True
        ) as response:
            # Handle error response
            if response.status_code != 200:
                error_msg = f"OpenRouter API error: {response.status_code} - {response.text}"
                raise Exception(error_msg)

            # Process the streaming response
            for line in response.iter_lines():
                if line:
                    # Parse the JSON data from the stream
                    try:
                        line = line.decode('utf-8')

                        # Skip empty lines or [DONE]
                        if not line or line == 'data: [DONE]':
                            continue

                        # Remove 'data: ' prefix if present
                        if line.startswith('data: '):
                            line = line[6:]

                        data = json.loads(line)

                        # Skip non-content deltas
                        if 'choices' not in data or not data['choices']:
                            continue

                        choice = data['choices'][0]

                        if 'delta' not in choice or 'content' not in choice['delta'] or not choice['delta']['content']:
                            continue

                        # Extract content delta
                        content = choice['delta']['content']

                        # Get role from delta or default to assistant
                        role = choice['delta'].get('role', 'assistant')

                        # Create a message for this chunk
                        message = ChatMessage(role=role, content=content)

                        # Usage stats typically not provided in stream chunks
                        usage = {}

                        # Get model info if available
                        model = data.get('model', request.model)

                        yield ChatCompletionResponse(
                            message=message,
                            provider='openrouter',
                            model=model,
                            usage=usage,
                            raw_response=data
                        )
                    except json.JSONDecodeError:
                        # Skip invalid JSON lines
                        continue
