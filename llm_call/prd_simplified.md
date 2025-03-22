# UniInfer: Unified Inference API

## Simplified Product Requirements Document

### 1. Executive Summary

UniInfer is a lightweight Python package that provides a unified interface for making LLM chat completion requests across multiple providers. It abstracts away provider-specific implementation details while maintaining a simple, intuitive API for developers.

### 2. Problem Statement

- Different LLM providers use inconsistent APIs and parameters
- Switching between providers requires significant code changes
- Authentication and error handling vary across services
- Managing multiple SDKs increases complexity and maintenance burden

### 3. Core Requirements

#### 3.1 Unified Interface
- Simple, consistent methods for chat completion requests
- Support for both standard and streaming responses
- Common parameters across all providers (messages, temperature, max_tokens)

#### 3.2 Provider Support
- Initial support for key providers: Anthropic, OpenAI, Mistral
- Extensible design for easy addition of more providers
- Provider-specific parameters exposed when needed

#### 3.3 Authentication
- Integration with credgoo for API key management (`get_api_key('provider_name')`)
- Option for direct API key input

### 4. Implementation Plan

#### Phase 1: Core Framework (MVP)
1. Implement base classes (ChatMessage, ChatCompletionRequest, ChatCompletionResponse)
2. Create abstract ChatProvider interface
3. Implement ProviderFactory for provider registration and instantiation
4. Add support for Mistral provider with basic authentication

#### Phase 2: Provider Expansion
1. Add support for Anthropic provider
2. Add support for OpenAI provider
3. Implement basic error handling and standardization

#### Phase 3: Enhancements
1. Add robust error handling and retries
2. Implement simple fallback strategy
3. Add streaming support for all providers
4. Create examples and documentation

### 5. API Design

```python
# Core classes
class ChatMessage:
    def __init__(self, role: str, content: str)

class ChatCompletionRequest:
    def __init__(
        self, 
        messages: List[ChatMessage], 
        model: str = None, 
        temperature: float = 1.0, 
        max_tokens: int = None, 
        streaming: bool = False
    )

class ChatCompletionResponse:
    def __init__(
        self, 
        message: ChatMessage, 
        provider: str, 
        model: str, 
        usage: Dict, 
        raw_response: Any
    )

# Base Provider Interface
class ChatProvider:
    def complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> ChatCompletionResponse
    
    def stream_complete(
        self, 
        request: ChatCompletionRequest, 
        **provider_specific_kwargs
    ) -> Iterator[ChatCompletionResponse]

# Provider Factory
class ProviderFactory:
    @staticmethod
    def get_provider(name: str, api_key: str = None) -> ChatProvider
    
    @staticmethod
    def register_provider(name: str, provider_class: Type[ChatProvider])
```

### 6. Usage Examples

```python
# Simple usage
from uniinfer import ChatMessage, ChatCompletionRequest, ProviderFactory
from credgoo import get_api_key

# Get provider with credgoo integration
api_key = get_api_key("mistral")
provider = ProviderFactory.get_provider("mistral", api_key=api_key)

# Create request
request = ChatCompletionRequest(
    messages=[
        ChatMessage(role="user", content="What is machine learning?")
    ],
    model="mistral-small-latest",
    temperature=0.7,
    max_tokens=200
)

# Get completion
response = provider.complete(request)
print(response.message.content)

# Streaming example
for chunk in provider.stream_complete(request):
    print(chunk.message.content, end="", flush=True)
```

### 7. Success Metrics

- Clean, minimal API that requires less than 10 lines to implement a basic call
- Support for at least 3 major providers in initial release
- Consistent error handling across providers
- Minimal performance overhead compared to direct API calls
