import os
import pandas as pd
from huggingface_hub import InferenceClient
from tqdm import tqdm
import time

HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN")

all_models = []


def loop_query_data():
    global all_models
    client = InferenceClient(token=HUGGINGFACE_TOKEN)
    models_dict = client.list_deployed_models("text-generation-inference")
    models = models_dict.get('text-generation', []) + \
        models_dict.get('text2text-generation', [])
    models_vision = models_dict.get('image-text-to-text', [])
    try:
        models_others = client.list_deployed_models(
            frameworks="all").get("text-generation", [])
    except Exception as e:
        print(f"Warning: Failed to list all frameworks - {str(e)}")
        models_others = []

    models_conclusion = {
        "Model": [],
        "API": [],
        "Text Completion": [],
        "Chat Completion": [],
        "Vision": []
    }

    all_models = list(set(all_models + models + models_vision + models_others))
    for m in tqdm(all_models):
        text_available = False
        chat_available = False
        vision_available = False
        if m in models_vision:
            vision_available = True
        pro_sub = False

        run_text = True
        retry_count = 0
        max_retries = 3
        initial_timeout = 10

        while run_text and retry_count < max_retries:
            try:
                run_text = False
                client.text_generation(
                    m, "Hi.", max_new_tokens=1, timeout=initial_timeout)
                text_available = True
            except Exception as e:
                error_msg = str(e)
                if "Model requires a Pro subscription" in error_msg:
                    pro_sub = True
                    break
                elif "Rate limit reached" in error_msg:
                    print(
                        f"Rate Limited, waiting {60 * (retry_count + 1)} seconds...")
                    time.sleep(60 * (retry_count + 1))
                    run_text = True
                elif "Timeout" in error_msg or "Connection" in error_msg:
                    retry_count += 1
                    initial_timeout += 5
                    print(
                        f"Connection issue, retrying ({retry_count}/{max_retries}) with timeout {initial_timeout}s...")
                    run_text = True
                else:
                    print(f"Unexpected error testing model {m}: {error_msg}")
                    break

        run_chat = True
        retry_count = 0
        max_retries = 3
        initial_timeout = 10

        while run_chat and retry_count < max_retries:
            try:
                run_chat = False
                client.chat_completion(
                    m, messages=[{'role': 'user', 'content': 'Hi.'}], max_tokens=1, timeout=initial_timeout)
                chat_available = True
            except Exception as e:
                error_msg = str(e)
                if "Model requires a Pro subscription" in error_msg:
                    pro_sub = True
                    break
                elif "Rate limit reached" in error_msg:
                    print(
                        f"Rate Limited, waiting {60 * (retry_count + 1)} seconds...")
                    time.sleep(60 * (retry_count + 1))
                    run_chat = True
                elif "Timeout" in error_msg or "Connection" in error_msg:
                    retry_count += 1
                    initial_timeout += 5
                    print(
                        f"Connection issue, retrying ({retry_count}/{max_retries}) with timeout {initial_timeout}s...")
                    run_chat = True
                else:
                    print(f"Unexpected error testing model {m}: {error_msg}")
                    break

        models_conclusion["Model"].append(m)
        models_conclusion["API"].append("Free" if chat_available or text_available else (
            "Pro Subscription" if pro_sub else "Not Responding"))
        models_conclusion["Chat Completion"].append(
            "---" if (pro_sub or (not chat_available and not text_available)) else ("✓" if chat_available else "⌀"))
        models_conclusion["Text Completion"].append(
            "---" if (pro_sub or (not chat_available and not text_available)) else ("✓" if text_available else "⌀"))
        models_conclusion["Vision"].append("✓" if vision_available else "⌀")

    pd.DataFrame(models_conclusion).to_csv("data.csv", index=False)
    return models_conclusion


def get_available_free(use_cache=False):
    if use_cache and os.path.exists("data.csv"):
        return pd.read_csv("data.csv").to_dict(orient='list')
    else:
        return loop_query_data()


def update_data(use_cache=False):
    data = get_available_free(use_cache)
    df = pd.DataFrame(data)

    status_mapping = {"✓": 0, "⌀": 1, "---": 2}

    df['Text Completion'] = df['Text Completion'].map(status_mapping)
    df['Chat Completion'] = df['Chat Completion'].map(status_mapping)

    df = df.sort_values(by=['API', 'Text Completion',
                        'Chat Completion', 'Vision'])

    df['Text Completion'] = df['Text Completion'].map(
        {v: k for k, v in status_mapping.items()})
    df['Chat Completion'] = df['Chat Completion'].map(
        {v: k for k, v in status_mapping.items()})

    return df


def display_table(search_query="", filters=[], use_cache=False):
    df = update_data(use_cache)
    search_query = str(search_query)

    if search_query:
        filtered_df = df[df["Model"].str.contains(search_query, case=False)]
    else:
        filtered_df = df

    if filters:
        api_filters = [f for f in filters if f in [
            "Free", "Pro Subscription", "Not Responding"]]
        if api_filters:
            filtered_df = filtered_df[filtered_df["API"].isin(api_filters)]
        if "Text Completion" in filters:
            filtered_df = filtered_df[filtered_df["Text Completion"] == "✓"]
        if "Chat Completion" in filters:
            filtered_df = filtered_df[filtered_df["Chat Completion"] == "✓"]
        if "Vision" in filters:
            filtered_df = filtered_df[filtered_df["Vision"] == "✓"]

    return filtered_df


def search_models(query="", filters=[], use_cache=True):
    return display_table(query, filters, use_cache)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Fetch and update Hugging Face models data.')
    parser.add_argument('--query', type=str, default="",
                        help='Search query for models')
    parser.add_argument('--filters', nargs='+', default=[],
                        help='Filters for models')
    parser.add_argument('--use_cache', action='store_true',
                        help='Use cached data if available')
    parser.add_argument('--update', action='store_true',
                        help='Fetch and update models data')

    args = parser.parse_args()

    if args.update:
        print("Fetching and updating models data...")
        loop_query_data()
        print("Update completed. Data saved to data.csv.")
    else:
        result_df = search_models(args.query, args.filters, args.use_cache)
        result_df.to_csv("filtered_models.csv", index=False)
        print("Filtered data saved to filtered_models.csv.")
        print(result_df)
