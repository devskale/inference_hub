import google.generativeai as genai
import os
from typing import List, Dict
from rich.console import Console
from rich.markdown import Markdown
from getparams import load_api_credentials
import time

class GeminiChat:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.chat = self.model.start_chat(history=[])
        self.history: List[Dict[str, str]] = []
        self.console = Console()

    def format_response(self, text: str) -> Markdown:
        return Markdown(text)

    def chat_loop(self):
        print("Welcome to Gemini Chat! Type 'quit' to exit.")
        print("-" * 50)

        try:
            while True:
                user_input = input("\nYou: ").strip()
                if user_input.lower() in ['quit', 'exit']:
                    print("\nGoodbye!")
                    break
                if not user_input:
                    continue

                try:
                    # Command handling
                    if user_input.startswith('/'):
                        command, *args = user_input[1:].split(maxsplit=1) # maxsplit=1 limits to 2 parts
                        if command in self.commands:
                            if args: # Check if arguments were passed
                                self.commands[command](self, args) # pass args as a single string
                            else:
                                print(f"Command '{command}' requires arguments.")
                        else:
                            print(f"Unknown command: {command}")
                    else:  # Gemini interaction
                        response_stream = self.chat.send_message(user_input, stream=True)
                        self.history.append({"role": "user", "content": user_input})
                        self.console.print("\nGemini: ", end="", style="bold cyan")

                        buffer = ""
                        for chunk in response_stream:
                            if chunk.text:
                                buffer += chunk.text
                                lines = buffer.splitlines()
                                for line in lines[:-1]:
                                    formatted_text = self.format_response(line)
                                    self.console.print(formatted_text, style="default")
                                buffer = lines[-1]

                        if buffer:
                            formatted_text = self.format_response(buffer)
                            self.console.print(formatted_text, style="default")
                        print()  # Add newline at the end

                except Exception as e:
                    print(f"\nError: {e}")

        except KeyboardInterrupt:
            print("\n\nChat session ended by user.")


    def tweet(self, text: str):
        """Generates a tweet using Gemini."""
        try:
            response = self.chat.send_message(f"Write a short engaging tweet about this: {text}") #Use the chat interface
            self.console.print("\nTweet: ", end="", style="bold magenta")
            self.console.print(self.format_response(response.text), style="default")
            print()
        except Exception as e:
            print(f"\nError generating tweet: {e}")

    def summarize(self, text: str):
        """Summarizes the given text using Gemini."""
        #Use Gemini to Summarize the given text
        response = self.model.generate_text(text=text, temperature=0, max_output_tokens=100, prompt="Summarize this text: " + text)
        self.console.print("\nSummary: ", end="", style="bold magenta")
        self.console.print(self.format_response(response.text), style="default")
        print()


    commands = {
        "tweet": tweet,
        "summarize": summarize,  # Add the summarize function
    }

def main():
    api_key = load_api_credentials('gemini')
    if not api_key:
        print("Please set your GOOGLE_API_KEY environment variable.")
        return

    try:
        chat = GeminiChat(api_key)
        chat.chat_loop()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
