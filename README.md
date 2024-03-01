# NVIDIA Invocation API Utility

This utility script is tailored for making API requests to NVIDIA's Large Language Models (LLMs). It facilitates the process by reading API credentials and model parameters from JSON files, constructing and sending requests, and managing streaming JSON responses.

Please register at https://ngc.nvidia.com/signin to being able to infer state of the art open source LLMs.

## Features

- Load NVIDIA API credentials from a JSON file.
- Load NVIDIA model parameters from a JSON file.
- Support for multiple NVIDIA models including gemma7b, mixtral, mistral7b, phi2, and yi34b.
- Send requests to NVIDIA's API endpoint.
- Handle streaming JSON responses.

## Supported Models and Parameters

The script currently supports the following NVIDIA models with specified parameters:

- `gemma7b`: Moderate creativity with a focus on relevance.
- `mixtral`: Balanced approach for creativity and relevance.
- `mistral7b`: Similar to mixtral with a different parameter tuning.
- `phi2`: Designed for tasks requiring precise language understanding.
- `yi34b`: For applications that benefit from a very large model size.

The parameters for each model are pre-configured in the `models.json` file with optimal settings for general use.

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
Run the script with:

```bash
python ngcinfer.py [-llm MODEL_NAME] [-q QUESTION]
````

```text
python ngcinfer.py -llm phi2 -q "what are some hipster breakfast spots in san francisco"

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

