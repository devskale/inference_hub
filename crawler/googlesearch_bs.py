import requests
from bs4 import BeautifulSoup
import urllib.parse
import argparse

def google_search(query, num_results=4):
    # URL encode the query
    encoded_query = urllib.parse.quote(query)
    # Construct the Google search URL
    search_url = f"https://www.google.com/search?q={encoded_query}"
    
    try:
        # Perform the HTTP request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        
        # Print the response status and part of the HTML content for debugging
        print(f"Response Status Code: {response.status_code}")

        # Parse the response HTML with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract URLs from the search results
        urls = []
        for g in soup.find_all('div', class_='g'):
            a_tag = g.find('a')
            if a_tag:
                href = a_tag.get('href')
                if href and "http" in href:
                    urls.append(href)
                    if len(urls) >= num_results:
                        break

        return urls
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Google Search from the command line.")
    parser.add_argument("-s", "--searchterm", type=str, help="The search term to query Google with.")
    parser.add_argument("-n", "--numresults", type=int, default=4, help="The number of results to return (default=4).")

    # Parse arguments
    args = parser.parse_args()

    # Perform Google search
    urls = google_search(args.searchterm, num_results=args.numresults)
    
    # Print the search results
    print("Search results:")
    for url in urls:
        print(url)
