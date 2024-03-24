import json


def load_api_credentials(model_name, filename='keys.json'):
    with open(filename, 'r') as file:
        keys = json.load(file)

    if model_name not in keys:
        raise ValueError(
            f"API configuration for '{{{model_name}}}' not found in {filename}.")

    return keys[model_name]['api_key'], keys[model_name]['api_url']


def load_model_parameters(model_name, filename='models.json'):
    with open(filename, 'r') as file:
        models = json.load(file)

    if model_name not in models:
        raise ValueError(f"Model '{model_name}' not found in {filename}.")

    return models[model_name]
