import requests
import json

def login_to_filebrowser(host, username, password):
    """Logs in to the Filebrowser and returns the authentication cookie."""
    login_url = f'{host}/api/login'
    login_data = {'username': username, 'password': password}
    try:
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
             return response.text
        else:
            raise Exception(f"Login failed with status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error during login: {str(e)}")

def list_directory(host, auth_cookie, dir_path='/'):
    """Lists the contents of a directory in Filebrowser."""
    resources_url = f'{host}/api/resources{dir_path}'
    cookies = {'auth': auth_cookie}
    try:
      response = requests.get(resources_url, cookies=cookies)
      if response.status_code == 200:
            return response.json()
      else:
          raise Exception(f"Failed to get listing. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error during directory listing: {str(e)}")

def download_file(host, auth_cookie, file_path):
  """Downloads a file from Filebrowser."""
  download_url = f'{host}/api/download{file_path}'
  cookies = {'auth': auth_cookie}
  try:
    response = requests.get(download_url, cookies=cookies, stream=True)
    if response.status_code == 200:
      return response.content
    else:
        raise Exception(f"Failed to download file. Status code: {response.status_code}")
  except requests.exceptions.RequestException as e:
        raise Exception(f"Error during file download: {str(e)}")

if __name__ == "__main__":
    HOST = 'http://pind.mooo.com:8010'
    USERNAME = 'plansky'
    PASSWORD = 'plan23'

    try:
        auth_cookie = login_to_filebrowser(HOST, USERNAME, PASSWORD)
        print("Login successful.")
        
        # Example of listing a directory
        directory_listing = list_directory(HOST, auth_cookie, dir_path='beispiele')
        print("Directory listing:")
        print(json.dumps(directory_listing, indent=2))

        #Example of downloading a file
        # Assuming the path is like /test.txt
        #file_path_to_download = "/test.txt" 
        #file_content = download_file(HOST,auth_cookie,file_path_to_download)
        #if file_content:
        #    print(f"File downloaded successfully. Content: {file_content.decode()}")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
