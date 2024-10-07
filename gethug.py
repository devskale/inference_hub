import os
import json
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN")
JSON_FILE = "latest_model.json"

client = InferenceClient(token=HUGGINGFACE_TOKEN)
models = client.list_deployed_models(frameworks="text-generation-inference")

def print_nice_list_and_count(models_dict):
    total_models = sum(len(models) for models in models_dict.values())
    
    for category_idx, (category, model_list) in enumerate(models_dict.items(), start=1):
        category_letter = chr(96 + category_idx)  # Convert to a, b, c, ...
        print(f"{category_letter}. {category}:")
        for idx, model in enumerate(model_list, start=1):
            print(f"     {idx}. {model}")
    
    print(f"\nTotal models: {total_models}")

def find_matching_models(search_term, models_dict):
    matching_models = []
    for category_idx, (category, model_list) in enumerate(models_dict.items(), start=1):
        for model_idx, model in enumerate(model_list, start=1):
            if search_term.lower() in model.lower():
                matching_models.append((chr(96 + category_idx), model_idx, model))
    return matching_models

def save_latest_model(model):
    with open(JSON_FILE, 'w') as f:
        json.dump({"latest_model": model}, f)

def load_latest_model():
    try:
        with open(JSON_FILE, 'r') as f:
            data = json.load(f)
            return data.get("latest_model")
    except FileNotFoundError:
        return None

def select_model():
    print_nice_list_and_count(models)

    suggested_models = ["Mistral-Nemo-Instruct", "gemma-2-9b-it", "Llama-3.2-3B-Instruct", "qwen"]

    print("\nPlease select a model")
    print("Suggestions:")

    for model in suggested_models:
        matching_models = find_matching_models(model, models)
        if matching_models:
            for category_letter, model_idx, full_model_name in matching_models:
                print(f"    {category_letter}{model_idx} {full_model_name}")
        else:
            print(f"    Model not found: {model}")

    # Loop until a valid model is chosen or the user decides to exit
    chosen_model = None
    while chosen_model is None:
        selected_model = input("\nEnter the model code (e.g., b34) or type 'exit' to quit: ")
        if selected_model.lower() == 'exit':
            print("Exiting...")
            return None
        
        if len(selected_model) < 2:
            print("Invalid input. Please enter a valid model code.")
            continue
        
        category_letter, model_number = selected_model[0], int(selected_model[1:])
        
        # Find the selected model
        for category_idx, (category, model_list) in enumerate(models.items(), start=1):
            if chr(96 + category_idx) == category_letter:
                if 1 <= model_number <= len(model_list):
                    chosen_model = model_list[model_number - 1]
                    print(f"\nYou selected: {chosen_model}")
                    break
                else:
                    print(f"\nInvalid model number for category {category_letter}")
                break
        else:
            print("\nInvalid category")

    return chosen_model

def main():
    latest_model = load_latest_model()
    
    if latest_model:
        print(f"Latest model used: {latest_model}")
        use_latest = input("Do you want to use the latest model? (y/n): ").lower()
        if use_latest == 'y':
            chosen_model = latest_model
        else:
            chosen_model = select_model()
    else:
        chosen_model = select_model()

    if chosen_model:
        save_latest_model(chosen_model)
        
        # load the selected model
        chatmodel = InferenceClient(chosen_model)

        introquery = "Tell me how excited you are to chat with me."

        response = chatmodel.chat_completion(
            messages=[
                {"role": "system", "content": f"You are {chosen_model}, a helpful assistant."},
                {"role": "user", "content": introquery}
            ],
            max_tokens=500,
        )

        print(f"\n{response.choices[0].message.content}")

if __name__ == "__main__":
    main()