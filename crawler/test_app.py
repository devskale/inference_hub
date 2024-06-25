import requests

urls = [
        "https://www.bbc.com/news/world",
        "https://sport.orf.at/stories/3125900/",
        "https://www.kicker.at/der-letzte-auftritt-des-koenigs-1027304/artikel",
        "https://www.instagram.com/b.netanyahu/reel/Cyg659bIcV8/",
        "https://x.com/Inc/status/1794471900837486780",
        "https://searx.tiekoetter.com/search?q=top+news&category_general=&language=de-DE&time_range=&safesearch=0&theme=simple"
        ]        



def test_crawl_endpoint(crawler = 'mark'):
    base_url = "http://127.0.0.1:5000"
    endpoint = f"/{crawler}"
    params = {
        'result': urls[0]
    }
    
    try:
        response = requests.get(base_url + endpoint, params=params)
        if response.status_code == 200:
            print("Test passed! Here is the response:")
            print(response.json())
        else:
            print(f"Test failed with status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"An error occurred: {e}")


from playwright.sync_api import sync_playwright
import html2text

def fetch_with_playwright(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            content = page.content()
            browser.close()
            markdown = html2text.html2text(content)
            return markdown
    except Exception as e:
        return f"An error occurred: {e}"




if __name__ == "__main__":
#    test_crawl_endpoint('w3m')
    urlnum = 4
    content = fetch_with_playwright(urls[urlnum])
    print(f"---========================================--\n")  # Print first 500 characters for brevity
    print(f"Content from {urls[urlnum]}:\n{content}...\n")  # Print first 500 characters for brevity
    print(f"---========================================--\n")  # Print first 500 characters for brevity

