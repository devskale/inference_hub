import json


def load_api_credentials(hoster, filename='keys.json'):
    with open(filename, 'r') as file:
        keys = json.load(file)

    if hoster not in keys:
        raise ValueError(
            f"API configuration for '{{{hoster}}}' not found in {filename}.")

    return keys[hoster]['api_key']


def load_model_parameters(hoster, model_name, filename='models.json'):
    with open(filename, 'r') as file:
        data = json.load(file)

    if hoster not in data:
        raise ValueError(f"Model '{hoster}' not found in {data}.")

    # Check if the model exists under the specified hoster
    if model_name not in data[hoster]:
        raise ValueError(f"Model '{model_name}' not found under hoster '{hoster}' in {filename}.")

    # Return the params for the specified model under the specified hoster
    # also return inference api
    return data[hoster][model_name]['params'], data[hoster][model_name]['inference_api'] 
    


    return models[model_name]
