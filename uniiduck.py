#!/usr/bin/env python3
"""
UniDuck - Combined News Search and AI Summarization

Combines DuckNews search with uniinfer's summarization capabilities.
Optimized version with caching, better error handling, and improved article processing.
"""

from typing import List, Dict, Generator, Optional, Tuple, Any
import requests
import os
import hashlib
import time
import logging
import argparse
import json
from functools import lru_cache
from colorama import Fore, Style, init
from uniinfer import (
    ChatMessage,
    ChatCompletionRequest,
    ProviderFactory,
    ChatProvider
)
from credgoo import get_api_key
from providers_config import PROVIDER_CONFIGS

# Initialize colorama
init(autoreset=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
API_BASE_URL = "https://amd1.mooo.com/api/duck/news"
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.cache')
CACHE_EXPIRY = 1800  # 30 minutes in seconds

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)


class ColorHandler:
    """Handles colored text output for the terminal."""

    @staticmethod
    def title(text):
        return f"{Fore.BLUE}{Style.BRIGHT}{text}{Style.RESET_ALL}"

    @staticmethod
    def meta(text):
        return f"{Fore.LIGHTBLACK_EX}{text}{Style.RESET_ALL}"

    @staticmethod
    def link(text):
        return f"{Fore.CYAN}{text}{Style.RESET_ALL}"

    @staticmethod
    def error(text):
        return f"{Fore.RED}{text}{Style.RESET_ALL}"

    @staticmethod
    def success(text):
        return f"{Fore.GREEN}{text}{Style.RESET_ALL}"


def search_news(topic: str, bearer_token: str, max_results: int = 8) -> List[Dict]:
    """Fetch news articles from the API endpoint.

    Args:
        topic (str): The news topic to search for
        bearer_token (str): Authentication token for the API
        max_results (int, optional): Maximum number of results to return. Defaults to 8.

    Returns:
        List[Dict]: List of news articles
    """
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {bearer_token}"
    }

    params = {"topic": topic}

    try:
        response = requests.get(
            API_BASE_URL,
            headers=headers,
            params=params,
            timeout=10  # Add a timeout
        )
        response.raise_for_status()

        data = response.json()
        # Extract articles from the 'results' array in the response
        results = data.get('results', [])
        # Limit results if needed
        return results[:max_results] if max_results else results

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch news: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse API response: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in search_news: {str(e)}")
        return []


@lru_cache(maxsize=32)
def get_provider(provider_name: str) -> ChatProvider:
    """Get a provider instance with caching.

    Args:
        provider_name: Name of the provider to use

    Returns:
        ChatProvider: Initialized provider instance
    """
    if provider_name not in PROVIDER_CONFIGS:
        logger.warning(
            f"Provider '{provider_name}' not found in configuration. Falling back to 'internlm'.")
        provider_name = 'internlm'

    try:
        return ProviderFactory.get_provider(
            name=provider_name,
            api_key=get_api_key(provider_name),
        )
    except Exception as e:
        logger.error(f"Failed to initialize provider {provider_name}: {e}")
        raise


def filter_articles(articles: List[Dict]) -> List[Dict]:
    """Filter articles to remove duplicates and low-quality content.

    Args:
        articles: List of article dictionaries

    Returns:
        List[Dict]: Filtered list of articles
    """
    if not articles:
        return []

    # Remove articles with empty bodies or titles
    articles = [art for art in articles if art.get(
        'body', '').strip() and art.get('title', '').strip()]

    # Remove duplicate articles (based on content similarity)
    unique_articles = []
    seen_content = set()

    for article in articles:
        # Create a simplified version of the content for comparison
        # Using both title and first part of body for better duplication detection
        content_hash = hashlib.md5(
            (article.get('title', '') + article['body'][:100]).lower().encode()
        ).hexdigest()

        if content_hash not in seen_content:
            seen_content.add(content_hash)
            unique_articles.append(article)

    return unique_articles


def create_summary_prompt(topic: str, articles_text: str) -> str:
    """Create an optimized prompt for article summarization.

    Args:
        topic: The news topic
        articles_text: Combined article text

    Returns:
        str: Formatted prompt for the AI model
    """
    return (
        f"Analyze these news articles about {topic}:\n"
        f"1. What is the overall sentiment (positive, negative, or neutral)?\n"
        f"2. What are the 2-3 most important facts or developments?\n"
        f"3. Are there any conflicting viewpoints presented?\n\n"
        f"Synthesize this information into a concise summary with key insights.\n\n"
        f"{articles_text}"
    )


def summarize_articles(text: str, topic: str, provider_name: str, max_length: int = 1000) -> Generator[str, None, str]:
    """Summarize articles using the specified AI provider.

    Args:
        text: The combined article text
        topic: The news topic
        provider_name: The AI provider to use
        max_length: Maximum summary length in tokens

    Yields:
        String chunks of the summary as they are generated

    Returns:
        The complete summary
    """
    try:
        # Get provider with caching
        provider = get_provider(provider_name)

        # Create optimized prompt
        prompt = create_summary_prompt(topic, text)

        # Prepare request
        messages = [ChatMessage(role="user", content=prompt)]
        request = ChatCompletionRequest(
            messages=messages,
            model=PROVIDER_CONFIGS[provider_name]['default_model'],
            max_tokens=max_length,
            streaming=True
        )

        logger.info(f"Generating summary using {provider_name}...")
        summary = ""

        try:
            for chunk in provider.stream_complete(request):
                content = chunk.message.content
                if content:  # Check if content is not empty
                    summary += content
                    yield content
            return summary
        except Exception as e:
            error_msg = f"Error during streaming: {e}"
            logger.error(error_msg)
            # Yield the error message so the user sees it
            yield f"\n{ColorHandler.error(error_msg)}"
            return summary
    except Exception as e:
        error_msg = f"Summarization failed: {e}"
        logger.error(error_msg)
        yield ColorHandler.error(error_msg)
        return ""


def get_cached_news(topic: str, bearer_token: str, max_results: int) -> Tuple[List[Dict], bool]:
    """Get news with caching to avoid redundant API calls.

    Args:
        topic: News topic to search for
        bearer_token: API authentication token
        max_results: Maximum number of results to return

    Returns:
        Tuple[List[Dict], bool]: (articles, from_cache) where from_cache indicates if results came from cache
    """
    # Create a cache key based on the search parameters
    cache_key = f"{hashlib.md5(f'{topic}_{max_results}'.encode(
    )).hexdigest()}.cache"
    cache_path = os.path.join(CACHE_DIR, cache_key)

    # Check if we have a recent cache
    if os.path.exists(cache_path):
        cache_time = os.path.getmtime(cache_path)
        if time.time() - cache_time < CACHE_EXPIRY:
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f), True
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")

    # No valid cache, fetch from API
    logger.info(f"Fetching news for topic: {topic}")
    articles = search_news(topic, bearer_token, max_results=max_results)

    # Save to cache
    if articles:
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(articles, f)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    return articles, False


def format_article_text(articles: List[Dict]) -> str:
    """Format articles into text for summarization.

    Args:
        articles: List of article dictionaries

    Returns:
        Formatted text containing all articles
    """
    combined_text = ""
    for i, art in enumerate(articles):
        article_text = f"Article {i+1}:\n"
        if 'title' in art:
            article_text += f"Title: {art['title']}\n"
        if 'source' in art:
            article_text += f"Source: {art['source']}\n"
        if 'date' in art:
            article_text += f"Date: {art['date']}\n"
        article_text += f"Content: {art.get('body', 'No content available')}\n\n"
        combined_text += article_text

    return combined_text


def main():
    """Main function to run the UniDuck application."""
    parser = argparse.ArgumentParser(description='Search and summarize news')
    parser.add_argument('topic', help='News topic to search and summarize')
    parser.add_argument('-n', '--num-articles', type=int, default=5,
                        help='Number of articles to summarize')
    parser.add_argument('-l', '--max-length', type=int, default=1000,
                        help='Maximum summary length in tokens')
    parser.add_argument('--no-cache', action='store_true',
                        help='Disable caching of API responses')
    parser.add_argument('-p', '--provider', type=str, default='internlm',
                        help='AI provider to use for summarization')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose logging')

    args = parser.parse_args()

    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Get API token
        bearer_token = get_api_key('amd1')
        if not bearer_token:
            print(ColorHandler.error("Failed to get API token"))
            return 1

        # Get articles (from cache if available and not disabled)
        if args.no_cache:
            articles, from_cache = search_news(args.topic, bearer_token,
                                               max_results=args.num_articles), False
        else:
            articles, from_cache = get_cached_news(args.topic, bearer_token,
                                                   max_results=args.num_articles)

        if from_cache:
            print(ColorHandler.meta("Using cached news results"))

        if not articles:
            print(ColorHandler.error(
                "No articles found for the topic: " + args.topic))
            return 1

        # Filter articles to remove duplicates and low-quality content
        filtered_articles = filter_articles(articles)
        if len(filtered_articles) < len(articles):
            print(ColorHandler.meta(
                f"Filtered out {len(articles) - len(filtered_articles)} duplicate or low-quality articles"))

        if not filtered_articles:
            print(ColorHandler.error("No quality articles found after filtering"))
            return 1

        articles = filtered_articles

        # Format the articles for summarization
        combined_text = format_article_text(articles)

        # Validate provider exists in config
        provider_name = args.provider
        if provider_name not in PROVIDER_CONFIGS:
            print(ColorHandler.error(
                f"Provider '{provider_name}' not found in configuration"))
            print(ColorHandler.meta(
                f"Available providers: {', '.join(PROVIDER_CONFIGS.keys())}"))
            provider_name = 'internlm'  # Fallback to default
            print(ColorHandler.meta(
                f"Falling back to default provider: {provider_name}"))

        # Print summary header
        print("\n" + ColorHandler.title("=== News Summary ===") + "\n")
        print(f"Topic: {ColorHandler.title(args.topic)}")
        print(
            f"Provider: {ColorHandler.meta(provider_name)}@{ColorHandler.meta(PROVIDER_CONFIGS[provider_name]['default_model'])}")
        print(f"Articles: {ColorHandler.meta(str(len(articles)))}")
        print("\n" + ColorHandler.title("=== Generating Summary ===") + "\n")

        # Generate summary
        start_time = time.time()
        summary = ""

        try:
            for chunk in summarize_articles(combined_text, args.topic, provider_name, args.max_length):
                print(chunk, end="", flush=True)
                summary += chunk

            # Show completion time
            elapsed = time.time() - start_time
            print(
                f"\n\n{ColorHandler.meta(f'Summary generated in {elapsed:.2f} seconds')}")
            return 0

        except Exception as e:
            print(ColorHandler.error(f"\nError during summarization: {e}"))
            return 1

    except KeyboardInterrupt:
        print(ColorHandler.meta("\nOperation cancelled by user"))
        return 130
    except Exception as e:
        print(ColorHandler.error(f"Unexpected error: {e}"))
        logger.exception("Unexpected error in main function")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
