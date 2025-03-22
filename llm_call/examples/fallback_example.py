"""
Example demonstrating fallback between multiple providers.
"""
import sys
import os
import time

# Add the parent directory to the Python path to make the uniinfer package importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from credgoo import get_api_key
    HAS_CREDGOO = True
except ImportError:
    HAS_CREDGOO = False
    print("credgoo not found, you'll need to provide API keys manually")

from uniinfer import ChatMessage, ChatCompletionRequest, ProviderFactory
from uniinfer.errors import ProviderError


class FallbackProvider:
    """
    Simple fallback mechanism between multiple providers.
    """
    def __init__(self, provider_names):
        """
        Initialize with a list of provider names to try in order.
        """
        self.provider_names = provider_names
        self.providers = {}
        
        # Initialize each provider
        for name in provider_names:
            try:
                if HAS_CREDGOO:
                    api_key = get_api_key(name)
                    self.providers[name] = ProviderFactory.get_provider(name)
                else:
                    api_key = input(f"Enter your {name} API key (leave blank to skip): ")
                    if api_key:
                        self.providers[name] = ProviderFactory.get_provider(name, api_key=api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize {name} provider: {str(e)}")
    
    def complete(self, request, **kwargs):
        """
        Try each provider in order until one succeeds.
        """
        last_error = None
        
        for name in self.provider_names:
            if name not in self.providers:
                continue
                
            provider = self.providers[name]
            try:
                print(f"Trying provider: {name}")
                start_time = time.time()
                response = provider.complete(request, **kwargs)
                elapsed = time.time() - start_time
                print(f"Success with {name} (took {elapsed:.2f}s)")
                return response, name
            except Exception as e:
                last_error = e
                print(f"Error with {name}: {str(e)}")
                continue
        
        # If we get here, all providers failed
        raise ProviderError(f"All providers failed. Last error: {str(last_error)}")


def main():
    # Create a fallback provider with multiple providers
    fallback = FallbackProvider(['mistral', 'anthropic', 'openai'])
    
    # Create a chat request
    messages = [
        ChatMessage(role="user", content="What are three interesting facts about quantum computing?")
    ]
    
    request = ChatCompletionRequest(
        messages=messages,
        temperature=0.7,
        max_tokens=200
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
    except ProviderError as e:
        print(f"All providers failed: {str(e)}")


if __name__ == "__main__":
    main()
