"""
Provider implementations for different LLM services.
"""
from .mistral import MistralProvider
from .anthropic import AnthropicProvider
from .openai import OpenAIProvider
from .ollama import OllamaProvider
from .openrouter import OpenRouterProvider
from .arli import ArliAIProvider
from .internlm import InternLMProvider
from .stepfun import StepFunProvider
from .sambanova import SambanovaProvider
from .upstage import UpstageProvider

# Import providers with optional dependencies
try:
    from .huggingface import HuggingFaceProvider
    HAS_HUGGINGFACE = True
except ImportError:
    HAS_HUGGINGFACE = False

try:
    from .cohere import CohereProvider
    HAS_COHERE = True
except ImportError:
    HAS_COHERE = False

try:
    from .moonshot import MoonshotProvider
    HAS_MOONSHOT = True
except ImportError:
    HAS_MOONSHOT = False

try:
    from .groq import GroqProvider
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

# Import all provider classes here so they can be easily imported from uniinfer.providers
__all__ = [
    'MistralProvider', 
    'AnthropicProvider', 
    'OpenAIProvider',
    'OllamaProvider',
    'OpenRouterProvider',
    'ArliAIProvider',
    'InternLMProvider',
    'StepFunProvider',
    'SambanovaProvider',
    'UpstageProvider'
]

# Add optional providers to __all__ if available
if HAS_HUGGINGFACE:
    __all__.append('HuggingFaceProvider')

if HAS_COHERE:
    __all__.append('CohereProvider')

if HAS_MOONSHOT:
    __all__.append('MoonshotProvider')

if HAS_GROQ:
    __all__.append('GroqProvider')
