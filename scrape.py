from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info

print("Scraping the web...")

graph_config = {
    "llm": {
        "model": "ollama/phi3",
        "temperature": 0,
        "format": "json",  # Ollama needs the format to be specified explicitly
        "base_url": "http://amp1.mooo.com:11434",  # set Ollama URL
    },
    "embeddings": {
        "model": "ollama/nomic-embed-text",
        "base_url": "http://amp1.mooo.com:11434",  # set Ollama URL
    }
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

'''
smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the projects with their description.",
    # also accepts a string with the already downloaded HTML code
    source="https://perinim.github.io/projects",
    config=graph_config
)
'''

smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the news with their description. Separate them by category.",
    # also accepts a string with the already downloaded HTML code
    source="https://www.wired.com/category/science/",
    config=graph_config
)


result = smart_scraper_graph.run()
print(result)

import json

output = json.dumps(result, indent=2)

line_list = output.split("\n")  # Sort of line replacing "\n" with a new line

for line in line_list:
    print(line)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = smart_scraper_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
