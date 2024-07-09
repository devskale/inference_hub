import argparse
from duckduckgo_search import DDGS
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)

def search_news(topic):
    try:
        results = DDGS().news(keywords=topic, region="wt-wt", safesearch="off", timelimit="m", max_results=8)
        return results
    except Exception as e:
        logging.error(f"Error searching for news: {e}")
        return []

def search_text(topic):
    try:
        results = DDGS().text(topic, max_results=5)
        return results
    except Exception as e:
        logging.error(f"Error searching for text: {e}")
        return []

def search_maps(topic, place):
    try:
        results = DDGS().maps(topic, place=place, max_results=20)
        return results
    except Exception as e:
        logging.error(f"Error searching for maps: {e}")
        return []

def search_translate(topic, to_language):
    try:
        results = DDGS().translate(topic, to=to_language)
        return results
    except Exception as e:
        logging.error(f"Error translating: {e}")
        return []

def format_results_news(results):
    for result in results:
        result['age'] = age_of_article(result['date'])
    results = sorted(results, key=lambda x: x['age'])
    for counter, result in enumerate(results, start=1):
        print(f"\n\033[94m\033[1m{counter}. {result['title']}\033[0m    {age_of_article(result['date'])}")
        print(f"   \033[90m{format_text(result['body'], 100)}\033[0m")
        print(f"   \033[34mLink: [{result['url'].split('/')[2]}]({result['url']})\033[0m")
        print('\n-')

def format_results_text(results):
    for counter, result in enumerate(results, start=1):
        print(f"\n\033[94m\033[1m{counter}. {result['title']}\033[0m")
        print(f"   \033[90m{format_text(result['body'], 100)}\033[0m")
        print(f"   \033[34mLink: [{result['href'].split('/')[2]}]({result['href']})\033[0m")
        print('\n-')

def format_results_maps(results):
    for counter, result in enumerate(results, start=1):
        print(f"\n\033[94m\033[1m{counter}. {result['title']}\033[0m")
        print(f"   \033[90mAddress: {result['address']}\033[0m")
#        print(f"   \033[90mCountry Code: {result['country_code']}\033[0m")
#        print(f"   \033[34mLink: [{result['url'].split('/')[2]}]({result['url']})\033[0m")
#        print('\n-')

def format_results_translate(results):
    for counter, result in enumerate([results], start=1):
        print(f"\n\033[94m\033[1m{counter}. Detected Language: {result['detected_language']}\033[0m")
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
    parser = argparse.ArgumentParser(description="Search for news, text, maps, or translate using the DuckDuckGo.com search engine.")
    parser.add_argument('search_type', choices=['news', 'text', 'maps', 'translate'], help="Type of search to perform")
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
        logging.info(f"Searching for maps on topic: {args.search_topic} in {args.place}")
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
