import argparse
import json
import os
from google import genai
from credgoo import get_api_key
from jsonclean import cleanify_json


def main():
    parser = argparse.ArgumentParser(
        description="Analyze a file using a prompt with Google's Gemini model.")
    parser.add_argument("-p", "--prompt", required=True,
                        help="Path to the prompt file.")
    parser.add_argument("-f", "--file", required=True,
                        help="Path to the file to analyze.")
    parser.add_argument("-o", "--output", required=True,
                        help="Path to the output JSON file.")
    args = parser.parse_args()

    try:
        with open(args.prompt, 'r', encoding='utf-8') as f:
            prompt_text = f.read()
    except FileNotFoundError:
        print(f"Error: Prompt file not found at {args.prompt}")
        return

    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            file_text = f.read()
    except FileNotFoundError:
        print(f"Error: File to analyze not found at {args.file}")
        return

    client = genai.Client(api_key=get_api_key("gemini"))

    # Combine the prompt and the file content
    # You might want to adjust how they are combined based on your prompt's structure
    full_prompt = f"{prompt_text}\n\n---\n\n{file_text}"

    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=full_prompt
    )

    if args.output.endswith('.json'):
        output_data = cleanify_json(response.text)
    else:
        output_data = {"analysis_result": response.text}

    # Ensure the output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(f"Analysis complete. Output saved to {args.output}")


if __name__ == "__main__":
    main()
