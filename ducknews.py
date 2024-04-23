import argparse
from duckduckgo_search import DDGS
from datetime import datetime, timezone


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

'''News search
date: str
title: str
body: str
url: str
image: str
source: str
'''

'''Text search
title: str
href: str
body: str
'''

'''Maps Search
title: str
address: str
country_code: str
url: str
phone: str
latitude: float
longitude: float
source: str
image: str
desc: str
hours: str
category: str
facebook: str
instagram: str
twitter: str
'''

'''suggestions 
phrase: str
'''

'''
translate
detected_language: str
translated: str
original: str
'''
# Setup argparse to handle command-line arguments
parser = argparse.ArgumentParser(description="Search for news articles on a given topic.")
parser.add_argument('newstopic', nargs='?', help="News topic to search for", default="")

args = parser.parse_args()
#newstopic = ' '.join(args.newstopic)

if args.newstopic:
    newstopic = args.newstopic
    print(f"\n\nNews topic: {newstopic}")
else:
    newstopic = input('\n\nEnter a news keywords to search for: ')

print('--------------------------------------------------\n\n')
#results = DDGS().text("DI Johann Waldherr", max_results=5)
#results = DDGS().news(keywords=newstopic, region="wt-wt", safesearch="off", timelimit="m", max_results=5)
results = DDGS().news(keywords=newstopic, region="wt-wt", safesearch="off", timelimit="m", max_results=8)
#results = DDGS().answers("sun")
#results = DDGS().maps("Cafe", place="Neusiedl am See", max_results=20)
#results = DDGS().suggestions("skale")
#keywords = ['Search for words, documents, images, news, maps and text translation using the DuckDuckGo.com search engine.', 'cat']
#results = DDGS().translate(keywords, to="de")
#print_dict_structure(results[0])
#print(results)
#exit()

for result in results:
    result['age'] = age_of_article(result['date'])

sorted_results = sorted(results, key=lambda x: x['age'])

for result in sorted_results:
    print(f"\n{result['title']}    {result['age']}\n")
    print(f"   {format_text(result['body'], 100)}")  # Assuming format_text wraps text at 80 characters
    print('\n-')

print('\n\n')

exit()

          
