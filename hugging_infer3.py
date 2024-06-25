import requests
from getparams import load_api_credentials, load_model_parameters

hoster = 'huggingface'
model_name = 'mistral7b'

api_key = load_api_credentials(hoster)
model_parameters, api_url = load_model_parameters(hoster,model_name)

print(f"api_key: {api_key}, inference_url: {api_url}")
headers = {"Authorization": "Bearer " + api_key}

def query(payload):
    response = requests.post(api_url, headers=headers, json=payload)
    return response.json()


while True:
    user_input = input("\nq: ")
    if user_input.lower() == 'exit':
        break  # Exit the loop and program if the user types 'exit'.
    output = query({
        "inputs": user_input,
    })
    print("\n--\n\na: ", end='')
    print(output[0]['generated_text'])
    #print(output)
