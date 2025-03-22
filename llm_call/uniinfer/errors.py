"""
Error handling for UniInfer.
"""

class UniInferError(Exception):
    """Base exception for all UniInfer errors."""
    pass


class ProviderError(UniInferError):
    """Error related to a provider operation."""
    pass


class AuthenticationError(ProviderError):
    """Authentication error with a provider."""
    pass


class RateLimitError(ProviderError):
    """Rate limit error from a provider."""
    pass


class TimeoutError(ProviderError):
    """Timeout error from a provider."""
    pass


class InvalidRequestError(ProviderError):
    """Invalid request error."""
    pass


def map_provider_error(provider_name: str, original_error: Exception) -> ProviderError:
    """
    Map a provider-specific error to a UniInfer error.
    
    Args:
        provider_name (str): The name of the provider.
        original_error (Exception): The original error.
        
    Returns:
        ProviderError: A standardized UniInfer error.
    """
    error_message = str(original_error).lower()
    
    # Common authentication errors
    if any(term in error_message for term in ["authentication", "auth", "unauthorized", "api key", "401"]):
        return AuthenticationError(f"{provider_name} authentication error: {str(original_error)}")
    
    # Rate limit errors
    if any(term in error_message for term in ["rate limit", "ratelimit", "too many requests", "429"]):
        return RateLimitError(f"{provider_name} rate limit error: {str(original_error)}")
    
    # Timeout errors
    if any(term in error_message for term in ["timeout", "timed out"]):
        return TimeoutError(f"{provider_name} timeout error: {str(original_error)}")
    
    # Invalid request errors
    if any(term in error_message for term in ["invalid", "validation", "bad request", "400"]):
        return InvalidRequestError(f"{provider_name} invalid request: {str(original_error)}")
    
    # Default to generic provider error
    return ProviderError(f"{provider_name} error: {str(original_error)}")
