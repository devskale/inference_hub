"""
UniInfer - Unified Inference API for LLM chat completions

A standardized interface for making chat completion requests across multiple
LLM inference providers.
"""

from .core import ChatMessage, ChatCompletionRequest, ChatCompletionResponse, ChatProvider
from .factory import ProviderFactory
from .providers import (
    MistralProvider, AnthropicProvider, OpenAIProvider,
    OllamaProvider, OpenRouterProvider, ArliAIProvider,
    InternLMProvider
)
from .errors import (
    UniInferError, ProviderError, AuthenticationError, 
    RateLimitError, TimeoutError, InvalidRequestError
)
from .strategies import FallbackStrategy, CostBasedStrategy

# Import HuggingFace provider conditionally (requires huggingface_hub package)
try:
    from .providers import HuggingFaceProvider
    HAS_HUGGINGFACE = True
except ImportError:
    HAS_HUGGINGFACE = False

# Register built-in providers
ProviderFactory.register_provider("mistral", MistralProvider)
ProviderFactory.register_provider("anthropic", AnthropicProvider)
ProviderFactory.register_provider("openai", OpenAIProvider)
ProviderFactory.register_provider("ollama", OllamaProvider)
ProviderFactory.register_provider("openrouter", OpenRouterProvider)
ProviderFactory.register_provider("arli", ArliAIProvider)
ProviderFactory.register_provider("internlm", InternLMProvider)

# Register HuggingFace provider if available
if HAS_HUGGINGFACE:
    ProviderFactory.register_provider("huggingface", HuggingFaceProvider)

__version__ = "0.1.0"

# Export commonly used functions and classes
__all__ = [
    'ChatMessage',
    'ChatCompletionRequest',
    'ChatCompletionResponse',
    'ChatProvider',
    'ProviderFactory',
    'MistralProvider',
    'AnthropicProvider',
    'OpenAIProvider',
    'OllamaProvider',
    'OpenRouterProvider',
    'ArliAIProvider',
    'InternLMProvider',
    'UniInferError',
    'ProviderError',
    'AuthenticationError',
    'RateLimitError',
    'TimeoutError',
    'InvalidRequestError',
    'FallbackStrategy',
    'CostBasedStrategy'
]

# Add HuggingFaceProvider to exports if available
if HAS_HUGGINGFACE:
    __all__.append('HuggingFaceProvider')
