#!/usr/bin/env python3
"""
DuckNews - A Command-Line DuckDuckGo Search Tool

This script provides a command-line interface for searching news, text, maps, and translations
using the DuckDuckGo search engine. It leverages the duckduckgo_search Python package to
perform searches and displays the results in a formatted, readable manner in the terminal.

Features:
- News search: Find recent news articles on a specific topic
- Text search: Perform general web searches on any topic
- Maps search: Look up locations and addresses
- Translation: Translate text to different languages

Usage:
    python ducknews.py news "search topic"                  # Search for news articles
    python ducknews.py text "search topic"                  # Perform a general web search
    python ducknews.py maps "search topic" --place="city"   # Search for locations
    python ducknews.py translate "text" --to_language="de"  # Translate text

Results are displayed with formatting for better readability, including color highlighting
for titles, content snippets, and links. News results are sorted by age (most recent first).
"""

from colorama import Fore, Style
import colorama
from typing import Optional, List, Dict
import argparse
from duckduckgo_search import DDGS
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)

colorama.init()


class ColorHandler:
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


def search_news(topic: str, region: str = 'wt-wt', max_results: int = 8) -> List[Dict]:
    valid_regions = ['wt-wt', 'us-en', 'uk-en']
    if region not in valid_regions:
        logging.error(ColorHandler.error(f"Invalid region: {region}"))
        region = 'wt-wt'

    for attempt in range(3):
        try:
            results = DDGS().news(
                keywords=topic,
                region=region,
                safesearch="off",
                timelimit="m",
                max_results=max_results
            )
            return results
        except Exception as e:
            logging.error(ColorHandler.error(
                f"Attempt {attempt+1}/3 failed: {str(e)}"
            ))
    return []


def search_text(topic):
    try:
        results = DDGS().text(topic, max_results=5)
        return results
    except Exception as e:
        logging.error(f"Error searching for text: {e}")
        return []


def search_maps(topic, place):
    if not isinstance(place, str) or len(place.strip()) == 0:
        logging.error(ColorHandler.error(f"Invalid place: {place}"))
        return []

    for attempt in range(3):
        try:
            results = DDGS().maps(topic, place=place, max_results=20)
            return results
        except Exception as e:
            logging.error(ColorHandler.error(
                f"Maps search attempt {attempt+1}/3 failed: {str(e)}"
            ))
    return []


def search_translate(topic, to_language):
    try:
        results = DDGS().translate(topic, to=to_language)
        return results
    except Exception as e:
        logging.error(f"Error translating: {e}")
        return []


def format_results_news(results: List[Dict]):
    if not results:
        print(ColorHandler.meta("No news results found"))
        return

    for result in results:
        try:
            result['age'] = age_of_article(result['date'])
        except KeyError:
            result['age'] = "Date unknown"

    sorted_results = sorted(results, key=lambda x: x.get('age', ''))

    for counter, result in enumerate(sorted_results, start=1):
        print(f"\n{ColorHandler.title(f'{counter}. {result['title']}')}    {
              result['age']}")
        print(f"   {ColorHandler.meta(format_text(result['body'], 100))}")
        print(f"   {ColorHandler.link(f'Link: {result['url']}')}")
        print('\n-')


def format_results_text(results):
    for counter, result in enumerate(results, start=1):
        print(f"\n\033[94m\033[1m{counter}. {result['title']}\033[0m")
        print(f"   \033[90m{format_text(result['body'], 100)}\033[0m")
        print(
            f"   \033[34mLink: [{result['href'].split('/')[2]}]({result['href']})\033[0m")
        print('\n-')


def format_results_maps(results):
    if not results:
        print(ColorHandler.meta("No maps results found"))
        return

    for counter, result in enumerate(results, start=1):
        print(f"\n{ColorHandler.title(f'{counter}. {result['title']}')}")

        if result.get('address'):
            print(f"   {ColorHandler.meta('Address:')} {result['address']}")

        if result.get('phone'):
            print(f"   {ColorHandler.meta('Phone:')} {result['phone']}")

        if result.get('url'):
            print(f"   {ColorHandler.link(f'Website: {result["url"]}')}")

        if result.get('rating'):
            rating_str = f"{result['rating']}/5"
            if result.get('ratings'):
                rating_str += f" ({result['ratings']} reviews)"
            print(f"   {ColorHandler.meta('Rating:')} {rating_str}")

        print('\n-')


def format_results_translate(results):
    for counter, result in enumerate([results], start=1):
        print(
            f"\n\033[94m\033[1m{counter}. Detected Language: {result['detected_language']}\033[0m")
        print(f"   \033[90mTranslated: {result['translated']}\033[0m")
        print(f"   \033[90mOriginal: {result['original']}\033[0m")
        print('\n-')


def age_of_article(date):
    """
    Calculate the age of an article in days based on its date.

    Parameters:
    - date (str): The publication date of the article in 'YYYY-MM-DD' format.

    Returns:
    - str: The age of the article in days, formatted as "+Xd" where X is the number of days.
    """
    # Parse the article's date
    article_date = datetime.fromisoformat(date.replace("Z", "+00:00"))

    # Calculate the difference between now (in UTC) and the article's date
    current_date = datetime.now(timezone.utc)
    age_delta = current_date - article_date

    # Return the age of the article in days
    return f"+{age_delta.days}d"


def print_dict_structure(d, indent=0):
    for key, value in d.items():
        print('    ' * indent + str(key), end='')
        if isinstance(value, dict):
            print(": {")
            print_dict_structure(value, indent+1)
            print('    ' * indent + '}')
        else:
            print(": " + str(type(value).__name__))


def format_text(text, max_line_length, tabs=0):
    words = text.split()
    formatted_lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= max_line_length:
            current_line += (word + " ")
        else:
            formatted_lines.append(current_line.rstrip())
            current_line = word + " "
    # also append tabs number of spaces before each line
    current_line = " " * tabs + current_line
    formatted_lines.append(current_line.rstrip())  # Add the last line

    return "\n".join(formatted_lines)


def main():
    parser = argparse.ArgumentParser(
        description="Search for news, text, maps, or translate using the DuckDuckGo.com search engine.")
    parser.add_argument('search_type', choices=[
                        'news', 'text', 'maps', 'translate'], help="Type of search to perform")
    parser.add_argument('search_topic', help="Topic to search for")
    parser.add_argument('--place', help="Place to search for in maps")
    parser.add_argument('--to_language', help="Language to translate to")
    args = parser.parse_args()

    if args.search_type == 'news':
        logging.info(f"Searching for news on topic: {args.search_topic}")
        results = search_news(args.search_topic)
        if results:
            format_results_news(results)
        else:
            logging.info("No results found.")
    elif args.search_type == 'text':
        logging.info(f"Searching for text on topic: {args.search_topic}")
        results = search_text(args.search_topic)
        if results:
            format_results_text(results)
        else:
            logging.info("No results found.")
    elif args.search_type == 'maps':
        logging.info(
            f"Searching for maps on topic: {args.search_topic} in {args.place}")
        results = search_maps(args.search_topic, args.place)
        if results:
            format_results_maps(results)
        else:
            logging.info("No results found.")
    elif args.search_type == 'translate':
        logging.info(f"Translating: {args.search_topic} to {args.to_language}")
        results = search_translate(args.search_topic, args.to_language)
        if results:
            format_results_translate(results)
        else:
            logging.info("No results found.")


if __name__ == "__main__":
    main()
