# app/services/qa_service.py
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from chromadb.errors import NotFoundError
from app.core.config import settings

# Initialize clients
embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)

class QAService:
    
    def __init__(self):
        # Don't try to get collections in __init__ - they might not exist yet
        self.topic_collection = None
        self.problem_collection = None
    
    def _get_topic_collection(self):
        """Lazy loading of topic collection"""
        if self.topic_collection is None:
            try:
                self.topic_collection = chroma_client.get_collection("topics")
            except NotFoundError:
                # Collection doesn't exist yet, return None
                return None
        return self.topic_collection
    
    def _get_problem_collection(self):
        """Lazy loading of problem collection"""
        if self.problem_collection is None:
            try:
                self.problem_collection = chroma_client.get_collection("problems")
            except NotFoundError:
                # Collection doesn't exist yet, return None
                return None
        return self.problem_collection
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for query text."""
        try:
            embedding = embedding_model.encode(text).tolist()
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise
    
    def retrieve_relevant_chunks(self, query: str, collection_type: str = "topics", n_results: int = 5) -> List[Dict]:
        """
        Retrieve relevant chunks from the knowledge base based on user query.
        """
        try:
            # Get the appropriate collection
            if collection_type == "topics":
                collection = self._get_topic_collection()
            else:
                collection = self._get_problem_collection()
            
            # If collection doesn't exist yet, return empty results
            if collection is None:
                print(f"Collection '{collection_type}' does not exist yet")
                return []
            
            # Generate embedding for the query
            query_embedding = self.generate_embedding(query)
            
            # Query the vector database
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format the results
            retrieved_chunks = []
            docs = results.get("documents")
            dists = results.get("distances")
            metas = results.get("metadatas")
            if docs and docs[0] is not None and dists and dists[0] is not None and metas and metas[0] is not None:
                for i in range(len(docs[0])):
                    similarity_score = 1 - dists[0][i]  # Convert distance to similarity
                    
                    retrieved_chunks.append({
                        "content": docs[0][i],
                        "metadata": metas[0][i],
                        "similarity_score": round(similarity_score, 4),
                        "is_relevant": similarity_score > 0.7  # Threshold for relevance
                    })
            else:
                print("No results found or results are None.")
            
            return retrieved_chunks
            
        except Exception as e:
            print(f"Error retrieving chunks: {e}")
            raise
    
    def determine_collection_type(self, query: str) -> str:
        """Simple heuristic to determine if the query is about a topic or a problem."""
        query_lower = query.lower()
        
        # Keywords that suggest it's about a coding problem
        problem_keywords = [
            "solve", "problem", "leetcode", "codeforces", "hackerrank",
            "solution", "approach", "algorithm for", "how to code",
            "implement", "write a function", "coding question"
        ]
        
        # Check for problem keywords first
        for keyword in problem_keywords:
            if keyword in query_lower:
                return "problems"
        
        # Default to topics for general questions
        return "topics"
    
    def is_search_successful(self, chunks: List[Dict], similarity_threshold: float = 0.7) -> bool:
        """Determine if the search was successful based on similarity scores."""
        if not chunks:
            return False
        
        # Check if any chunk meets the similarity threshold
        return any(chunk['similarity_score'] >= similarity_threshold for chunk in chunks)

# Create singleton instance
qa_service = QAService()