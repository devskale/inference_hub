from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
import json

# Initialize the FirecrawlApp with your API key
app = FirecrawlApp(api_key='fc-d8c497322f3444bab82f0f78eb5a8309')

class StromTarif(BaseModel):
    Name: str
    GrundpreisproNettoEURproMonat: str
    ArbeitspreisNettoEURprokWh: str
    Beschreibung: str

class ExtractSchema(BaseModel):
    Energieanbieter: str
    url: str
    Stromtarife: list[StromTarif]
    

def main():
  data = app.extract([
    'https://www.burgenlandenergie.at/de/privat/oekostrom-tarifuebersicht/',
    'https://www.wienenergie.at/privat/produkte/strom/'
  ], 
    {
  #    'prompt': 'Extract the company mission, whether it supports SSO, whether it is open source, and whether it is in Y Combinator from the page.',
      'prompt': 'Extrahiere den Namen des Energieanbieters und Details zu den angebotenen Stromtarifen.',
      'schema': ExtractSchema.model_json_schema(),
  })
  print(json.dumps(data, indent=4, ensure_ascii=False))

  with open(f'./stromdata.json', 'w') as f:
        json.dump(data, f, indent=4)

  try:
    with open(f'./data/strom/{data["data"]["Energieanbieter"]}.json', 'w') as f:
        json.dump(data, f, indent=4)
  except IOError as e:
    print(f"Error writing to file: {e}")




if __name__ == '__main__':
    main()