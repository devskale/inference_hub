import os
import gradio as gr
import pandas as pd
from huggingface_hub import InferenceClient
from threading import Timer
from tqdm import tqdm
import time

HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN")

def loop_query_data():
    global all_models
    models_dict = InferenceClient(token=HUGGINGFACE_TOKEN).list_deployed_models("text-generation-inference")
    text_generation_models = models_dict.get('text-generation', [])
    text2text_generation_models = models_dict.get('text2text-generation', [])
    models = text_generation_models + text2text_generation_models
    models_vision = models_dict.get('image-text-to-text', [])
    models_others = InferenceClient(token=HUGGINGFACE_TOKEN).list_deployed_models(frameworks="all").get("text-generation", [])
    
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
        while run_text:
            try:
                run_text = False
                InferenceClient(m, timeout=10, token=HUGGINGFACE_TOKEN).text_generation("Hi.", max_new_tokens=1)
                text_available = True
            except Exception as e:
                if e and "Model requires a Pro subscription" in str(e):
                    pro_sub = True
                if e and "Rate limit reached" in str(e):
                    print("Rate Limited, waiting 1 hour...")
                    time.sleep(60*60)
                    run_text = True
        run_chat = True
        while run_chat:
            try:
                run_chat = False
                InferenceClient(m, timeout=10).chat_completion(messages=[{'role': 'user', 'content': 'Hi.'}], max_tokens=1)
                chat_available = True
            except Exception as e:
                if e and "Model requires a Pro subscription" in str(e):
                    pro_sub = True
                if e and "Rate limit reached" in str(e):
                    print("Rate Limited, waiting 1 hour...")
                    time.sleep(60*60)
                    run_chat = True
        models_conclusion["Model"].append(m)
        models_conclusion["API"].append("Free" if chat_available or text_available else ("Pro Subscription" if pro_sub else "Not Responding"))
        models_conclusion["Chat Completion"].append("---" if (pro_sub or (not chat_available and not text_available)) else ("✓" if chat_available else "⌀"))
        models_conclusion["Text Completion"].append("---" if (pro_sub or (not chat_available and not text_available)) else ("✓" if text_available else "⌀"))
        models_conclusion["Vision"].append("✓" if vision_available else "⌀")
    pd.DataFrame(models_conclusion).to_csv(str(os.getcwd())+"/data.csv", index=False)
    return models_conclusion

def get_available_free(use_cache = False):
    if use_cache:
        if os.path.exists(str(os.getcwd())+"/data.csv"):
            return pd.read_csv("data.csv").to_dict(orient='list')
    else:
        return loop_query_data()

def update_data(use_cache = False):
    data = get_available_free(use_cache)
    df = pd.DataFrame(data)
    
    status_mapping = {"✓": 0, "⌀": 1, "---": 2}

    df['Text Completion'] = df['Text Completion'].map(status_mapping)
    df['Chat Completion'] = df['Chat Completion'].map(status_mapping)
    
    df = df.sort_values(by=['API', 'Text Completion', 'Chat Completion', 'Vision'])
    
    df['Text Completion'] = df['Text Completion'].map({v: k for k, v in status_mapping.items()})
    df['Chat Completion'] = df['Chat Completion'].map({v: k for k, v in status_mapping.items()})
    
    return df

def display_table(search_query="", filters=[], use_cache=False):
    df = update_data(use_cache)
    search_query = str(search_query)
    
    if search_query:
        filtered_df = df[df["Model"].str.contains(search_query, case=False)]
    else:
        filtered_df = df

    if filters:
        api_filters = [f for f in filters if f in ["Free", "Pro Subscription", "Not Responding"]]
        if api_filters:
            filtered_df = filtered_df[filtered_df["API"].isin(api_filters)]
        if "Text Completion" in filters:
            filtered_df = filtered_df[filtered_df["Text Completion"] == "✓"]
        if "Chat Completion" in filters:
            filtered_df = filtered_df[filtered_df["Chat Completion"] == "✓"]
        if "Vision" in filters:
            filtered_df = filtered_df[filtered_df["Vision"] == "✓"]

    styled_df = filtered_df.style.apply(apply_row_styles, axis=1, subset=["Model", "API", "Text Completion", "Chat Completion", "Vision"])
    return styled_df

def apply_row_styles(row):
    api_value = row["API"]
    return [
        color_status(api_value, row["Model"]),
        color_status(api_value, row["API"]),
        color_status(api_value, row["Text Completion"]),
        color_status(api_value, row["Chat Completion"]),
        color_status(api_value, row["Vision"])
    ]

def color_status(api_value, cell_value):
    if cell_value == "---":
        if api_value == "Free":
            return 'background-color: green'
        elif api_value == "Pro Subscription":
            return 'background-color: blue'
        elif api_value == "Not Responding":
            return 'background-color: red'
    else:
        if cell_value == "Free":
            return 'background-color: green'
        elif cell_value == "Pro Subscription":
            return 'background-color: blue'
        elif cell_value == "Not Responding":
            return 'background-color: red'
        elif cell_value == "✓":
            return 'background-color: green'
        elif cell_value == "⌀":
            return 'background-color: red'
    return ''

def search_models(query, filters = [], use_cache = True):
    return display_table(query, filters,  use_cache)

description = """
This is a space that retrieves the status of supported HF LLM Serverless Inference APIs.
*Updates every 2 hours!*
If you are a student or you just want to quickly see what models are available to experiment for free, you are most likely highly interested on the free API huggingface provides... but like me, you struggle to find what models are available or not!
This is why I made this space that every 2 hours checks and updates the status of the list of LLMs that are cached and, in theory, supported by retrieving the list in `InferenceClient().list_deployed_models()`.
*It may not have all of the available ones... for now... it's WIP*
So all you need is to plug:
```py
from huggingface_hub import InferenceClient
inf = InferenceClient(model = "MODEL", token = "TOKEN")
response = inf.text_generation("And play !!")
print(response)
"""
first_run = True
all_models = []
loop_query_data()
with gr.Blocks() as demo:
    gr.Markdown("## HF Serverless LLM Inference API Status")
    gr.Markdown(description)
    search_box = gr.Textbox(label="Search for a model", placeholder="Type model name here...")
    filter_box = gr.CheckboxGroup(choices=["Free", "Pro Subscription", "Not Responding", "Text Completion", "Chat Completion", "Vision"], label="Filters")
    table = gr.Dataframe(value=display_table(use_cache=True), headers="keys")

def update_filters(query, filters):
    return search_models(query, filters, use_cache=True)

search_box.change(fn=update_filters, inputs=[search_box, filter_box], outputs=table)
filter_box.change(fn=update_filters, inputs=[search_box, filter_box], outputs=table)

def update_every_two_hours(first_run):
    search_models(search_box.value, use_cache = first_run)
    Timer(60, update_every_two_hours, args=(False,)).start()

Timer(0, update_every_two_hours, args=(first_run,)).start()
