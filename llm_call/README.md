# UniInfer

UniInfer is a lightweight Python package that provides a unified interface for making LLM chat completion requests across multiple providers.

## Features

- **Unified API**: Simple, consistent interface for all LLM providers
- **Multiple Providers**: Support for Mistral, Anthropic, OpenAI, Ollama, OpenRouter, and more
- **Streaming Support**: Both standard and streaming completions for all providers
- **Error Handling**: Standardized error handling across providers
- **Credentials Management**: Integration with credgoo for API key management
- **Extensible**: Easy to add support for additional providers
- **Fallback Strategies**: Built-in support for provider fallback and selection

## Installation

```bash
pip install uniinfer
```

Or install from source:

```bash
git clone <repository-url>
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

## Adding a New Provider

UniInfer is designed to be easily extensible with new providers. Here's how to add a new LLM provider to the library:

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

## Supported Providers

### SambaNova

```python
# Requires openai package
# pip install openai

provider = ProviderFactory.get_provider("sambanova", api_key="your-api-key")

request = ChatCompletionRequest(
    messages=[
        ChatMessage(role="system", content="Answer the question in a couple sentences."),
        ChatMessage(role="user", content="Share a happy story with me")
    ],
    model="Meta-Llama-3.1-8B-Instruct",  # SambaNova's model
    temperature=0.1
)

response = provider.complete(request)
print(response.message.content)
```

### Groq

```python
# Requires groq package
# pip install groq

provider = ProviderFactory.get_provider("groq", api_key="your-api-key")

request = ChatCompletionRequest(
    messages=[
        ChatMessage(role="system", content="You are a helpful assistant."),
        ChatMessage(role="user", content="What makes Groq unique among LLM providers?")
    ],
    model="llama-3.1-8b",  # Also supports "llama-3.1-70b", "llama-3.1-405b", etc.
    temperature=0.7
)

# Streaming response
for chunk in provider.stream_complete(request):
    print(chunk.message.content, end="", flush=True)
```

### StepFun AI

```python
# Requires openai package
# pip install openai

provider = ProviderFactory.get_provider("stepfun", api_key="your-api-key")

request = ChatCompletionRequest(
    messages=[
        ChatMessage(role="system", content="你是由阶跃星辰提供的AI聊天助手，你擅长中文，英文，以及多种其他语言的对话。"),
        ChatMessage(role="user", content="你好，请介绍一下阶跃星辰的人工智能!")
    ],
    model="step-1-8k",  # StepFun model
    temperature=0.3
)

response = provider.complete(request)
```

### Moonshot AI

```python
# Requires openai package
# pip install openai

provider = ProviderFactory.get_provider("moonshot", api_key="your-api-key")

request = ChatCompletionRequest(
    messages=[
        ChatMessage(role="system", content="你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。"),
        ChatMessage(role="user", content="你好，我叫李雷，1+1等于多少？")
    ],
    model="moonshot-v1-8k",  # Moonshot model
    temperature=0.3,
    max_tokens=500
)

response = provider.complete(request)
```

### Cohere

```python
# Requires cohere package
# pip install cohere

provider = ProviderFactory.get_provider("cohere", api_key="your-api-key")

request = ChatCompletionRequest(
    messages=[messages],
    model="command-r-plus-08-2024",  # Cohere model
    temperature=0.8,
    max_tokens=500
)

response = provider.complete(request)

# Streaming
for chunk in provider.stream_complete(request):
    print(chunk.message.content, end="", flush=True)
```

### InternLM

```python
# Recommended: Install OpenAI client for better InternLM compatibility
# pip install openai

provider = ProviderFactory.get_provider("internlm", api_key="your-api-key")

# InternLM-specific parameters
internlm_params = {
    "top_p": 0.9
}

request = ChatCompletionRequest(
    messages=[messages],
    model="internlm3-latest",  # InternLM model
    temperature=0.8,
    max_tokens=500
)

# Pass InternLM-specific parameters
response = provider.complete(request, **internlm_params)
```

### HuggingFace Inference

```python
# Requires huggingface_hub package
# pip install huggingface_hub

provider = ProviderFactory.get_provider("huggingface", api_key="your-api-key")

request = ChatCompletionRequest(
    messages=[messages],
    model="mistralai/Mistral-7B-Instruct-v0.3",  # HuggingFace model path
    temperature=0.7,
    max_tokens=500
)

response = provider.complete(request)
```

### ArliAI

```python
provider = ProviderFactory.get_provider("arli", api_key="your-api-key")

# ArliAI-specific parameters
arli_params = {
    "repetition_penalty": 1.1,
    "top_p": 0.9,
    "top_k": 40,
}

request = ChatCompletionRequest(
    messages=[messages],
    model="Mistral-Nemo-12B-Instruct-2407",  # ArliAI model
    temperature=0.7,
    max_tokens=300
)

# Pass ArliAI-specific parameters
response = provider.complete(request, **arli_params)
```

### Mistral AI

```python
provider = ProviderFactory.get_provider("mistral", api_key="your-api-key")

request = ChatCompletionRequest(
    messages=[messages],
    model="mistral-small-latest",  # or mistral-medium-latest, mistral-large-latest
    temperature=0.7,
    max_tokens=100
)
```

### Anthropic (Claude)

```python
provider = ProviderFactory.get_provider("anthropic", api_key="your-api-key")

request = ChatCompletionRequest(
    messages=[messages],
    model="claude-3-sonnet-20240229",  # or claude-3-opus-20240229, claude-3-haiku-20240229
    temperature=0.7,
    max_tokens=300
)
```

### OpenAI

```python
provider = ProviderFactory.get_provider("openai", api_key="your-api-key")

request = ChatCompletionRequest(
    messages=[messages],
    model="gpt-4",  # or gpt-3.5-turbo, gpt-4-turbo
    temperature=0.7,
    max_tokens=200
)
```

### Ollama (Local Models)

```python
# Connect to a local Ollama instance (default URL: http://localhost:11434)
provider = ProviderFactory.get_provider("ollama")

# Or connect to a remote Ollama instance
provider = ProviderFactory.get_provider("ollama", base_url="https://amp1.mooo.com:11444")

request = ChatCompletionRequest(
    messages=[messages],
    model="llama2",  # or any other model available in your Ollama instance
    temperature=0.7,
    max_tokens=300
)
```

### OpenRouter (Unified API for Multiple Providers)

```python
provider = ProviderFactory.get_provider("openrouter", api_key="your-api-key")

request = ChatCompletionRequest(
    messages=[messages],
    # Use provider/model format to specify models on OpenRouter
    model="openai/gpt-4",  # or anthropic/claude-3-opus-20240229, meta-llama/llama-3-70b-instruct, etc.
    temperature=0.7,
    max_tokens=200
)
```

## Adding Custom Providers

You can extend UniInfer with your own providers:

```python
from uniinfer import ChatProvider, ProviderFactory

class MyCustomProvider(ChatProvider):
    def __init__(self, api_key=None):
        super().__init__(api_key)
        # Your initialization code
    
    def complete(self, request, **kwargs):
        # Your implementation for standard completion
        pass
    
    def stream_complete(self, request, **kwargs):
        # Your implementation for streaming
        pass

# Register your provider
ProviderFactory.register_provider("custom", MyCustomProvider)

# Now you can use it
provider = ProviderFactory.get_provider("custom", api_key="your-api-key")
```

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

### Providers

- **MistralProvider**: Provider for Mistral AI
- **AnthropicProvider**: Provider for Anthropic Claude
- **OpenAIProvider**: Provider for OpenAI
- **OllamaProvider**: Provider for local Ollama instance
- **OpenRouterProvider**: Provider for OpenRouter unified API
- **ArliAIProvider**: Provider for ArliAI API
- **HuggingFaceProvider**: Provider for HuggingFace Inference API (requires huggingface_hub package)
- **InternLMProvider**: Provider for InternLM API
- **CohereProvider**: Provider for Cohere API (requires cohere package)
- **MoonshotProvider**: Provider for Moonshot AI API (requires openai package)
- **StepFunProvider**: Provider for StepFun AI API (requires openai package)
- **GroqProvider**: Provider for Groq API (requires groq package)
- **SambanovaProvider**: Provider for SambaNova AI (requires openai package)

### Strategies

- **FallbackStrategy**: Tries providers in order until one succeeds
  - `complete(request, **kwargs)`: Make a request with fallback
  - `stream_complete(request, **kwargs)`: Stream with fallback
  - `get_stats()`: Get provider statistics

- **CostBasedStrategy**: Selects providers based on cost
  - `complete(request, **kwargs)`: Make a request with the cheapest provider
  - `stream_complete(request, **kwargs)`: Stream with the cheapest provider

### Error Classes

- **UniInferError**: Base exception for all UniInfer errors
- **ProviderError**: Error related to a provider operation
- **AuthenticationError**: Authentication error with a provider
- **RateLimitError**: Rate limit error from a provider
- **TimeoutError**: Timeout error from a provider
- **InvalidRequestError**: Invalid request error

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)
