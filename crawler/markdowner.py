import sys
import requests

def ensure_https(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url
    return url

def fetch_content(url):
    api_endpoint = 'https://md.dhr.wtf/'
    response = requests.get(api_endpoint, params={'url': url})
    
    if response.status_code == 200:
        return response.content.decode('utf-8')
    else:
        return f"Error: {response.status_code}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python markdowner.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    url = ensure_https(url)
    content = fetch_content(url)
    print(content)