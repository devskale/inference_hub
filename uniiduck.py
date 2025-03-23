#!/usr/bin/env python3
"""
UniDuck - Combined News Search and AI Summarization

Combines DuckNews search with uniinfer's summarization capabilities.
"""

from ducknews import search_news, ColorHandler
from uniinfer import (
    ChatMessage,
    ChatCompletionRequest,
    ProviderFactory,
    ChatProvider
)
from providers_config import PROVIDER_CONFIGS
from credgoo import get_api_key
import argparse
import logging

logging.basicConfig(level=logging.INFO)


def summarize_articles(text: str, topic: str, max_length: int = 1000) -> str:
    provider_name = 'internlm'
    try:
        provider = ProviderFactory.get_provider(
            name=provider_name,
            api_key=get_api_key(provider_name),
        )
        messages = [ChatMessage(role="user",
                                content=f"Analyze these news articles about {topic}:\n1. What is the overall sentiment (positive, negative, or neutral)?\nSynthesize these news articles about {topic} into 1-3 key points that capture the main developments or insights:\n\n{text}")]
        request = ChatCompletionRequest(
            messages=messages,
            model=PROVIDER_CONFIGS[provider_name]['default_model'],
            max_tokens=max_length,
            streaming=True
        )

        summary = ""
        for chunk in provider.stream_complete(request):
            content = chunk.message.content
            summary += content
            yield content
        return summary
    except Exception as e:
        logging.error(ColorHandler.error(f"Summarization failed: {e}"))
        return ""


def main():
    parser = argparse.ArgumentParser(description='Search and summarize news')
    parser.add_argument('topic', help='News topic to search and summarize')
    parser.add_argument('-n', '--num-articles', type=int, default=5,
                        help='Number of articles to summarize')
    parser.add_argument('-l', '--max-length', type=int, default=1000,
                        help='Maximum summary length in tokens')

    args = parser.parse_args()

    # Search for news articles
    articles = search_news(args.topic, max_results=args.num_articles)
    if not articles:
        print(ColorHandler.error("No articles found for summarization"))
        return

    # Combine article content
    combined_text = "\n\n".join([
        f"Article {i+1}: {art['body']}"
        for i, art in enumerate(articles)
    ])

    # Generate summary
    print("\n=== News Summary ===\n")
    provider_name = 'openrouter'
    print(
        f"Prompt: {args.topic} ({provider_name}@{PROVIDER_CONFIGS[provider_name]['default_model']})")
    print("\n=== Response ===\n")
    summary = ""
    for chunk in summarize_articles(combined_text, args.topic, args.max_length):
        print(chunk, end="", flush=True)
        summary += chunk

    # Display results
    print(f"\n=== News Summary ===\n")
    print(
        f"Prompt: {args.topic} ({provider_name}@{PROVIDER_CONFIGS[provider_name]['default_model']})")
    print(f"\n=== Response ===\n")
    print(summary)


if __name__ == "__main__":
    main()
