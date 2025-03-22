"""
Interactive example to select a provider and ask a question with streaming output.

This script uses the inquirer library for interactive prompts.
"""
import sys
import os
import inquirer
import time

# Add the parent directory to the Python path to make the uniinfer package importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from credgoo import get_api_key
    HAS_CREDGOO = True
except ImportError:
    HAS_CREDGOO = False
    print("Note: credgoo not found, you'll need to provide API keys manually")

from uniinfer import ChatMessage, ChatCompletionRequest, ProviderFactory

# Check if HuggingFace support is available
try:
    from uniinfer import HuggingFaceProvider
    HAS_HUGGINGFACE = True
except ImportError:
    HAS_HUGGINGFACE = False
    
# Check if Cohere support is available
try:
    from uniinfer import CohereProvider
    HAS_COHERE = True
except ImportError:
    HAS_COHERE = False
    
# Check if Moonshot support is available
try:
    from uniinfer import MoonshotProvider
    HAS_MOONSHOT = True
except ImportError:
    HAS_MOONSHOT = False
    
# Check if OpenAI client is available (for StepFun)
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    
# Check if Groq support is available
try:
    from uniinfer import GroqProvider
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

# Check if AI21 support is available
try:
    from uniinfer import AI21Provider
    HAS_AI21 = True
except ImportError:
    HAS_AI21 = False


# Provider configurations
PROVIDER_CONFIGS = {
    'mistral': {
        'name': 'Mistral AI',
        'default_model': 'mistral-small-latest',
        'needs_api_key': True,
    },
    'anthropic': {
        'name': 'Anthropic (Claude)',
        'default_model': 'claude-3-sonnet-20240229',
        'needs_api_key': True,
    },
    'openai': {
        'name': 'OpenAI',
        'default_model': 'gpt-3.5-turbo',
        'needs_api_key': True,
    },
    'ollama': {
        'name': 'Ollama (Local)',
        'default_model': 'llama2',
        'needs_api_key': False,
        'extra_params': {
            'base_url': 'http://localhost:11434'
        }
    },
    'arli': {
        'name': 'ArliAI',
        'default_model': 'Mistral-Nemo-12B-Instruct-2407',
        'needs_api_key': True,
    },
    'openrouter': {
        'name': 'OpenRouter',
        'default_model': 'moonshotai/moonlight-16b-a3b-instruct:free',
        'needs_api_key': True,
    },
    'internlm': {
        'name': 'InternLM',
        'default_model': 'internlm3-latest',
        'needs_api_key': True,
        'extra_params': {
            'top_p': 0.9
        }
    },
    'stepfun': {
        'name': 'StepFun AI',
        'default_model': 'step-1-8k',
        'needs_api_key': True,
    },
    'sambanova': {
        'name': 'SambaNova',
        'default_model': 'Meta-Llama-3.1-8B-Instruct',
        'needs_api_key': True,
    },
    'upstage': {
        'name': 'Upstage AI',
        'default_model': 'solar-pro',
        'needs_api_key': True,
    }
}

# Add HuggingFace if available
if HAS_HUGGINGFACE:
    PROVIDER_CONFIGS['huggingface'] = {
        'name': 'HuggingFace Inference',
        'default_model': 'mistralai/Mistral-7B-Instruct-v0.3',
        'needs_api_key': True,
    }

# Add Cohere if available
if HAS_COHERE:
    PROVIDER_CONFIGS['cohere'] = {
        'name': 'Cohere',
        'default_model': 'command-r-plus-08-2024',
        'needs_api_key': True,
    }

# Add Moonshot if available
if HAS_MOONSHOT:
    PROVIDER_CONFIGS['moonshot'] = {
        'name': 'Moonshot AI',
        'default_model': 'moonshot-v1-8k',
        'needs_api_key': True,
    }

# Add Groq if available
if HAS_GROQ:
    PROVIDER_CONFIGS['groq'] = {
        'name': 'Groq',
        'default_model': 'llama-3.1-8b',
        'needs_api_key': True,
    }

# Add AI21 if available
if HAS_AI21:
    PROVIDER_CONFIGS['ai21'] = {
        'name': 'AI21 Labs',
        'default_model': 'jamba-mini-1.6-2025-03',
        'needs_api_key': True,
    }

DEFAULT_QUESTION = "Explain how transformers work in machine learning in simple terms."


def select_provider():
    """
    Prompt the user to select a provider from the list of available providers.
    
    Returns:
        str: The selected provider ID.
    """
    # Create a list of provider choices
    choices = [
        (f"{config['name']} ({provider_id})", provider_id)
        for provider_id, config in PROVIDER_CONFIGS.items()
    ]
    
    questions = [
        inquirer.List('provider',
                     message="Select a provider:",
                     choices=choices,
                     carousel=True)
    ]
    
    answers = inquirer.prompt(questions)
    return answers['provider']


def get_provider_instance(provider_id):
    """
    Get a provider instance with the appropriate API key.
    
    Args:
        provider_id (str): The provider ID.
        
    Returns:
        tuple: (provider, model) - The provider instance and default model.
    """
    config = PROVIDER_CONFIGS[provider_id]
    provider_kwargs = config.get('extra_params', {})
    model = config['default_model']
    
    # Handle API key for providers that need one
    if config['needs_api_key']:
        if HAS_CREDGOO:
            try:
                api_key = get_api_key(provider_id)
                print(f"Using API key from credgoo for {config['name']}.")
            except Exception as e:
                print(f"Failed to get API key from credgoo: {str(e)}")
                api_key = inquirer.text(
                    message=f"Enter your {config['name']} API key:"
                )
        else:
            api_key = inquirer.text(
                message=f"Enter your {config['name']} API key:"
            )
        
        # Get model options for this provider if desired
        # For simplicity, we'll use the default model
        
        provider = ProviderFactory.get_provider(provider_id, api_key=api_key, **provider_kwargs)
    else:
        # For providers like Ollama that don't need an API key
        provider = ProviderFactory.get_provider(provider_id, **provider_kwargs)
    
    return provider, model


def get_user_question():
    """
    Get the user's question.
    
    Returns:
        str: The user's question.
    """
    question = inquirer.text(
        message="What's your question? (press Enter for default):",
    )
    
    if not question:
        question = DEFAULT_QUESTION
        print(f"Using default question: {question}")
    
    return question


def main():
    """Main function to run the interactive provider example."""
    print("=== UniInfer Interactive Provider Example ===\n")
    
    # Get the user to select a provider
    provider_id = select_provider()
    config = PROVIDER_CONFIGS[provider_id]
    print(f"\nYou selected: {config['name']}")
    
    # Get the provider instance
    try:
        provider, model = get_provider_instance(provider_id)
    except Exception as e:
        print(f"Error initializing provider: {str(e)}")
        return
    
    # Get the user's question
    question = get_user_question()
    
    # Create the request
    messages = [
        ChatMessage(role="system", content="You are a helpful, knowledgeable assistant."),
        ChatMessage(role="user", content=question)
    ]
    
    request = ChatCompletionRequest(
        messages=messages,
        model=model,
        temperature=0.7,
        streaming=True
    )
    
    # Provider-specific parameters
    provider_specific_params = {}
    if provider_id == 'arli':
        provider_specific_params = {
            "repetition_penalty": 1.1,
            "top_p": 0.9,
            "top_k": 40,
        }
    elif provider_id == 'internlm':
        provider_specific_params = {
            "top_p": 0.9
        }
    
    # Execute the request
    print("\n=== Response ===\n")
    try:
        # Stream the response
        start_time = time.time()
        response_text = ""
        
        for chunk in provider.stream_complete(request, **provider_specific_params):
            content = chunk.message.content
            print(content, end="", flush=True)
            response_text += content
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        print(f"\n\n=== Completed in {elapsed_time:.2f} seconds ===")
        
        # Ask if the user wants to save the response
        save_response = inquirer.confirm(
            message="Would you like to save this response to a file?",
            default=False
        )
        
        if save_response:
            filename = inquirer.text(
                message="Enter filename (or press Enter for default):",
                default=f"{provider_id}_response.txt"
            )
            
            with open(filename, 'w') as f:
                f.write(f"Question: {question}\n\n")
                f.write(f"Response from {config['name']} ({model}):\n\n")
                f.write(response_text)
            
            print(f"Response saved to {filename}")
    
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Make sure the provider is correctly configured and accessible.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation canceled by user.")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
