# test_embedding_debug.py
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def test_models():
    models = [
        "sentence-transformers/all-MiniLM-L6-v2",
        "BAAI/bge-small-en-v1.5",
        "all-MiniLM-L6-v2",  # Try without prefix
        "multi-qa-MiniLM-L6-cos-v1"  # Another good option
    ]
    
    # Your exact texts
    query = "Does Linked list help with browser history functionality ?"
    chunk_text = "Browser history functionality"
    
    print("Testing embedding models...")
    print(f"Query: '{query}'")
    print(f"Chunk: '{chunk_text}'")
    print("=" * 60)
    
    for model_name in models:
        try:
            print(f"\nTesting: {model_name}")
            model = SentenceTransformer(model_name)
            
            # Test embedding generation
            query_emb = model.encode(query)
            chunk_emb = model.encode(chunk_text)
            
            print(f"Query embedding shape: {query_emb.shape}")
            print(f"Chunk embedding shape: {chunk_emb.shape}")
            
            # Calculate similarity
            similarity = cosine_similarity([query_emb], [chunk_emb])[0][0]
            print(f"Cosine similarity: {similarity:.4f}")
            
            # Test with normalized embeddings
            query_emb_norm = model.encode(query, normalize_embeddings=True)
            chunk_emb_norm = model.encode(chunk_text, normalize_embeddings=True)
            similarity_norm = cosine_similarity([query_emb_norm], [chunk_emb_norm])[0][0]
            print(f"Normalized similarity: {similarity_norm:.4f}")
            
        except Exception as e:
            print(f"Error with {model_name}: {e}")

if __name__ == "__main__":
    test_models()