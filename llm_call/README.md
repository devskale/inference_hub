# UniInfer · [![PyPI Version](https://img.shields.io/pypi/v/uniinfer.svg)](https://pypi.org/project/uniinfer/)

**Unified LLM Inference Interface for Python with Seamless API Key Management**

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/uniinfer.svg)](https://pypi.org/project/uniinfer/)
[![Documentation](https://img.shields.io/badge/docs-readthedocs.io-informational)](https://uniinfer.readthedocs.io)

UniInfer provides a consistent Python interface for LLM chat completions across multiple providers with:

- 🚀 Single API for 15+ LLM providers
- 🔑 Seamless API key management with credgoo integration
- ⚡ Real-time streaming support
- 🔄 Automatic fallback strategies
- 🔧 Extensible provider architecture

## Table of Contents

- [Features](#features)
- [Key Benefits](#key-benefits)
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

## Key Benefits

### Secure API Key Management with credgoo

UniInfer integrates with [credgoo](https://github.com/your-org/credgoo) for secure API key management, offering:

- **Centralized Key Storage** - Store all your provider API keys in a personal Google Sheet
- **Secure Retrieval** - Keys are encrypted and secured via token authentication
- **Seamless Provider Switching** - Change providers without managing keys in code
- **Development Simplicity** - No more hardcoded API keys or environment variables

With credgoo integration, switching between providers becomes trivial:

```python
from credgoo import get_api_key
from uniinfer import ProviderFactory

# Get OpenAI provider
openai_provider = ProviderFactory.get_provider("openai")  # Key retrieved automatically

# Switch to Anthropic with one line
anthropic_provider = ProviderFactory.get_provider("anthropic")  # Key retrieved automatically
```

All provider API keys are stored securely in your personal Google Sheet and automatically retrieved when needed, eliminating the need for hardcoded keys or environment variables in your code.

## Installation

```bash
pip install uniinfer credgoo
```

Or install from source:

```bash
git clone https://github.com/your-username/uniinfer.git
cd uniinfer
pip install -e .
pip install credgoo  # For seamless API key management
```

## Quick Start

### Basic Usage with Automatic Key Management

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

### Easily Switch Between Providers

One of the biggest advantages of UniInfer with credgoo integration is how easily you can switch between providers:

```python
from uniinfer import ChatMessage, ChatCompletionRequest, ProviderFactory

# Create your request once
request = ChatCompletionRequest(
    messages=[
        ChatMessage(role="system", content="You are a helpful assistant."),
        ChatMessage(role="user", content="Explain how nuclear fusion works.")
    ],
    temperature=0.7,
    max_tokens=500
)

# Try different providers with minimal code changes
# API keys are automatically retrieved from your secure credgoo storage

# Using Anthropic Claude
claude_provider = ProviderFactory.get_provider("anthropic")
claude_request = request.copy()
claude_request.model = "claude-3-sonnet-20240229"
claude_response = claude_provider.complete(claude_request)
print(f"Claude response: {claude_response.message.content[:100]}...")

# Using OpenAI
openai_provider = ProviderFactory.get_provider("openai")
openai_request = request.copy()
openai_request.model = "gpt-4"
openai_response = openai_provider.complete(openai_request)
print(f"OpenAI response: {openai_response.message.content[:100]}...")

# Using Gemini
gemini_provider = ProviderFactory.get_provider("gemini")
gemini_request = request.copy()
gemini_request.model = "gemini-1.5-pro"
gemini_response = gemini_provider.complete(gemini_request)
print(f"Gemini response: {gemini_response.message.content[:100]}...")
```

### Streaming Responses

```python
from uniinfer import ChatMessage, ChatCompletionRequest, ProviderFactory

# Get a provider instance with automatic key management
provider = ProviderFactory.get_provider("openai")

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
provider = ProviderFactory.get_provider("openai")  # Key retrieved automatically

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

### Fallback Between Providers

The combination of UniInfer and credgoo makes provider fallback strategies extremely powerful:

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
# All API keys are retrieved automatically from your secure credgoo storage
fallback = FallbackStrategy(["mistral", "anthropic", "openai", "gemini", "cohere"])

# Try providers in order until one succeeds
response, provider_used = fallback.complete(request)
print(f"Response from {provider_used}: {response.message.content}")
```

## Supported Providers 🤖

| Provider            | Example Models                     | Streaming | Auth Method       |
| ------------------- | ---------------------------------- | --------- | ----------------- |
| **OpenAI**          | GPT-4, GPT-4 Turbo                 | ✅        | API Key (credgoo) |
| **Anthropic**       | Claude 3 Opus, Sonnet              | ✅        | API Key (credgoo) |
| **Mistral**         | Mistral 8x7B, Mixtral              | ✅        | API Key (credgoo) |
| **Ollama**          | Local/self-hosted models           | ✅        | None              |
| **OpenRouter**      | 60+ models incl. Claude 2          | ✅        | API Key (credgoo) |
| **Google Gemini**   | Gemini Pro, Gemini Flash           | ✅        | API Key (credgoo) |
| **HuggingFace**     | Llama 2, Mistral                   | ✅        | API Key (credgoo) |
| **Cohere**          | Command R+                         | ✅        | API Key (credgoo) |
| **Groq**            | Llama 3.1 8B/70B                   | ✅        | API Key (credgoo) |
| **AI21**            | Jamba models                       | ✅        | API Key (credgoo) |
| **InternLM**        | InternLM models                    | ✅        | API Key (credgoo) |
| **Moonshot**        | Moonshot models                    | ✅        | API Key (credgoo) |
| **StepFun**         | Step-1 models                      | ✅        | API Key (credgoo) |
| **Upstage**         | Solar models                       | ✅        | API Key (credgoo) |
| **NGC**             | NVIDIA GPU Cloud                   | ✅        | API Key (credgoo) |
| **Cloudflare**      | Workers AI models                  | ✅        | API Key (credgoo) |

Below are examples for some of our newer providers (all using automatic API key management with credgoo):

### Gemini (Google)

```python
# Requires google-generativeai package
# pip install google-generativeai

provider = ProviderFactory.get_provider("gemini")  # API key retrieved automatically

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
```

### NVIDIA GPU Cloud (NGC)

```python
# Requires openai package
# pip install openai

provider = ProviderFactory.get_provider("ngc")  # API key retrieved automatically

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
```

### Cloudflare Workers AI

```python
# Requires requests package
# pip install requests

# With credgoo, your API key is retrieved automatically
# However, account_id is still required as it's specific to each request
provider = ProviderFactory.get_provider(
    "cloudflare", 
    account_id="your-cloudflare-account-id"  # API key retrieved automatically
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

## Error Handling

UniInfer provides standardized error handling:

```python
from uniinfer import ProviderFactory
from uniinfer.errors import AuthenticationError, RateLimitError, TimeoutError, ProviderError

try:
    # Even with wrong API keys, the credgoo integration makes error handling cleaner
    provider = ProviderFactory.get_provider("openai")
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
  - `get_provider(name, api_key=None)`: Get a provider instance (uses credgoo if no key provided)
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

**UniInfer** with credgoo integration is designed to make working with multiple LLM providers as simple and secure as possible. By automatically retrieving API keys from your secure storage, you can focus on building applications instead of managing credentials.

For issues, feature requests, or contributions, please visit our [GitHub repository](https://github.com/your-username/uniinfer).
