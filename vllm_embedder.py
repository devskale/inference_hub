import os
from openai import OpenAI

def get_embedding(base_url: str, api_key: str, model: str, text_input: str):
    """
    Accesses an embedding model via a vLLM endpoint to get the embedding for a given text.

    Args:
        base_url (str): The base URL of the vLLM server (e.g., "http://localhost:8000/v1").
        api_key (str): The API key for the vLLM server (can be a placeholder like "EMPTY").
        model (str): The name of the embedding model to use.
        text_input (str): The text to get the embedding for.

    Returns:
        list: The embedding vector for the input text.
    """
    try:
        # Instantiate the OpenAI client to connect to the vLLM server
        client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )

        # Request the embedding from the model
        embedding_response = client.embeddings.create(
            model=model,
            input=[text_input]
        )

        # Extract the embedding vector
        embedding = embedding_response.data[0].embedding
        return embedding

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    # --- Configuration Variables ---
    # The base URL for your vLLM instance.
    # This should point to the v1 API endpoint, which is standard for OpenAI compatibility.
    VLLM_BASE_URL = "http://localhost:8000/v1"

    # The API key for your vLLM instance.
    # For many local vLLM setups, this can be a placeholder string like "EMPTY" or "NA".
    VLLM_API_KEY = "EMPTY"

    # The name of the model you are serving with vLLM.
    # This should match the model name loaded by the vLLM server.
    MODEL_NAME = "e5-mistral-7b-instruct"

    # Example text to embed
    example_text = "This is a test sentence to be embedded by the model."

    print(f"Requesting embedding for model: {MODEL_NAME}")
    print(f"Text: \"{example_text}\"")

    # Get the embedding
    embedding_vector = get_embedding(
        base_url=VLLM_BASE_URL,
        api_key=VLLM_API_KEY,
        model=MODEL_NAME,
        text_input=example_text
    )

    if embedding_vector:
        print(f"Successfully retrieved embedding.")
        print(f"Embedding dimension: {len(embedding_vector)}")
        # Print the first 5 elements of the vector as a sample
        print(f"Embedding preview: {embedding_vector[:5]}...")
    else:
        print("Failed to retrieve embedding.")

    # Example of how to use environment variables for configuration
    # VLLM_BASE_URL_ENV = os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1")
    # VLLM_API_KEY_ENV = os.getenv("VLLM_API_KEY", "EMPTY")
    # print("\n--- Example using environment variables ---")
    # embedding_from_env = get_embedding(VLLM_BASE_URL_ENV, VLLM_API_KEY_ENV, MODEL_NAME, "Another test.")
    # if embedding_from_env:
    #     print("Successfully retrieved embedding using environment variable configuration.")
