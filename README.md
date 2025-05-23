# TODOs

[x] add break option to interrupt (too) long (misguided) answers. pynput threads globvars.
[] add multiline option, strg+enter for instance
[] add commands like /sum or /tweet
[] make a executable (pyinstaller)
[] add web input
[] autocheck the best ollama model
[] use phi3 for german, its supposedly good
[] add numchars/numtokens as bottom status line

# SKALE.DEV LLM Inference Examples

This repository is a collection of scripts demonstrating the inference capabilities of several Large Language Models (LLMs) across a variety of providers.

## Providers

Here's a quick overview of the platforms and APIs featured in this collection, along with the benefits they offer:

- [NVIDIA GPU Cloud](https://catalog.ngc.nvidia.com/) (NGC) API  
  Offers 1500 free inferences for any model listed in the NGC catalogue.
- [Huggingface Hub Models](https://huggingface.co/docs/api-inference/index) API  
  Features a selection of models, including Mixtral and Mistral7b, available for free use.
- [Groq](https://console.groq.com/) API  
  free mixtral inference
- [Anthropic](https://console.anthropic.com/) API  
  Grants $10 USD credit for inferring with haiku, sonnet, and opus models.
- [Cohere](https://coral.cohere.com/) API  
  command-r inference with web tool.
- [OpenRouter](https://openrouter.ai/playground) API  
  Offers free Mistral inference.
- [Ollama](https://ollama.com/) A solution for self-hosting.
- [ ] LM-Studio Self Hosted
- [ ] Jan Self Hosted
- liteLLM An OpenAI API wrapper for simplified access.

## Model Parameters and Keyfiles

This repository is designed to streamline the inference process with various Large Language Models (LLMs) by providing pre-configured parameters and simplifying API key management. Here's how it works:

### Pre-configured Model Parameters

The models.json file contains the optimal settings for each model, ensuring you can start inference tasks with configurations tuned for general use. These parameters have been carefully selected to balance performance and resource usage effectively.

### API Key Management

API keys are essential for accessing model inference APIs securely. To manage these keys:
Store them in the keys.json file. This file should be structured to map each service provider to its corresponding API key.
The script loads API keys at runtime from keys.json, ensuring each call to an inference service is authenticated seamlessly.

### Security Note

Do not commit keys.json to public repositories to avoid unauthorized access to your API keys. keys.json is added to .gitignore to prevent accidental uploads.

## Features 🌟

Dive into the versatility and power of our inference scripts, designed to simplify and enhance your interactions with various Large Language Models (LLMs). Here's what makes our collection stand out:

- **Model Parameter Abstraction**: Configuration of model parameters is streamlined through JSON files, allowing for easy adjustments without altering the code.
- **Secure API Key Management**: API keys are safely stored in key.json, ensuring secure access to inference services while keeping sensitive information out of the codebase.
- **Efficient Streaming Response**: Experience real-time, streaming responses for continuous interaction with models, ensuring minimal latency in receiving outputs.
- **Message Templates**: Jumpstart your queries with pre-defined message templates tailored for specific requests including summarization, questions, tweets, and elaboration tasks.
- **Inference Options**: Whether you prefer hitting API endpoints or running models locally, our scripts support both approaches, offering you the freedom to choose based on your needs.
- **OpenAI Abstraction with liteLLM**: Simplify your OpenAI interactions using liteLLM, our custom wrapper that abstracts away complexity, making it easier to work with OpenAI's offerings.
- **Native OpenAI API Support**: Enjoy out-of-the-box support for OpenAI API, complemented by seamless integrations with services like Anthropic, Groq, and OpenRouter, broadening your model access options.
- [ ] **Function Calling**

## Requirements

- Python 3.6+
- `requests` module

It is suggested to create a venv environment.  
`python -m venv envllm`  
 activate it with  
`source envllm/bin/activate`

## Setup

```bash
pip install requests
```

## Configuration

Create keys.json with your API credentials and models.json for model parameters.

Example models.json:

## Usage

Run the ngc infer script example with:

```bash
python ngcinfer.py [-llm MODEL_NAME] [-q QUESTION]
```

```text
python ngcinfer.py -q "what are some hipster breakfast spots in san francisco"

q: what are some hipster breakfast spots in san francisco

--

a: Hi there! I'd be happy to help you find some hipster breakfast spots in San Francisco. Here are a few options:

1. The Breakfast Spot: This cozy cafe serves up delicious breakfast sandwiches, avocado toast, and artisanal coffee.

2. The Breakfast Nook: This trendy spot offers a variety of breakfast dishes, including vegan options and gluten-free pancakes.

3. The Breakfast Bar: This popular spot serves up classic breakfast dishes like eggs, bacon, and pancakes, as well as more unique options like breakfast burritos and breakfast tacos.

4. The Breakfast Bistro: This charming cafe serves up fresh-baked pastries, artisanal coffee, and a variety of breakfast dishes, including omelets and frittatas.

5. The Breakfast Shack: This casual spot serves up classic breakfast dishes like eggs, bacon, and pancakes, as well as more unique options like breakfast burritos and breakfast tacos.

I hope this helps! Let me know if you have any other questions.
```

## Text Classification Utilities

### classify_file.py

Performs zero-shot text classification using Huggingface's Inference API. Features:

- Classifies input text into predefined categories (contracts, legal advice, insurance)
- Supports both direct text input and file processing
- Uses the typeform/distilbert-base-uncased-mnli model
- Includes test mode with predefined input
- Handles API authentication via getparams module

Usage:

```bash
python classify_file.py "Text to classify"
python classify_file.py -f input.txt
python classify_file.py -t  # Test mode
```

## Document Processing Utilities

### fnamer.py

Analyzes text documents using AI models to:

- Generate descriptive filenames and summaries (mode 's')
- Classify documents into predefined categories (mode 'k')
- Supports multiple AI providers (Huggingface, Ollama, OpenAI, Google)
- Processes streaming responses for real-time output
- Handles OCR-scanned documents with potential text errors

### dirnamer.py

Batch processes Markdown files in directories to:

- Generate summaries or classifications for multiple files
- Supports the same AI providers as fnamer.py
- Saves results to analysis_results.json
- Includes rate limiting to avoid API throttling
- Preserves existing results and only updates changed files

## Directory Analysis Utilities

The `dirnamer.py` script provides batch processing capabilities for analyzing Markdown files in a directory structure:

- Processes all `.md` files matching a specified tag filter (default: "llama")
- Supports multiple AI providers (Huggingface, Ollama, OpenAI, Google)
- Offers two analysis modes: summary ('s') or classification ('k')
- Saves results to `analysis_results.json` in the target directory
- Includes rate limiting to avoid API throttling
- Preserves existing results and only updates changed files

Usage:

```bash
python dirnamer.py DIRECTORY [--provider PROVIDER] [--model MODEL] [--mode MODE] [-n NUMMAX] [-tag TAG]
```

## Filebrowser Integration

The `filebrowser_list.py` script provides utilities for interacting with a Filebrowser instance:

- `login_to_filebrowser(host, username, password)`: Authenticates with Filebrowser and returns an auth cookie
- `list_directory(host, auth_cookie, dir_path='/')`: Lists contents of a specified directory
- `download_file(host, auth_cookie, file_path)`: Downloads a file from Filebrowser

The script includes example usage in its `__main__` section demonstrating authentication and directory listing.

## License

MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
