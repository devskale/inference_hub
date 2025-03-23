# Import uniinfer components
from uniinfer import (
    ChatMessage,
    ChatCompletionRequest,
    ProviderFactory,
    ChatProvider
)
from credgoo import get_api_key
# Cloudflare API Details


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
        'default_model': 'gemma3:4b',
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
    },
    'ngc': {
        'name': 'NVIDIA GPU Cloud (NGC)',
        'default_model': 'deepseek-ai/deepseek-r1-distill-llama-8b',
        'needs_api_key': True,
    },
    'cloudflare': {
        'name': 'Cloudflare Workers AI',
        'default_model': '@cf/meta/llama-3.1-8b-instruct',
        'needs_api_key': True,
        'extra_params': {
            'account_id': '1ee331dfd225ac49d67c521a73ca7fe8'  # Will be prompted during setup
        }
    }
}


def main():
    # Initialize the provider factory

    provider = "openrouter"

    # Initialize the provider factory
    uni = ProviderFactory().get_provider(
        provider,
        api_key=get_api_key(provider),
        # account_id=PROVIDER_CONFIGS[provider].get('extra_params', {}).get('account_id', None)
    )

    prompt = "Explain in a few sentences in simple words how transformers work in machine learning."
    # Create a simple chat request
    messages = [
        ChatMessage(role="user", content=prompt)
    ]
    request = ChatCompletionRequest(
        messages=messages,
    )
    # Make the request

    response = uni.complete(request)
    print(response.message.content)


if __name__ == "__main__":
    main()
