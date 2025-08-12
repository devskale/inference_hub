import numpy as np
from openai import OpenAI
from credgoo import get_api_key
import math

# Set up API configuration
API_BASE = "https://aqueduct.ai.datalab.tuwien.ac.at/v1"
TU_API_KEY = get_api_key("tu")

# Configure OpenAI client
openai_api_key = TU_API_KEY
openai_api_base = API_BASE

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    return dot_product / (norm_vec1 * norm_vec2)

def select_embedding_model():
    """Select an embedding-capable model from available models"""
    models = client.models.list()
    
    # Look for embedding models specifically
    embedding_models = []
    for model in models.data:
        model_id = model.id.lower()
        if any(keyword in model_id for keyword in ['embedding', 'e5', 'text-embedding', 'bge', 'gte']):
            embedding_models.append(model.id)
    
    if embedding_models:
        model = embedding_models[0]
        print(f"Using embedding model: {model}")
        return model
    else:
        # Fallback to first model if no embedding-specific models found
        if models.data:
            model = models.data[0].id
            print(f"Warning: No embedding-specific models found, using: {model}")
            return model
        else:
            print("No models found!")
            return None

def generate_embeddings(texts, model):
    """Generate embeddings for a list of texts"""
    responses = client.embeddings.create(
        input=texts,
        model=model
    )
    return [response.embedding for response in responses.data]

def run_embedder_validation():
    """Run validation tests for the embedder"""
    print("=== Embedder Validation Test ===\n")
    
    # Select model
    model = select_embedding_model()
    if not model:
        return False
    
    # Test cases: (text1, text2, expected_similarity_range, description)
    test_cases = [
        (
            "The cat is sitting on the mat",
            "A feline rests on the rug",
            (0.7, 1.0),
            "Similar texts (cat/feline, mat/rug)"
        ),
        (
            "Artificial intelligence transforms industries",
            "Chocolate cake recipes for beginners",
            (0.0, 0.6),
            "Dissimilar texts (AI vs cooking)"
        ),
        (
            "Quantum computing breakthroughs",
            "Quantum computing breakthroughs",
            (1.0, 1.0),
            "Identical texts"
        ),
        (
            "Machine learning algorithms improve with more data",
            "Deep neural networks require large datasets",
            (0.6, 0.9),
            "Related technical topics"
        ),
        (
            "The weather is beautiful today",
            "Photosynthesis occurs in plant chloroplasts",
            (0.0, 0.6),
            "Unrelated topics (weather vs biology)"
        ),
        (
            "The cat sat on the mat and purred quietly.",
            "Investors sold off tech stocks amid rising interest rate concerns.",
            (0.0, 0.4),
            "Completely unrelated topics (cat vs finance)"
        ),
        (
            "No pushing on the swings, and always take turns!",
            "Basel III requires banks to maintain a minimum Tier 1 capital ratio of 6%.",
            (0.0, 0.4),
            "Completely unrelated topics (playground vs banking)"
        )
    ]
    
    all_passed = True
    
    for i, (text1, text2, expected_range, description) in enumerate(test_cases, 1):
        print(f"Test {i}: {description}")
        print(f"  Text 1: '{text1}'")
        print(f"  Text 2: '{text2}'")
        
        # Generate embeddings
        embeddings = generate_embeddings([text1, text2], model)
        embedding1, embedding2 = embeddings[0], embeddings[1]
        
        # Calculate similarity
        similarity = cosine_similarity(embedding1, embedding2)
        
        # Check embedding dimensions
        embedding_dim = len(embedding1)
        print(f"  Embedding dimension: {embedding_dim}")
        
        # Validate similarity
        min_expected, max_expected = expected_range
        passed = min_expected <= similarity <= max_expected
        all_passed = all_passed and passed
        
        print(f"  Cosine similarity: {similarity:.4f}")
        print(f"  Expected range: [{min_expected}, {max_expected}]")
        print(f"  Result: {'✓ PASS' if passed else '✗ FAIL'}")
        print()
    
    # Summary
    print("=== Test Summary ===")
    print(f"Overall result: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
    print(f"Model used: {model}")
    
    return all_passed

if __name__ == "__main__":
    run_embedder_validation()