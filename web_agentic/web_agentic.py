import logging
import os
import argparse
import sys
import inquirer
import requests
from datetime import datetime
import re
from typing import Dict, List, Any, Optional
from urllib.parse import unquote
from credgoo import get_api_key
from uniinfer import (
    ChatMessage,
    ChatCompletionRequest,
    ProviderFactory,
    ChatProvider
)


llm_providers = {
    "stepfun": {
        "models": {
            "step-2-mini": {
                "description": "chinese top",
                "capabilities": ["general", "chinese"]
            },
        }
    },
    "mistral": {
        "models": {
            "ministral-8b-latest": {
                "description": "small and good",
                "capabilities": ["general"]
            },
            "mistral-large-latest": {
                "description": "mistral large",
                "capabilities": ["general", "instruction"]
            }
        }
    },
    "cloudflare": {
        "models": {
            "discolm-german-7b-v1-awq": {
                "description": "german",
                "capabilities": ["german"]
            },
            "deepseek-r1-distrill-qwen-32b": {
                "description": "deepseek r1",
                "capabilities": ["reasoning"]
            }
        }
    }
}

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fetch_search_results(query: str, num_results: int = 10, api_key: str = None) -> dict | None:
    """
    Fetch search results from the API.

    Args:
        query: Search query string
        num_results: Number of results to return (default: 10)

    Returns:
        Dictionary containing search results or None if error occurs
    """
    try:

        url = f'https://amd1.mooo.com/api/w3m_google?query={query}&num_results={num_results}'
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f'Error fetching search results: {e}')
        return None


def select_search_result(results):
    """
    Present search results using inquirer for user selection

    Args:
        results (list): List of search results

    Returns:
        dict: Selected result
    """
    try:
        import inquirer
        questions = [
            inquirer.List('result',
                          message='Select a search result',
                          choices=[
                              f"{i+1}. {result['title'].split('›')[0][:120]}" for i, result in enumerate(results)],
                          carousel=True)
        ]
        answers = inquirer.prompt(questions)
        selected_title = answers['result']
        selected_index = int(selected_title.split('.')[0]) - 1
        return results[selected_index]
    except ImportError:
        logger.error('Inquirer module not installed')
        return None


def present_results(search_results):
    """
    Present search results in a structured format

    Args:
        search_results (dict): JSON response from search API

    Returns:
        list: Formatted results for display
    """
    formatted_results = []
    if search_results and 'content' in search_results:
        for item in search_results['content']:
            formatted_results.append({
                'id': item['id'],
                'title': item.get('title') or unquote(([p for p in item['url'].split('/') if p][-1] if [p for p in item['url'].split('/') if p] else '')).replace('_', ' ').replace('-', ' ').title(),
                'url': item['url'],
                'description': re.sub(r'\s*[›»•·–—:]\s*\S+.*$', '', item.get('description', 'No description available')).strip()
            })
    return formatted_results


def save_results_to_md(query, results):
    """
    Save search results to a markdown file

    Args:
        query (str): The search query
        results (dict): JSON response from search API
    """
    today = datetime.now().strftime('%Y-%m-%d')
    filename = f'step1_{query.lower().replace(" ", "_")}_{today}.md'
    filepath = os.path.join(os.path.dirname(__file__), filename)

    if os.path.exists(filepath):
        return

    formatted = present_results(results)
    if not formatted:
        return

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f'# Search Results for "{query}"\n\n')
        for item in formatted:
            f.write(f'## {item["title"]}\n')
            f.write(f'- URL: {item["url"]}\n')
            f.write(f'- Description: {item["description"]}\n\n')


def get_filename_for_query(query: str) -> str:
    """
    Generate a standardized filename for a given query

    Args:
        query: The search query

    Returns:
        Standardized filename
    """
    today = datetime.now().strftime('%Y-%m-%d')
    return f'step1_{query.lower().replace(" ", "_")}_{today}.md'


def fetch_url_content(url: str, api_key: str, fetcher: str = 'w3m') -> Optional[str]:
    """
    Fetch content from a URL if not already prefetched

    Args:
        url: URL to fetch content from
        api_key: API key for authorization

    Returns:
        Retrieved content as string or None if error occurs
    """
    try:
        if fetcher == 'w3m':
            headers = {
                'accept': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
            response = requests.get(
                f'https://amd1.mooo.com/api/w3m?url={url}', headers=headers)
            response.raise_for_status()
            return response.text
        elif fetcher == 'markdowner':
            response = requests.get(f'https://md.dhr.wtf/?url={url}')
            response.raise_for_status()
            return response.text
        elif fetcher == 'jina':
            response = requests.get(f'https://r.jina.ai/{url}')
            response.raise_for_status()
            return response.text
        elif fetcher == 'urltomarkdown':
            response = requests.get(f'https://urltomarkdown.herokuapp.com/?url={url}&links=false&title=true')
            response.raise_for_status()
            return response.text
        else:
            logger.error(f'Invalid fetcher specified: {fetcher}')
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f'Error fetching URL content with {fetcher}: {e}')

        # If primary fetcher fails, try alternate fetcher
        try:
            import inquirer
            alternate_fetcher = 'markdowner' if fetcher == 'w3m' else 'w3m'
            questions = [
                inquirer.Confirm('use_alternate',
                                 message=f'{fetcher} failed. Try {alternate_fetcher} instead?',
                                 default=True)
            ]
            answers = inquirer.prompt(questions)

            if answers and answers.get('use_alternate'):
                logger.info(f'Using alternate fetcher: {alternate_fetcher}')
                try:
                    if alternate_fetcher == 'w3m':
                        headers = {
                            'accept': 'application/json',
                            'Authorization': f'Bearer {api_key}'
                        }
                        alt_response = requests.get(
                            f'https://amd1.mooo.com/api/w3m?url={url}', headers=headers)
                    else:
                        alt_response = requests.get(
                            f'https://md.dhr.wtf/?url={url}')
                    alt_response.raise_for_status()
                    return alt_response.text
                except requests.exceptions.RequestException as alt_error:
                    logger.error(
                        f'Error fetching URL content with alternate fetcher: {alt_error}')
                    return None
            else:
                logger.info('User declined to use alternate fetcher')
                return None
        except ImportError:
            logger.error(
                'Inquirer module not installed, cannot prompt for alternate fetcher')
            return None


def store_url_content(url: str, content: str, overwrite: bool = True) -> str:
    """
    Store URL content to a markdown file

    Args:
        url: The source URL
        content: Content to store

    Returns:
        Filename of the stored content
    """
    filename = f'url_{url.split("//")[-1].replace("/", "_")}.md'
    filepath = os.path.join(os.path.dirname(__file__), filename)

    if os.path.exists(filepath) and not overwrite:
        logger.info(f'Content already exists at {filepath}')
        return filename

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    logger.info(f'Stored content to {filename}')
    return filename


def parse_markdown_results(filepath: str) -> Dict[str, Any]:
    """
    Parse existing markdown file to extract search results

    Args:
        filepath: Path to the markdown file

    Returns:
        Dictionary containing parsed search results
    """
    results = {'content': []}
    try:
        if not os.path.exists(filepath):
            logger.warning(f"File not found: {filepath}")
            return results

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract URLs and descriptions from markdown
            sections = content.split('##')[1:]  # Skip the header
            for section in sections:
                lines = section.strip().split('\n')
                if len(lines) >= 2:
                    title = lines[0].strip()
                    from urllib.parse import unquote
                    url = unquote(lines[1].replace('- URL: ', '').strip())
                    desc = ''
                    if len(lines) >= 3:
                        desc = lines[2].replace('- Description: ', '').strip()
                    results['content'].append({
                        'id': len(results['content']) + 1,
                        'url': url,
                        'description': desc
                    })
        logger.info(
            f"Parsed {len(results['content'])} results from {filepath}")
    except Exception as e:
        logger.error(f"Error parsing markdown file: {e}")

    return results


def display_results(formatted_results: List[Dict[str, Any]]) -> None:
    """
    Display formatted search results to the console

    Args:
        formatted_results: List of formatted search result items
    """
    if not formatted_results:
        logger.warning("No results to display")
        return

    for item in formatted_results:
        print(f"{item['id']}. {item['title']}\n{item['description']}\n")


def get_filestats(filepath: str) -> Dict[str, Any]:
    """
    Get file statistics for a given file

    Args:
        filepath: Path to the file

    Returns:
        Dictionary containing file statistics
    """
    stats = {}
    try:
        if os.path.exists(filepath):
            stats['filename'] = os.path.basename(filepath)
            stats['crawldate'] = datetime.fromtimestamp(
                os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
            with open(filepath, 'r', encoding='utf-8') as f:
                chars = len(f.read())
                stats['Chars'] = chars
                stats['Tokens'] = chars // 4
        else:
            logger.warning(f"File not found: {filepath}")
    except Exception as e:
        logger.error(f"Error getting file stats: {e}")

    return stats


def main():
    """
    Main function to execute the search workflow
    """

    # Set up argument parser
    parser = argparse.ArgumentParser(description='Search API client')
    parser.add_argument('query', nargs='?', default='ki für architekten',
                        help='Search query (default: "ki für architekten")')
    parser.add_argument('--num-results', type=int, default=10,
                        help='Number of results to fetch (default: 10)')
    parser.add_argument('--no-cache', action='store_true',
                        help='Ignore cached results and fetch new ones')
    args = parser.parse_args()

    # PARAMETERS
    amd1_api_key = get_api_key("amd1")   # Get API key from credgoo

    fetcher_use = 'urltomarkdown' # 'jina' #'w3m'  # or 'markdowner'
    # Generate filename for the query
    filename = get_filename_for_query(args.query)
    filepath = os.path.join(os.path.dirname(__file__), filename)


    # Ask user if they want to skip web crawling
    skip_flow = inquirer.prompt([
        inquirer.Confirm('crawl_flow',
                        message='Skip web crawling?',
                        default=True)
    ])
    
    if not skip_flow['crawl_flow']:
        # Check if we have cached results
        if os.path.exists(filepath) and not args.no_cache:
            logger.info(f"Using cached results from {filepath}")
            results = parse_markdown_results(filepath)
        else:
            # Fetch new results
            logger.info(f"Fetching search results for '{args.query}'")
            results = fetch_search_results(
                args.query, args.num_results, amd1_api_key)
            if not results:
                logger.error("Failed to fetch search results")
                sys.exit(1)

            # Save results to markdown file
            save_results_to_md(args.query, results)
            logger.info(f"Saved results to {filename}")

        # Format and display results
        formatted_results = present_results(results)
        # display_results(formatted_results)

        # If inquirer is available, allow user to select a result
        try:
            selected = select_search_result(formatted_results)
            if selected:
                print(f"\nSelected: {selected['title']}\nURL: {selected['url']}")

                # Ensure we're using the actual URL, not description text
                url = selected['url']
                # Check if URL is valid (starts with http:// or https://)
                if not url.startswith('http://') and not url.startswith('https://'):
                    # Try to extract URL from the string if it contains a domain
                    import re
                    url_match = re.search(
                        r'((?:https?://)?(?:www\.)?[\w-]+\.[\w.-]+(?:/[\w.-]*)*)', url)
                    if url_match:
                        extracted_url = url_match.group(1)
                        # Add https:// if missing
                        if not extracted_url.startswith('http'):
                            extracted_url = 'https://' + extracted_url
                        url = extracted_url
                        logger.info(f"Extracted URL: {url}")
                    else:
                        logger.error(f"Invalid URL format: {url}")
                        print(
                            f"Error: Invalid URL format. URL must start with http:// or https://")
                        sys.exit(1)
        except ImportError:
            logger.info("Inquirer module not installed, skipping selection")

        # Fetch and store content for selected URL
        if selected:
            content = fetch_url_content(
                url=url, api_key=amd1_api_key, fetcher=fetcher_use)
            if content:
                filename = store_url_content(url, content)
                logger.info(f"Stored content to {filename}")

        filestats = get_filestats(filename)
        print(f"File stats: {filestats}")
        # Print the first 400 characters of the file
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read(40)
            print(f"{filename}:    {content}")
    # Ask user to pipe the file into a llm
    # select from a list of provider / llm to use
    # Define available LLM providers and models using a more structured approach
    # select via inquirer a host/model pair
    # Ask user if they want to skip web crawling
    # Ask user if they want to skip web crawling
    skip_flow = inquirer.prompt([
        inquirer.Confirm('model_flow',
                        message='Use Default Model?',
                        default=True)
    ])
    
    if not skip_flow['model_flow']:
        # Will prompt user to select LLM provider and model
        try:
            provider_choices = [
                (f"{provider} ({', '.join(models.keys())})", provider) 
                for provider, models in llm_providers.items()
            ]
            provider_question = [
                inquirer.List('provider',
                            message='Select a LLM provider',
                            choices=provider_choices)
            ]
            provider_answer = inquirer.prompt(provider_question)
            selected_provider = provider_answer['provider']

            model_choices = [
                (f"{model} - {details['description']}", model) 
                for model, details in llm_providers[selected_provider]['models'].items()
            ]
            model_question = [
                inquirer.List('model',
                            message='Select a model',
                            choices=model_choices)
            ]
            model_answer = inquirer.prompt(model_question)
            selected_model = model_answer['model']

            print(f"Selected {selected_provider}/{selected_model}")
            # Now you can use the selected model for processing
        except ImportError:
            logger.error("Inquirer module not installed, skipping model selection")

        
    skip_flow = inquirer.prompt([
        inquirer.Confirm('file_flow',
                        message='Use Default File?',
                        default=True)
    ])
    
    if not skip_flow['file_flow']:        
        # Get list of markdown files in current directory with token counts
        md_files = []
        for f in os.listdir(os.path.dirname(__file__)):
            if f.endswith('.md'):
                filepath = os.path.join(os.path.dirname(__file__), f)
                with open(filepath, 'r', encoding='utf-8') as file:
                    chars = len(file.read())
                    tokens = chars // 4
                    md_files.append(f"{f} ({tokens} tokens)")
        if not md_files:
            logger.warning("No markdown files found in directory")
            sys.exit(1)

        # Have user select a file using inquirer
        try:
            file_question = [
                inquirer.List('file',
                            message='Select a file to process',
                            choices=md_files)
            ]
            file_answer = inquirer.prompt(file_question)
            selected_file = file_answer['file'].split(' ')[0]  # Extract filename before token count
            
            # Get full path of selected file
            selected_filepath = os.path.join(os.path.dirname(__file__), selected_file)
            
            # Read file content
            with open(selected_filepath, 'r', encoding='utf-8') as f:
                file_content = f.read()
                
            logger.info(f"Selected file: {selected_file}")
            
        except ImportError:
            logger.error("Inquirer module not installed, cannot select file")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error selecting/reading file: {e}")
            sys.exit(1)

        # pipe the file into the selected llm
        # pipe the file into the selected llm
if __name__ == "__main__":
    main()
