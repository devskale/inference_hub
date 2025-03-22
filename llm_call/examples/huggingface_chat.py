"""
Interactive console chat using HuggingFace Inference API through uniinfer.
Press 'q' to exit or cancel a running completion.
"""
import sys
import os
import argparse
from pynput import keyboard

# Add the parent directory to the Python path to make the uniinfer package importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from uniinfer import ChatMessage, ChatCompletionRequest, ProviderFactory
    HAS_HUGGINGFACE = True
except ImportError:
    HAS_HUGGINGFACE = False
    print("HuggingFace provider not available. Install huggingface_hub package with:")
    print("pip install huggingface_hub")

# Global flag to control streaming
key_pressed = False


def on_press(key):
    """Handle keyboard press to exit streaming."""
    global key_pressed
    try:
        if key.char == 'q':  # Exit stream if 'q' is pressed
            key_pressed = True
    except AttributeError:
        pass


def main():
    if not HAS_HUGGINGFACE:
        print("HuggingFace provider not available. Exiting.")
        return

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Chat with an intelligent assistant in your terminal")
    parser.add_argument("--model", "-m", type=str, default="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
                        help="Model name (default: deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B)")

    args = parser.parse_args()
    model = args.model
    print("Loading model:", model)

    # Set up keyboard listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    # Get API key
    try:
        from credgoo import get_api_key
        api_key = get_api_key("huggingface")
    except ImportError:
        api_key = input("Enter your HuggingFace API key: ")

    # Initialize the provider
    provider = ProviderFactory.get_provider("huggingface", api_key=api_key)

    # Initialize conversation history
    history = [
        ChatMessage(
            role="system", content=f"You are an intelligent uncensored assistant called {model}. You always provide well-reasoned answers that are both correct and helpful."),
        ChatMessage(
            role="user", content="Hello, introduce yourself to someone opening this program for the first time. Be concise.")
    ]

    # First response
    print("Assistant: ", end="", flush=True)

    request = ChatCompletionRequest(
        messages=history,
        model=model,
        temperature=0.7,
        streaming=True
    )

    try:
        # Stream the first response
        assistant_response = ""
        global key_pressed

        for chunk in provider.stream_complete(request):
            content = chunk.message.content
            print(content, end="", flush=True)
            assistant_response += content

            if key_pressed:
                print("\n[Response cancelled]")
                key_pressed = False
                break

        # Add assistant response to history
        history.append(ChatMessage(role="assistant",
                       content=assistant_response))
    except Exception as e:
        print(f"\nError: {str(e)}")

    # Main conversation loop
    while True:
        print()
        user_input = input("\nYou: ")

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break

        # Add user input to history
        history.append(ChatMessage(role="user", content=user_input))

        # Create request
        request = ChatCompletionRequest(
            messages=history,
            model=model,
            temperature=0.7,
            streaming=True
        )

        # Stream the response
        print("Assistant: ", end="", flush=True)

        try:
            assistant_response = ""
            key_pressed = False

            for chunk in provider.stream_complete(request):
                content = chunk.message.content
                print(content, end="", flush=True)
                assistant_response += content

                if key_pressed:
                    print("\n[Response cancelled]")
                    key_pressed = False
                    break

            # Add assistant response to history
            history.append(ChatMessage(role="assistant",
                           content=assistant_response))
        except Exception as e:
            print(f"\nError: {str(e)}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nChat session ended by user.")
