import google.generativeai as genai
import os
from typing import List, Dict
import textwrap
from rich.console import Console
from rich.markdown import Markdown

class GeminiChat:
    def __init__(self, api_key: str):
        """Initialize the Gemini chat client."""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.chat = self.model.start_chat(history=[])
        self.history: List[Dict[str, str]] = []
        self.console = Console()

    def format_response(self, text: str) -> Markdown:
        """Format the response text using Markdown."""
        return Markdown(text)


    def chat_loop(self):
        """Run the main chat loop with streaming."""
        print("Welcome to Gemini Chat! Type 'quit' to exit.")
        print("-" * 50)

        try:
            while True:
                # Get user input
                user_input = input("\nYou: ").strip()

                if user_input.lower() in ['quit', 'exit']:
                    print("\nGoodbye!")
                    break

                if not user_input:
                    continue

                try:
                    # Send message to Gemini and get response stream
                    response_stream = self.chat.send_message(user_input, stream=True)
                    
                    # Store user message in history
                    self.history.append({
                        "role": "user",
                        "content": user_input
                    })

                    self.console.print("\nGemini: ", end="", style="bold cyan")
                    full_response = ""
                    for chunk in response_stream:
                        if chunk.text:
                            full_response += chunk.text

                    formatted_text = self.format_response(full_response)
                    self.console.print(formatted_text, style="default")

                    # Store assistant response in history
                    self.history.append({
                        "role": "assistant",
                        "content": full_response
                    })

                except Exception as e:
                    print(f"\nError getting response: {str(e)}")
        
        except KeyboardInterrupt:
                print("\n\nChat session ended by user.")


def main():
    """Main function to run the chat application."""
    # Get API key from environment variable
    api_key = 'AIzaSyAgrLrWGPs9n5ijbPu52VPbhWI7ykL-stI'
    
    if not api_key:
        print("Please set your GOOGLE_API_KEY environment variable")
        print("You can get an API key from: https://makersuite.google.com/app/apikey")
        return

    try:
        chat = GeminiChat(api_key)
        chat.chat_loop()
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
