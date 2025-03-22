import requests
from bs4 import BeautifulSoup
import json

def get_energy_data(jahresverbrauch):
    url = "https://www.stromrechner.at/spottarif#vergleich"
    data = {"jahresverbrauch": jahresverbrauch}
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        response.encoding = 'utf-8'  # Ensure the response is decoded as UTF-8
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None


def analyze_energy_data(html_content):
    if not html_content:
        return None
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the table containing the tariff information
    table = soup.find('table', class_='dci nshow')
    if not table:
        print("Table with class 'dci nshow' not found on the page.")
        return None
    
    # Extract headers
    headers = [th.text.strip() for th in table.find_all('th')]
    
    # Extract data rows
    data_rows = []
    for row in table.find_all('tr')[1:]:
        row_data = [td.text.strip() for td in row.find_all('td')]
        data_rows.append(dict(zip(headers, row_data)))
    
    return data_rows


def main():
    jahresverbrauch = input("Enter your annual energy consumption (kWh): ")
    try:
        jahresverbrauch = int(jahresverbrauch)
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return
    
    html_content = get_energy_data(jahresverbrauch)
    if html_content:
        energy_data = analyze_energy_data(html_content)
        if energy_data:
            print(json.dumps(energy_data, indent=2, ensure_ascii=False)) # ensure_ascii=False to correctly display special characters
        else:
            print("Could not extract energy data.")
    else:
        print("Failed to retrieve data from the website.")

if __name__ == "__main__":
    main()
