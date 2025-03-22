import requests
from bs4 import BeautifulSoup
import re
import random
from summarizer import Summarizer

'''
Die Top 10 Nachrichtenseiten in Österreich sind:

ORF.at - Die Website des öffentlich-rechtlichen Rundfunks ORF
DerStandard.at - Eine der führenden Qualitätszeitungen Österreichs
Krone.at - Website der Kronen Zeitung, der auflagenstärksten Tageszeitung
Heute.at - Nachrichtenportal der Boulevardzeitung "Heute"
DiePresse.com - Website der überregionalen Qualitätszeitung Die Presse
OE24.at - Nachrichtenportal der Boulevardzeitung Österreich
NachrichtenAT.com - Überregionales Nachrichtenportal
Nachrichten.at - Weiteres Nachrichtenportal
KleinenZeitung.at - Website der Kleinen Zeitung aus der Steiermark
VorarlbergerNachrichten.at - Regionalnachrichten aus Vorarlberg
'''

Top_Austrian_News_Sites = ['https://www.orf.at/', 'https://www.derstandard.at/', 'https://www.krone.at/',
                           'https://www.heute.at/', 'https://www.diepresse.com/', 'https://www.oe24.at/',
                           'https://www.nachrichten.at/', 'https://www.kleinezeitung.at/', 'https://www.vol.at/']

def cleanify(text):
    """
    Cleans the input text by collapsing multiple spaces into one,
    reducing multiple newlines to a single newline, and stripping
    leading and trailing whitespaces.
    
    Parameters:
    - text (str): The input text to clean.
    
    Returns:
    - str: The cleaned text.
    """
    # Collapse two or more spaces into one
    text = re.sub(r' {2,}', ' ', text)
    # Collapse two or more newlines into one
    text = re.sub(r'\n{2,}', '\n', text)
    # Remove leading and trailing whitespaces
    text = text.strip()
    return text


url = input('Enter a URL to scrape: ')
if url =='':
    url = Top_Austrian_News_Sites[random.randint(0, len(Top_Austrian_News_Sites)-1)]
elif url[0:3] != 'http':
    url = 'https://' + url
content = requests.get(url)
soup = BeautifulSoup(content.text, 'html.parser')  # Specify the parser


t1 = cleanify(soup.text)

#print(t1)
print('\n---------\n'+url+' '+ str((len(t1))/4) + ' tokens\n')
print(t1.strip())
'''
summarizer = Summarizer()
# Define the type of summary you want ('paragraph' or 'long')
summary_type = 'bullet'  # Or 'long', based on your requirement
# Call the summarization function on the processed text
summary = summarizer.run_summarize(t1, summary_type)
print('\nSummary:\n', summary)
'''

