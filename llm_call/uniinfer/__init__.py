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
    InternLMProvider, StepFunProvider, SambanovaProvider
)
from .errors import (
    UniInferError, ProviderError, AuthenticationError, 
    RateLimitError, TimeoutError, InvalidRequestError
)
from .strategies import FallbackStrategy, CostBasedStrategy

# Import optional providers conditionally
try:
    from .providers import HuggingFaceProvider
    HAS_HUGGINGFACE = True
except ImportError:
    HAS_HUGGINGFACE = False

try:
    from .providers import CohereProvider
    HAS_COHERE = True
except ImportError:
    HAS_COHERE = False

try:
    from .providers import MoonshotProvider
    HAS_MOONSHOT = True
except ImportError:
    HAS_MOONSHOT = False

try:
    from .providers import GroqProvider
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

# Register built-in providers
ProviderFactory.register_provider("mistral", MistralProvider)
ProviderFactory.register_provider("anthropic", AnthropicProvider)
ProviderFactory.register_provider("openai", OpenAIProvider)
ProviderFactory.register_provider("ollama", OllamaProvider)
ProviderFactory.register_provider("openrouter", OpenRouterProvider)
ProviderFactory.register_provider("arli", ArliAIProvider)
ProviderFactory.register_provider("internlm", InternLMProvider)
ProviderFactory.register_provider("stepfun", StepFunProvider)
ProviderFactory.register_provider("sambanova", SambanovaProvider)

# Register optional providers if available
if HAS_HUGGINGFACE:
    ProviderFactory.register_provider("huggingface", HuggingFaceProvider)

if HAS_COHERE:
    ProviderFactory.register_provider("cohere", CohereProvider)

if HAS_MOONSHOT:
    ProviderFactory.register_provider("moonshot", MoonshotProvider)

if HAS_GROQ:
    ProviderFactory.register_provider("groq", GroqProvider)

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
    'StepFunProvider',
    'SambanovaProvider',
    'UniInferError',
    'ProviderError',
    'AuthenticationError',
    'RateLimitError',
    'TimeoutError',
    'InvalidRequestError',
    'FallbackStrategy',
    'CostBasedStrategy'
]

# Add optional providers to exports if available
if HAS_HUGGINGFACE:
    __all__.append('HuggingFaceProvider')

if HAS_COHERE:
    __all__.append('CohereProvider')

if HAS_MOONSHOT:
    __all__.append('MoonshotProvider')

if HAS_GROQ:
    __all__.append('GroqProvider')
