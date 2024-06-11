import sys
import subprocess

def ensure_https(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url
    return url

def fetch_webpage(url):
    # Ensure the URL starts with https://
    url = ensure_https(url)
    
    # Using subprocess to call w3m and fetch the webpage content
    result = subprocess.run(['w3m', '-dump', url], capture_output=True, text=True)
    
    if result.returncode == 0:
        return result.stdout
    else:
        return f"Error: {result.stderr}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python markdowner.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    content = fetch_webpage(url)
    print(content)