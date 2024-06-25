import subprocess
import re

def google_search(query, num_results=3):
    # Construct the Google search URL
    search_url = f"https://www.google.com/search?q={query}"
    
    try:
        # Use w3m to fetch the search results
        result = subprocess.run(['w3m', '-dump', search_url], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"w3m error: {result.stderr}")

        # Extract URLs from the w3m output using a regular expression
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', result.stdout)
        
        # Filter the URLs to exclude unwanted links and limit to num_results
        filtered_urls = [url for url in urls if 'google' not in url and 'webcache' not in url][:num_results]
        return filtered_urls
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

if __name__ == "__main__":
    # Example usage
    query = "python web scraping"
    urls = google_search(query, num_results=5)
    print("Search results:")
    for url in urls:
        print(url)
