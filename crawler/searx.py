import requests

def search_searx(query, num_results=5, searx_instance='https://searx.hu'):
    try:
        # Searx instance URL
        searx_url = f'{searx_instance}/search'
        # Query parameters
        params = {
            'q': query,
            'format': 'json',
            'count': num_results
        }
        # Sending GET request to the Searx API
        response = requests.get(searx_url, params=params, timeout=10)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

def main():
    query = 'example search query'
    results = search_searx(query)
    if isinstance(results, str):
        # An error occurred
        print(results)
    else:
        # Print out the results
        for result in results['results']:
            print(f"Title: {result['title']}")
            print(f"URL: {result['url']}")
            print(f"Snippet: {result['content']}\n")

if __name__ == "__main__":
    main()
