
from openai import OpenAI
from credgoo import get_api_key

# Set your API key
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
#api_key = get_api_key("tu")

API_BASE = "https://aqueduct.ai.datalab.tuwien.ac.at/v1"
TU_API_KEY = get_api_key("tu")

# Modify OpenAI's API key and API base to use vLLM's API server.
openai_api_key = TU_API_KEY
openai_api_base = API_BASE

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=openai_api_key,
    base_url=openai_api_base,
)

# List available models and select an embedding-capable one
models = client.models.list()

# Look for embedding models specifically
embedding_models = []
for model in models.data:
    model_id = model.id.lower()
    if any(keyword in model_id for keyword in ['embedding', 'e5', 'text-embedding', 'bge', 'gte']):
        embedding_models.append(model.id)

if embedding_models:
    model = embedding_models[0]  # Use first embedding model found
    print(f"Using embedding model: {model}")
else:
    # Fallback to first model if no embedding-specific models found
    if models.data:
        model = models.data[0].id
        print(f"Warning: No embedding-specific models found, using: {model}")
    else:
        print("No models found!")
        exit(1)

# Create embeddings
responses = client.embeddings.create(input=[
    "Hello my name is",
    "The best thing about vLLM is that it supports many different models"
],
    model=model
)

# Print the embeddings
for i, data in enumerate(responses.data):
    print(f"Embedding {i} (length: {len(data.embedding)}):")
    print(f"First 10 values: {data.embedding[:10]}")
    print()
