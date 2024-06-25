from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import subprocess
import requests
from googlesearch import search as google_search

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def ensure_https(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'https://' + url
    return url

def fetch_with_w3m(url):
    try:
        result = subprocess.run(['w3m', '-dump', url], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error fetching {url} with w3m: {result.stderr}"
    except subprocess.TimeoutExpired:
        return f"Error: Timeout expired while fetching {url} with w3m"
    except Exception as e:
        return f"An error occurred with w3m: {e}"

def fetch_with_markdowner(url):
    try:
        api_endpoint = 'https://md.dhr.wtf/'
        response = requests.get(api_endpoint, params={'url': url}, timeout=10)
        
        if response.status_code == 200:
            return response.content.decode('utf-8')
        else:
            return f"Error fetching {url} with Markdowner: {response.status_code}"
    except requests.Timeout:
        return f"Error: Timeout expired while fetching {url} with Markdowner"
    except Exception as e:
        return f"An error occurred with Markdowner: {e}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('term')
    num_results = int(request.args.get('num_results', 5))
    print(f"Search query: {query}, Number of results: {num_results}")
    urls = list(google_search(query, stop=num_results))
    print(f"Search results: {urls}")
    return jsonify(urls)

@app.route('/crawl')
def crawl():
    url = ensure_https(request.args.get('result'))
    print(f"Crawling URL: {url}")
    w3m_results = fetch_with_w3m(url)
    markdown_results = fetch_with_markdowner(url)
    print(f"w3m results: {w3m_results[0:100]}")
    print(f"Markdown results: {markdown_results[0:100]}")
    return jsonify({'w3m': w3m_results, 'markdown': markdown_results})

@app.route('/next')
def next_page():
    url = ensure_https(request.args.get('result'))
    print(f"Next page crawl URL: {url}")
    w3m_results = fetch_with_w3m(url)
    markdown_results = fetch_with_markdowner(url)
    print(f"Next page w3m results: {w3m_results}")
    print(f"Next page Markdown results: {markdown_results}")
    return jsonify({'w3m': w3m_results, 'markdown': markdown_results})

if __name__ == '__main__':
    app.run(debug=True)
