import argparse
import json
import os
import threading
import time
import sys
from google import genai
from credgoo import get_api_key
from jsonclean import cleanify_json


class Spinner:
    def __init__(self, message="Processing"):
        self.spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.message = message
        self.spinning = False
        self.thread = None

    def spin(self):
        i = 0
        while self.spinning:
            sys.stdout.write(
                f'\r{self.message} {self.spinner_chars[i % len(self.spinner_chars)]}')
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1

    def start(self):
        self.spinning = True
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()

    def stop(self):
        self.spinning = False
        if self.thread:
            self.thread.join()
        sys.stdout.write('\r' + ' ' * (len(self.message) + 2) + '\r')
        sys.stdout.flush()


def load_existing_json(file_path):
    """Load existing JSON file if it exists, otherwise return empty dict."""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}


def merge_json_with_insert(existing_data, new_data, insert_key):
    """Merge new data into existing JSON, clearing only the specified key."""
    if insert_key:
        # Clear only the specified key and replace with new data
        if insert_key in new_data:
            existing_data[insert_key] = new_data[insert_key]
            print(f"🔄 Cleared and updated '{insert_key}' section")
        else:
            print(f"⚠️  Warning: Key '{insert_key}' not found in new data")
    else:
        # Replace entire structure
        existing_data.update(new_data)
    return existing_data


def main():
    parser = argparse.ArgumentParser(
        description="Analyze a file using a prompt with Google's Gemini model.")
    parser.add_argument("-p", "--prompt", required=True,
                        help="Path to the prompt file.")
    parser.add_argument("-f", "--file", required=True,
                        help="Path to the file to analyze.")
    parser.add_argument("-o", "--output", required=True,
                        help="Path to the output JSON file.")
    parser.add_argument("-i", "--insert", type=str,
                        help="Insert mode: specify JSON key to clear and replace (e.g., 'meta', 'kriterien')")
    args = parser.parse_args()

    try:
        print("📄 Reading prompt file...")
        with open(args.prompt, 'r', encoding='utf-8') as f:
            prompt_text = f.read()
        print(f"✅ Prompt loaded from {args.prompt}")
    except FileNotFoundError:
        print(f"❌ Error: Prompt file not found at {args.prompt}")
        return

    try:
        print("📄 Reading input file...")
        with open(args.file, 'r', encoding='utf-8') as f:
            file_text = f.read()
        print(
            f"✅ File loaded from {args.file} ({len(file_text):,} characters)")
    except FileNotFoundError:
        print(f"❌ Error: File to analyze not found at {args.file}")
        return

    print("🔑 Initializing Gemini client...")
    client = genai.Client(api_key=get_api_key("gemini"))

    # Combine the prompt and the file content
    full_prompt = f"{prompt_text}\n\n---\n\n{file_text}"

    print(
        f"🚀 Sending request to Gemini (Total: {len(full_prompt):,} characters)...")
    spinner = Spinner("🤖 Waiting for Gemini response")
    spinner.start()

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=full_prompt
        )
    except Exception as e:
        spinner.stop()
        print(f"❌ Error during API call: {e}")
        return
    finally:
        spinner.stop()

    print("✅ Response received!")

    print("🧹 Processing response...")
    if args.output.endswith('.json'):
        spinner = Spinner("📊 Cleaning JSON")
        spinner.start()
        try:
            new_data = cleanify_json(response.text)
        finally:
            spinner.stop()
    else:
        new_data = {"analysis_result": response.text}

    # Ensure the output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Handle insert mode vs overwrite mode
    if args.insert:
        print(f"🔄 Insert mode: updating '{args.insert}' section...")
        existing_data = load_existing_json(args.output)
        final_data = merge_json_with_insert(existing_data, new_data, args.insert)
        print(f"💾 Updating {args.output}...")
    else:
        print(f"🆕 Overwrite mode: creating new file...")
        final_data = new_data
        print(f"💾 Saving to {args.output}...")

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

    print(f"🎉 Analysis complete! Output saved to {args.output}")

    # Show some stats
    if isinstance(final_data, dict) and 'kriterien' in final_data:
        criteria_count = len(final_data['kriterien'])
        print(f"📊 Extracted {criteria_count} criteria")

    print(f"📁 File size: {os.path.getsize(args.output):,} bytes")


if __name__ == "__main__":
    main()
