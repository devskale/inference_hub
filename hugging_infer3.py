import requests

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
headers = {"Authorization": "Bearer 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"}
# add more headers if needed like 'content-type': 'application/json'



def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()



while True:
    user_input = input("\nq: ")
    if user_input.lower() == 'exit':
        break  # Exit the loop and program if the user types 'exit'.
    output = query({
        "inputs": user_input,
    })
    print("\n--\n\na: ", end='')
    #print(output[0]['generated_text'])
    print(output)
