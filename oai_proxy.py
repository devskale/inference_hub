# use .env variables
# OPENAI_BASE=
# OPENAI_KEY=

import tty
import termios
import sys
import itertools
import os
import openai
from dotenv import load_dotenv

load_dotenv()
OPENAI_BASE = os.getenv("OPENAI_BASE")
OPENAI_KEY = os.getenv("OPENAI_KEY")
# OPENAI_BASE = "https://amd1.mooo.com:8123/v1"
# OPENAI_KEY = "test23@test34"
# and run against it several requests
Models = [
    # tu models
    "tu@deepseek-r1",
    "tu@qwen-coder-32b",
    "tu@mistral-small-3.1-24b",
    "tu@mistral-large-123b",
    "tu@qwen-32b",
    # arli
    "arli@Gemma-3-27B-it",
    #
]

Sample_Prompts = [
    "Erzähl einen Witz vom Onkel Fritz",
    "Was ist der Sinn des Lebens?",
    "Schreib ein kurzes Gedicht über den Herbst",
    "Erkläre Quantenverschränkung in einfachen Worten",
    "Beschreibe einen Tag im Leben eines Eichhörnchens aus seiner Perspektive",
    "Was wäre, wenn die Menschheit auf einem anderen Planeten leben würde?",
    "Schreibe eine kurze Geschichte über eine sprechende Kaffeetasse",
    "Diskutiere die Vor- und Nachteile von künstlicher Intelligenz im Alltag",
    "Wie funktioniert ein Schwarzes Loch? Erkläre es einem Kind",
]

# write a script that runs an arbitrary sample prompt against a model (round robin)

# Load environment variables
# OPENAI_BASE = os.getenv("OPENAI_BASE")
# OPENAI_KEY = os.getenv("OPENAI_KEY")

# Initialize OpenAI client
client = openai.OpenAI(
    base_url=OPENAI_BASE,
    api_key=OPENAI_KEY
)


def getch():
    """
    Waits for a single character input from the user without requiring Enter.
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def run_prompt_against_model(model_name, prompt):
    """
    Runs a single prompt against a specified model using the OpenAI API.
    """
    print(f"\n--- Running prompt against model: {model_name} ---")
    print(f"Prompt: {prompt}")
    try:
        chat_completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            stream=True
        )
        full_response_content = ""
        for chunk in chat_completion:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")
                full_response_content += chunk.choices[0].delta.content
        print(f"\nFull Response: {full_response_content}")
        return full_response_content
    except Exception as e:
        print(f"Error running prompt: {e}")
        return None


import random
def run_round_robin_prompts(models, prompts):
    """
    Runs sample prompts against models in a random fashion, waiting for a keypress after each.
    Quits when 'q' is pressed.
    """
    if not models or not prompts:
        print("No models or prompts available to run.")
        return

    model_iterator = itertools.cycle(models)

    # Run each prompt against each model once for demonstration
    for i in range(len(models) * len(prompts)):
        model = next(model_iterator)
        prompt = random.choice(prompts) # Select a random prompt
        run_prompt_against_model(model, prompt)
        if i < (len(models) * len(prompts)) - 1:
            print("\nPress any key to continue (q to quit)...")
            key = getch()
            if key.lower() == 'q':
                print("\nQuitting...")
                return


if __name__ == "__main__":
    print("Starting random prompt execution...")
    run_round_robin_prompts(Models, Sample_Prompts)
    print("Random execution finished.")
