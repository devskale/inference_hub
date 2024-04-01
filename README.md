# SKALE.DEV LLM Inference Examples

This script compilation is demonstrating inference of severel LLMs on several providers.

## Providers

- [NVIDIA GPU Cloud](https://catalog.ngc.nvidia.com/) (NGC) API
- [Huggingface Hub Models](https://huggingface.co/docs/api-inference/index) API
- [Groq](https://console.groq.com/) API
- [Anthropic](https://console.anthropic.com/) API
- [Cohere](https://coral.cohere.com/) API
- [OpenRouter](https://openrouter.ai/playground) API
- [Ollama](https://ollama.com/) Self Hosted
- [ ] LM-Studio Self Hosted
- [ ] Jan Self Hosted
- liteLLM OpenAI API Wrapper

## Model Parameters and Keyfiles

The parameters for each model are pre-configured in the `models.json` file with optimal settings for general use. API keys are loaded at runtime from `keys.json`.


## Requirements

- Python 3.6+
- `requests` module


## Setup

```bash
pip install requests
```

## Configuration
Create keys.json with your NVIDIA API credentials and models.json for model parameters.

Example models.json:

## Usage
Run the ngc infer script example with:

```bash
python ngcinfer.py [-llm MODEL_NAME] [-q QUESTION]
````

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

## License
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

