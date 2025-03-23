"""
Example demonstrating the built-in strategies.
"""
import sys
import os

# Add the parent directory to the Python path to make the uniinfer package importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from credgoo import get_api_key
    HAS_CREDGOO = True
except ImportError:
    HAS_CREDGOO = False
    print("credgoo not found, you'll need to provide API keys manually")

from uniinfer import (
    ChatMessage, ChatCompletionRequest, ProviderFactory,
    FallbackStrategy, CostBasedStrategy
)
from uniinfer.errors import ProviderError


def main():
    # Define provider order for fallback
    providers = ["mistral", "anthropic", "openai"]
    
    # Create a fallback strategy
    fallback = FallbackStrategy(providers)
    
    # Create a chat request
    messages = [
        ChatMessage(role="system", content="You are a helpful assistant that provides concise responses."),
        ChatMessage(role="user", content="Explain how machine learning differs from traditional programming.")
    ]
    
    request = ChatCompletionRequest(
        messages=messages,
        temperature=0.7,
        max_tokens=150
    )
    
    print("Attempting completion with fallback strategy...")
    
    try:
        # Try to get a completion with fallback
        response, provider_used = fallback.complete(request)
        
        # Print the response
        print("\nResponse from:", provider_used)
        print(f"Model: {response.model}")
        print(f"Content: {response.message.content}")
        print(f"Usage: {response.usage}")
        
        # Show fallback statistics
        print("\nProvider Statistics:")
        stats = fallback.get_stats()
        for provider, provider_stats in stats.items():
            print(f"  {provider}:")
            for stat, value in provider_stats.items():
                if isinstance(value, float):
                    print(f"    {stat}: {value:.3f}")
                else:
                    print(f"    {stat}: {value}")
    
    except ProviderError as e:
        print(f"All providers failed: {str(e)}")
    
    print("\n\nNow trying with cost-based strategy...")
    
    # Define costs per 1K tokens (approximate values)
    provider_costs = {
        "mistral": 0.7,
        "anthropic": 1.5,
        "openai": 2.0
    }
    
    # Create a cost-based strategy
    cost_strategy = CostBasedStrategy(provider_costs)
    
    try:
        # The cost-based strategy should choose the cheapest provider
        response, provider_used = cost_strategy.complete(request)
        
        print("\nResponse from:", provider_used)
        print(f"Model: {response.model}")
        print(f"Content: {response.message.content}")
        print(f"Usage: {response.usage}")
    except ProviderError as e:
        print(f"All providers failed: {str(e)}")


if __name__ == "__main__":
    main()
