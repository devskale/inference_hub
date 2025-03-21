import requests
import base64
import argparse
import sys

def decrypt_key(encrypted_key, encryption_key):
    """Decrypt the API key using the encryption key."""
    try:
        # Decode the base64 string
        decoded = base64.b64decode(encrypted_key).decode('utf-8', errors='replace')
        
        # Perform XOR decryption with key
        result = ""
        for i in range(len(decoded)):
            # Match the encryption algorithm's key usage pattern
            key_char = ord(encryption_key[(i * 7) % len(encryption_key)])
            decoded_char = ord(decoded[i])
            result += chr(decoded_char ^ key_char)
        
        # Remove the 8-character initialization vector
        if len(result) > 8:
            return result[8:]
        else:
            print("Warning: Decrypted result too short")
            return result
    except Exception as e:
        print(f"Decryption error: {e}")
        return None


def get_api_key(service, bearer_token, encryption_key):
    """Retrieve and decrypt an API key for the specified service."""
    # The URL of your deployed Google Apps Script
    url = "https://script.google.com/macros/s/AKfycbxMGfhXS9GNFyoMtwXNryXykxZ0sWXgPv_R4MTyiXOQNexfRzzly64c5IDjLAm8rGczww/exec"
    
    print(f"Fetching key for service: {service}")
    print(f"Using URL: {url}")
    
    # Add parameters
    params = {
        "service": service,
        "token": bearer_token
    }
    
    try:
        # Send request with timeout
        print("Sending request...")
        response = requests.get(url, params=params, timeout=10)
        print(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response data: {data}")
                
                if data.get("status") == "success":
                    encrypted_key = data.get("encryptedKey")
                    if encrypted_key:
                        return decrypt_key(encrypted_key, encryption_key)
                    else:
                        print("Error: No encrypted key in response")
                else:
                    print(f"Error: {data.get('message', 'Unknown error')}")
            except ValueError:
                print(f"Error parsing JSON response: {response.text[:100]}")
        else:
            print(f"Error: Failed to retrieve key (Status code: {response.status_code})")
            print(f"Response content: {response.text[:100]}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve API keys securely")
    parser.add_argument("service", help="Service name to retrieve the API key for")
    parser.add_argument("--token", required=True, help="Bearer token for authentication")
    parser.add_argument("--key", required=True, help="Encryption key for decryption")
    
    args = parser.parse_args()
    
    print("Starting API key retrieval...")
    api_key = get_api_key(args.service, args.token, args.key)
    if api_key:
        print(f"API Key for {args.service}: {api_key}")
    else:
        print("Failed to retrieve API key")
        sys.exit(1)