import requests
import json

# Disable SSL warnings for testing
requests.packages.urllib3.disable_warnings()

# Test request
url = "https://api.openai.com/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-test123"
}
data = {
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello, how are you?"}]
}

try:
    response = requests.post(url, headers=headers, json=data, verify=False)
    print(f"Status Code: {response.status_code}")
    print("Response Headers:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    
    try:
        print("\nResponse Body:")
        print(json.dumps(response.json(), indent=2))
    except:
        print("\nResponse Text:")
        print(response.text)
        
except Exception as e:
    print(f"Request failed: {str(e)}")