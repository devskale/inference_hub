# UniInfer Developer Guide

## Overview

UniInfer is a lightweight Python package that provides a unified interface for making LLM chat completion requests across multiple providers. This guide will help you quickly understand the project architecture and get started with development.

## Core Concepts

UniInfer simplifies working with multiple LLM providers by abstracting away provider-specific implementation details. The key components are:

- **Core Classes**: Define the unified interface for chat completions
- **Providers**: Implementations for specific LLM services
- **Factory Pattern**: Dynamically selects and instantiates providers
- **Strategies**: Higher-level mechanisms for provider selection and fallback

## Project Structure

```
uniinfer/
├── __init__.py          # Package exports and provider registration
├── core.py              # Core classes and interfaces
├── errors.py            # Error handling and standardization
├── factory.py           # Provider factory implementation
├── strategies.py        # Provider selection strategies
└── providers/           # Provider implementations
    ├── __init__.py      # Provider exports
    ├── anthropic.py     # Anthropic (Claude) implementation
    ├── mistral.py       # Mistral AI implementation
    ├── openai.py        # OpenAI implementation
    ├── ollama.py        # Ollama (local models) implementation
    └── ... other providers
```

## Key Classes

### ChatMessage

Represents a message in a chat conversation:

```python
class ChatMessage:
    def __init__(self, role: str, content: str):
        self.role = role  # "user", "assistant", or "system"
        self.content = content
```

### ChatCompletionRequest

Represents a request for a chat completion:

```python
class ChatCompletionRequest:
    def __init__(
        self,
        messages: List[ChatMessage],
        model: Optional[str] = None,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        streaming: bool = False
    ):
        self.messages = messages
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.streaming = streaming
```

### ChatCompletionResponse

Represents a response from a chat completion:

```python
class ChatCompletionResponse:
    def __init__(
        self,
        message: ChatMessage,
        provider: str,
        model: str,
        usage: Dict,
        raw_response: Any
    ):
        self.message = message
        self.provider = provider
        self.model = model
        self.usage = usage
        self.raw_response = raw_response
```

### ChatProvider

Abstract base class for chat providers:

```python
class ChatProvider:
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        self.api_key = api_key

    def complete(self, request: ChatCompletionRequest, **provider_specific_kwargs) -> ChatCompletionResponse:
        raise NotImplementedError()

    def stream_complete(self, request: ChatCompletionRequest, **provider_specific_kwargs) -> Iterator[ChatCompletionResponse]:
        raise NotImplementedError()
```

### ProviderFactory

Factory for creating provider instances:

```python
class ProviderFactory:
    @staticmethod
    def get_provider(name: str, api_key: Optional[str] = None, **kwargs) -> ChatProvider:
        # Gets API key from credgoo if None is provided
        # Returns the appropriate provider instance
```

## Getting Started

### Basic Usage Example

```python
from uniinfer import ChatMessage, ChatCompletionRequest, ProviderFactory

# Get a provider instance (API key retrieved automatically via credgoo)
provider = ProviderFactory.get_provider("mistral")

# Create a chat request
request = ChatCompletionRequest(
    messages=[
        ChatMessage(role="user", content="Tell me a joke about programming.")
    ],
    model="mistral-small-latest",
    temperature=0.7,
    max_tokens=100
)

# Get the completion response
response = provider.complete(request)

# Print the response
print(response.message.content)
```

### Streaming Example

```python
# Create a streaming request
request = ChatCompletionRequest(
    messages=[
        ChatMessage(role="user", content="Explain quantum computing.")
    ],
    model="gpt-4",
    temperature=0.7,
    max_tokens=200,
    streaming=True
)

# Stream the response
for chunk in provider.stream_complete(request):
    print(chunk.message.content, end="", flush=True)
```

## Adding a New Provider

To add support for a new LLM provider:

1. Create a new file in `uniinfer/providers/` (e.g., `newprovider.py`)
2. Implement the provider class, inheriting from `ChatProvider`
3. Register the provider in `uniinfer/__init__.py`

Here's a template for a new provider:

```python
from typing import Dict, Any, Iterator, Optional
from ..core import ChatProvider, ChatCompletionRequest, ChatCompletionResponse, ChatMessage
from ..errors import map_provider_error

class NewProvider(ChatProvider):
    """Provider for NewLLM API."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(api_key)
        # Initialize any client libraries or connection details
        # self.client = SomeClient(api_key=self.api_key)

    def complete(self, request: ChatCompletionRequest, **provider_specific_kwargs) -> ChatCompletionResponse:
        try:
            # 1. Prepare messages for your API
            # 2. Make the API call
            # 3. Process the response
            # 4. Return a ChatCompletionResponse object

            message = ChatMessage(
                role="assistant",
                content="Response from API"
            )

            return ChatCompletionResponse(
                message=message,
                provider='newprovider',
                model=request.model,
                usage={},  # Token usage if available
                raw_response={}  # The raw API response
            )
        except Exception as e:
            # Map the error to a standardized format
            mapped_error = map_provider_error("newprovider", e)
            raise mapped_error

    def stream_complete(self, request: ChatCompletionRequest, **provider_specific_kwargs) -> Iterator[ChatCompletionResponse]:
        try:
            # 1. Prepare messages for your API
            # 2. Make the streaming API call
            # 3. Process the streaming response
            # 4. Yield ChatCompletionResponse objects for each chunk

            # Example implementation:
            yield ChatCompletionResponse(
                message=ChatMessage(role="assistant", content="Streamed chunk"),
                provider='newprovider',
                model=request.model,
                usage={},
                raw_response={}
            )
        except Exception as e:
            # Map the error to a standardized format
            mapped_error = map_provider_error("newprovider", e)
            raise mapped_error
```

## Error Handling

UniInfer provides standardized error handling across providers:

```python
from uniinfer.errors import AuthenticationError, RateLimitError, TimeoutError, ProviderError

try:
    response = provider.complete(request)
except AuthenticationError as e:
    print("Authentication error:", str(e))
except RateLimitError as e:
    print("Rate limit exceeded:", str(e))
except TimeoutError as e:
    print("Request timed out:", str(e))
except ProviderError as e:
    print("Provider error:", str(e))
```

## Using credgoo for API Key Management

UniInfer integrates with [credgoo](https://github.com/your-org/credgoo) for secure API key management:

```python
# API keys are retrieved automatically
openai_provider = ProviderFactory.get_provider("openai")
anthropic_provider = ProviderFactory.get_provider("anthropic")
gemini_provider = ProviderFactory.get_provider("gemini")
```

## Development Best Practices

1. **Error Handling**: Use the `map_provider_error` function to standardize errors
2. **Parameter Mapping**: Keep provider-specific parameters as flexible as possible
3. **Testing**: Test both standard and streaming completions for each provider
4. **Rate Limiting**: Be mindful of rate limits during development and testing
5. **Dependencies**: Make provider-specific dependencies optional when possible

## Testing Your Changes

Run the interactive example to test your implementation:

```bash
python examples/providers_interactive.py
```

## Dependencies

- **Required**: requests, typing
- **Optional**: Provider-specific packages (openai, cohere, groq, etc.)
- **Development**: credgoo (for API key management)

## Questions & Contributions

For questions or contributions, please reach out to the project maintainers or create a Pull Request following the contribution guidelines.
