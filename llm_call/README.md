# UniInfer · [![PyPI Version](https://img.shields.io/pypi/v/uniinfer.svg)](https://pypi.org/project/uniinfer/)

**Unified LLM Inference Interface for Python**

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/uniinfer.svg)](https://pypi.org/project/uniinfer/)
[![Documentation](https://img.shields.io/badge/docs-readthedocs.io-informational)](https://uniinfer.readthedocs.io)

UniInfer provides a consistent Python interface for LLM chat completions across multiple providers with:

- 🚀 Single API for 15+ LLM providers
- ⚡ Real-time streaming support
- 🔄 Automatic fallback strategies
- 🔧 Extensible provider architecture

## Table of Contents

- [Features](#features)
- [Supported Providers](#supported-providers)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Advanced Usage](#advanced-usage)
- [Provider Development](#adding-a-new-provider)
- [Contributing](#contributing)
- [License](#license)

## Features ✨

### Core Capabilities

- **Unified API** - Consistent interface across all providers
- **Multi-provider Support** - Switch between providers with one line change
- **Streaming** - Real-time token streaming for all providers
- **Error Resilience** - Automatic retries & fallback strategies

### Advanced Features

- **Credential Management** - Integrated with credgoo for secure key storage
- **Custom Parameters** - Provider-specific options when needed
- **Type Safety** - Full Python type hint support
- **Provider Fallback** - Automatic provider switching on failures

## Installation

```bash
pip install uniinfer
```

Or install from source:

```bash
git clone https://github.com/your-username/uniinfer.git
cd uniinfer
pip install -e .
```

## Quick Start

### Basic Usage

```python
from uniinfer import ChatMessage, ChatCompletionRequest, ProviderFactory

# Get a provider instance
provider = ProviderFactory.get_provider("mistral", api_key="your-api-key")

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

### With credgoo Integration

If you have credgoo installed, you can get API keys automatically:

```python
from uniinfer import ProviderFactory

# API key will be fetched automatically
provider = ProviderFactory.get_provider("mistral")

# ... rest of your code
```

### Streaming Responses

```python
from uniinfer import ChatMessage, ChatCompletionRequest, ProviderFactory

# Get a provider instance
provider = ProviderFactory.get_provider("openai", api_key="your-api-key")

# Create a chat request with streaming enabled
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

### Provider-Specific Parameters

You can pass provider-specific parameters when making requests:

```python
# For OpenAI with tools/functions
response = provider.complete(
    request,
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather in a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ],
    tool_choice="auto"
)
```

### Using System Messages

System messages work across all providers:

```python
request = ChatCompletionRequest(
    messages=[
        ChatMessage(role="system", content="You are a helpful assistant that specializes in science."),
        ChatMessage(role="user", content="Explain how nuclear fusion works.")
    ],
    model="claude-3-sonnet-20240229",
    temperature=0.7
)
```

### Fallback Between Providers

You can use the built-in FallbackStrategy:

```python
from uniinfer import ChatMessage, ChatCompletionRequest, FallbackStrategy

# Create a request
request = ChatCompletionRequest(
    messages=[
        ChatMessage(role="user", content="What are three facts about quantum computing?")
    ],
    temperature=0.7,
    max_tokens=200
)

# Create a fallback strategy with providers to try in order
fallback = FallbackStrategy(["mistral", "anthropic", "openai"])

# Try providers in order until one succeeds
response, provider_used = fallback.complete(request)
print(f"Response from {provider_used}: {response.message.content}")
```

## Supported Providers 🤖

| Provider            | Example Models                     | Streaming | Auth Method       |
| ------------------- | ---------------------------------- | --------- | ----------------- |
| **OpenAI**          | GPT-4, GPT-4 Turbo                 | ✅        | API Key           |
| **Anthropic**       | Claude 3 Opus, Sonnet              | ✅        | API Key           |
| **Mistral**         | Mistral 8x7B, Mixtral              | ✅        | API Key           |
| **Ollama**          | Local/self-hosted models           | ✅        | None              |
| **OpenRouter**      | 60+ models incl. Claude 2          | ✅        | API Key           |
| **Google Gemini**   | Gemini Pro, Gemini Flash           | ✅        | API Key           |
| **HuggingFace**     | Llama 2, Mistral                   | ✅        | API Key/Inference |
| **Cohere**          | Command R+                         | ✅        | API Key           |
| **Groq**            | Llama 3.1 8B/70B                   | ✅        | API Key           |
| **AI21**            | Jamba models                       | ✅        | API Key           |
| **InternLM**        | InternLM models                    | ✅        | API Key           |
| **Moonshot**        | Moonshot models                    | ✅        | API Key           |
| **StepFun**         | Step-1 models                      | ✅        | API Key           |
| **Upstage**         | Solar models                       | ✅        | API Key           |
| **NGC**             | NVIDIA GPU Cloud                   | ✅        | API Key           |
| **Cloudflare**      | Workers AI models                  | ✅        | API Key + Account |

Below are examples for some of our newer providers:

### Gemini (Google)

```python
# Requires google-generativeai package
# pip install google-generativeai

provider = ProviderFactory.get_provider("gemini", api_key="your-gemini-api-key")

request = ChatCompletionRequest(
    messages=[
        ChatMessage(role="system", content="You are a helpful assistant."),
        ChatMessage(role="user", content="Tell me about language models.")
    ],
    model="gemini-1.5-pro",  # or gemini-1.5-flash, etc.
    temperature=0.7
)

response = provider.complete(request)
print(response.message.content)

# Or stream the response
for chunk in provider.stream_complete(request):
    print(chunk.message.content, end="", flush=True)
```

### NVIDIA GPU Cloud (NGC)

```python
# Requires openai package
# pip install openai

provider = ProviderFactory.get_provider("ngc", api_key="your-ngc-api-key")

request = ChatCompletionRequest(
    messages=[
        ChatMessage(role="user", content="Explain how transformers work in machine learning")
    ],
    model="deepseek-ai/deepseek-r1-distill-llama-8b",  # NGC model
    temperature=0.6,
    max_tokens=4096
)

# Get a completion
response = provider.complete(request)
print(response.message.content)

# Or stream the response
for chunk in provider.stream_complete(request):
    print(chunk.message.content, end="", flush=True)
```

### Cloudflare Workers AI

```python
# Requires requests package
# pip install requests

provider = ProviderFactory.get_provider(
    "cloudflare", 
    api_key="your-cloudflare-api-token",
    account_id="your-cloudflare-account-id"
)

request = ChatCompletionRequest(
    messages=[
        ChatMessage(role="user", content="Write a 50-word essay about hello world.")
    ],
    model="@cf/meta/llama-2-7b-chat-int8",  # Cloudflare model
    temperature=0.7
)

# Get a completion
response = provider.complete(request)
print(response.message.content)

# Or stream the response
for chunk in provider.stream_complete(request):
    print(chunk.message.content, end="", flush=True)
```

## Adding a New Provider 💻

Extend UniInfer with custom providers in 3 steps:

1. **Create Provider Class**  
   Implement required methods in `providers/your_provider.py`
2. **Register Provider**  
   Add to `ProviderFactory` registry
3. **Test Integration**  
   Use our validation suite

### 1. Create the Provider Class

Create a new file in `uniinfer/providers/` (e.g., `myprovider.py`) with your provider implementation:

```python
from typing import Dict, Any, Iterator, Optional
from ..core import ChatProvider, ChatCompletionRequest, ChatCompletionResponse, ChatMessage

class MyProvider(ChatProvider):
    """Provider for MyLLM API."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(api_key)
        # Initialize any client libraries or connection details
        # self.client = SomeClient(api_key=self.api_key)

    def complete(self, request: ChatCompletionRequest, **provider_specific_kwargs) -> ChatCompletionResponse:
        # Implement standard completion method
        # 1. Prepare messages/parameters for your API
        # 2. Make the API call
        # 3. Process the response
        # 4. Return a ChatCompletionResponse object

        # Example implementation:
        message = ChatMessage(
            role="assistant",
            content="Response from API"
        )

        return ChatCompletionResponse(
            message=message,
            provider='myprovider',
            model=request.model,
            usage={},  # Token usage if available
            raw_response={}  # The raw API response
        )

    def stream_complete(self, request: ChatCompletionRequest, **provider_specific_kwargs) -> Iterator[ChatCompletionResponse]:
        # Implement streaming completion method
        # Yield ChatCompletionResponse objects for each chunk

        # Example implementation:
        yield ChatCompletionResponse(
            message=ChatMessage(role="assistant", content="Streamed chunk"),
            provider='myprovider',
            model=request.model,
            usage={},
            raw_response={}
        )
```

### 2. Update `providers/__init__.py`

Add your provider to the `__init__.py` file in the providers directory:

```python
from .myprovider import MyProvider

# Add to __all__
__all__ = [
    # existing providers
    'MyProvider'
]
```

### 3. Register the Provider in `__init__.py`

Register your provider in the main `__init__.py` file:

```python
from .providers import MyProvider

# Register the provider
ProviderFactory.register_provider("myprovider", MyProvider)

# Add to __all__
__all__ = [
    # existing exports
    'MyProvider'
]
```

### 4. Use Your Provider

Now you can use your provider with the unified interface:

```python
from uniinfer import ChatMessage, ChatCompletionRequest, ProviderFactory

provider = ProviderFactory.get_provider("myprovider", api_key="your-api-key")

request = ChatCompletionRequest(
    messages=[ChatMessage(role="user", content="Hello!")],
    model="your-model-name"
)

response = provider.complete(request)
```

### 5. Advanced: Conditional Dependencies

If your provider requires an optional package, make it conditional:

```python
# In providers/__init__.py
try:
    from .myprovider import MyProvider
    HAS_MYPROVIDER = True
except ImportError:
    HAS_MYPROVIDER = False

# In main __init__.py
if HAS_MYPROVIDER:
    ProviderFactory.register_provider("myprovider", MyProvider)
    __all__.append('MyProvider')
```

This pattern allows UniInfer to work even if the dependency for your provider isn't installed.

## Error Handling

UniInfer provides standardized error handling:

```python
from uniinfer import ProviderFactory
from uniinfer.errors import AuthenticationError, RateLimitError, TimeoutError, ProviderError

try:
    provider = ProviderFactory.get_provider("openai", api_key="invalid-key")
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

## API Reference

### Core Classes

- **ChatMessage**: Represents a message in a chat conversation
  - `role`: The role of the message sender (user, assistant, system)
  - `content`: The content of the message
  - `to_dict()`: Convert to a dictionary format

- **ChatCompletionRequest**: Represents a request for a chat completion
  - `messages`: List of ChatMessage objects
  - `model`: The model to use (optional)
  - `temperature`: Controls randomness (0-1)
  - `max_tokens`: Maximum tokens to generate (optional)
  - `streaming`: Whether to stream the response

- **ChatCompletionResponse**: Represents a response from a chat completion
  - `message`: The generated ChatMessage
  - `provider`: Name of the provider that generated the response
  - `model`: The model used for generation
  - `usage`: Token usage information
  - `raw_response`: The raw response from the provider

- **ChatProvider**: Abstract base class for chat providers
  - `complete(request, **kwargs)`: Make a chat completion request
  - `stream_complete(request, **kwargs)`: Stream a chat completion response

- **ProviderFactory**: Factory for creating provider instances
  - `get_provider(name, api_key=None)`: Get a provider instance
  - `register_provider(name, provider_class)`: Register a provider
  - `list_providers()`: List all registered providers

### Strategies

- **FallbackStrategy**: Tries providers in order until one succeeds
  - `complete(request, **kwargs)`: Make a request with fallback
  - `stream_complete(request, **kwargs)`: Stream with fallback
  - `get_stats()`: Get provider statistics

- **CostBasedStrategy**: Selects providers based on cost
  - `complete(request, **kwargs)`: Make a request with the cheapest provider
  - `stream_complete(request, **kwargs)`: Stream with the cheapest provider

## Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Create a new Pull Request

Before contributing, please read our [Contribution Guidelines](CONTRIBUTING.md).

## License

[MIT License](LICENSE)

---

**UniInfer** is designed to make working with multiple LLM providers as simple as possible. We're continuously adding support for new providers and features.

For issues, feature requests, or contributions, please visit our [GitHub repository](https://github.com/your-username/uniinfer).
