import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Initialize InferenceClient and Supabase client
inference_client = InferenceClient(token=HUGGINGFACE_TOKEN)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Get the list of deployed models from HuggingFace
models_dict = inference_client.list_deployed_models()

# Function to store models into Supabase
def store_models(models_dict):
    for model in models_dict:
        model_name = model['modelId']
        model_category = model['model']['category']
        active = model['model']['active']
        provider = model['model']['provider']
        print(model_name, model_category, active, provider)

# Function to insert categories into Supabase
def insert_categories(models_dict):
    categories = [{'category': category} for category in models_dict.keys()]
    response = supabase.table('modelscategory').upsert(categories).execute()
    return response

# Insert categories first
categories_response = insert_categories(models_dict)
print(categories_response)

# Function to insert models into Supabase
def insert_models(models_dict):
    for category, models in models_dict.items():
        for model in models:
            data_to_insert = {
                'modelid': model,
                'active': True,
                'category': category
            }
            response = supabase.table('models').upsert(data_to_insert).execute()

# Function to deactivate all models
def deactivate_all_models():
    response = supabase.table('models').update({'active': False}).neq('active', False).execute()

# Deactivate all models
deactivate_all_models()

# Insert models
insert_models(models_dict)

# Function to print statistics of active and inactive models
def print_model_stats():
    active_count = supabase.table('models').select('count', count='exact').eq('active', True).execute()
    inactive_count = supabase.table('models').select('count', count='exact').eq('active', False).execute()
    print(f"Active models: {active_count.count}")
    print(f"Inactive models: {inactive_count.count}")

# Print model statistics
print_model_stats()

# Load all model categories from Supabase into model_categories
model_categories = supabase.table('modelscategory').select('*').execute()

# Print the model categories
for cat in model_categories.data:
    print(cat['category'])

# Function to read all models with category 'text-generation' from Supabase
def get_models_by_category(category):
    models = supabase.table('models').select('*').eq('category', category).execute()
    return models

# Example usage
text_generation_models = get_models_by_category('text-generation')
print(text_generation_models.data)
