"""
Provider strategies for UniInfer.
"""
import time
from typing import List, Dict, Any, Iterator, Optional, Tuple

from .core import ChatCompletionRequest, ChatCompletionResponse
from .factory import ProviderFactory
from .errors import ProviderError


class FallbackStrategy:
    """
    Strategy that tries providers in order until one succeeds.
    """
    def __init__(self, provider_names: List[str], max_retries: int = 1):
        """
        Initialize the fallback strategy.
        
        Args:
            provider_names (List[str]): Ordered list of provider names to try.
            max_retries (int): Maximum number of retries per provider.
        """
        self.provider_names = provider_names
        self.max_retries = max_retries
        self.latency_stats: Dict[str, List[float]] = {}
        self.error_counts: Dict[str, int] = {}
    
    def complete(
        self, 
        request: ChatCompletionRequest, 
        **kwargs
    ) -> Tuple[ChatCompletionResponse, str]:
        """
        Make a chat completion request with fallback.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **kwargs: Additional parameters for the provider.
        
        Returns:
            Tuple[ChatCompletionResponse, str]: The response and provider name.
        
        Raises:
            ProviderError: If all providers fail.
        """
        last_error = None
        
        for provider_name in self.provider_names:
            for attempt in range(self.max_retries + 1):
                try:
                    provider = ProviderFactory.get_provider(provider_name)
                    
                    # Measure latency
                    start_time = time.time()
                    response = provider.complete(request, **kwargs)
                    latency = time.time() - start_time
                    
                    # Record successful call
                    self._record_latency(provider_name, latency)
                    
                    return response, provider_name
                    
                except Exception as e:
                    last_error = e
                    
                    # Record error
                    self._record_error(provider_name)
                    
                    # If we've exhausted retries, move on to the next provider
                    if attempt == self.max_retries:
                        continue
        
        # If we get here, all providers failed
        raise ProviderError(f"All providers failed. Last error: {str(last_error)}")
    
    def stream_complete(
        self, 
        request: ChatCompletionRequest, 
        **kwargs
    ) -> Tuple[Iterator[ChatCompletionResponse], str]:
        """
        Stream a chat completion response with fallback.
        
        Args:
            request (ChatCompletionRequest): The request to make.
            **kwargs: Additional parameters for the provider.
        
        Returns:
            Tuple[Iterator[ChatCompletionResponse], str]: An iterator of response chunks and provider name.
        
        Raises:
            ProviderError: If all providers fail.
        """
        last_error = None
        
        for provider_name in self.provider_names:
            for attempt in range(self.max_retries + 1):
                try:
                    provider = ProviderFactory.get_provider(provider_name)
                    
                    # Start streaming
                    stream_iter = provider.stream_complete(request, **kwargs)
                    
                    # Return the streaming iterator and provider name
                    # Note: We can't easily measure latency for streaming
                    return stream_iter, provider_name
                    
                except Exception as e:
                    last_error = e
                    
                    # Record error
                    self._record_error(provider_name)
                    
                    # If we've exhausted retries, move on to the next provider
                    if attempt == self.max_retries:
                        continue
        
        # If we get here, all providers failed
        raise ProviderError(f"All providers failed streaming. Last error: {str(last_error)}")
    
    def _record_latency(self, provider: str, latency: float) -> None:
        """Record latency for a provider."""
        if provider not in self.latency_stats:
            self.latency_stats[provider] = []
        self.latency_stats[provider].append(latency)
        
        # Keep only the last 10 measurements
        if len(self.latency_stats[provider]) > 10:
            self.latency_stats[provider] = self.latency_stats[provider][-10:]
    
    def _record_error(self, provider: str) -> None:
        """Record an error for a provider."""
        if provider not in self.error_counts:
            self.error_counts[provider] = 0
        self.error_counts[provider] += 1
    
    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for each provider.
        
        Returns:
            Dict[str, Dict[str, Any]]: Stats for each provider.
        """
        stats = {}
        
        for provider in set(list(self.latency_stats.keys()) + list(self.error_counts.keys())):
            latencies = self.latency_stats.get(provider, [])
            errors = self.error_counts.get(provider, 0)
            
            stats[provider] = {
                "avg_latency": sum(latencies) / len(latencies) if latencies else None,
                "min_latency": min(latencies) if latencies else None,
                "max_latency": max(latencies) if latencies else None,
                "error_count": errors,
                "call_count": len(latencies) + errors
            }
        
        return stats


class CostBasedStrategy:
    """
    Simple strategy that selects providers based on cost.
    (This is a placeholder implementation - would need actual cost data)
    """
    def __init__(self, provider_costs: Dict[str, float]):
        """
        Initialize with provider costs.
        
        Args:
            provider_costs (Dict[str, float]): Cost per 1000 tokens for each provider.
        """
        self.provider_costs = provider_costs
        self.fallback = FallbackStrategy(
            sorted(provider_costs.keys(), key=lambda p: provider_costs[p])
        )
    
    def complete(self, request, **kwargs):
        """Select cheapest provider and complete request."""
        return self.fallback.complete(request, **kwargs)
    
    def stream_complete(self, request, **kwargs):
        """Select cheapest provider and stream response."""
        return self.fallback.stream_complete(request, **kwargs)
