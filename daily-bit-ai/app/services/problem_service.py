# app/services/problem_service.py
from typing import Dict, List, Optional
import uuid
import chromadb
from chromadb.config import Settings
from chromadb.errors import NotFoundError
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.models.problem import Problem, Difficulty, ProblemSource

# Initialize ChromaDB client for problems (separate collection)
chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
try:
    problem_collection = chroma_client.get_collection("problems")
except NotFoundError:
    # Create the collection if it doesn't exist
    problem_collection = chroma_client.create_collection(
        name="problems",
        metadata={"hnsw:space": "cosine"}
    )

# Initialize embedding model
embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)

class ProblemService:
    
    @staticmethod
    def generate_embedding(text: str) -> List[float]:
        """Generates an embedding vector for a given text."""
        try:
            embedding = embedding_model.encode(text).tolist()
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

    @staticmethod
    def create_chunks_from_problem(problem_data: Problem) -> List[Dict]:
        """Breaks down the problem into logical chunks for embedding."""
        chunks = []
        base_metadata = {
            "problem_id": problem_data.id or str(uuid.uuid4()),
            "title": problem_data.title,
            "difficulty": problem_data.difficulty.value,
            "source": problem_data.metadata.source.value,
            "topics": ",".join(problem_data.topics),
            "optimal_approach": problem_data.optimal_approach
        }

        # Chunk 1: Problem Description and Constraints
        desc_text = f"""
        Problem: {problem_data.title}
        Difficulty: {problem_data.difficulty.value}
        Source: {problem_data.metadata.source.value}
        
        Description:
        {problem_data.description}
        
        Constraints:
        {chr(10).join([f"- {constraint}" for constraint in problem_data.constraints])}
        """
        chunks.append({
            "id": f"{base_metadata['problem_id']}_description",
            "text": desc_text.strip(),
            "metadata": {**base_metadata, **{"chunk_type": "problem_description"}}
        })

        # Chunk 2: Examples
        examples_text = f"""
        Problem: {problem_data.title}
        Type: Examples
        
        Examples:
        """
        for i, example in enumerate(problem_data.examples, 1):
            examples_text += f"""
        Example {i}:
        Input: {example.input}
        Output: {example.output}
        {f'Explanation: {example.explanation}' if example.explanation else ''}
        """
        chunks.append({
            "id": f"{base_metadata['problem_id']}_examples",
            "text": examples_text.strip(),
            "metadata": {**base_metadata, **{"chunk_type": "examples"}}
        })

        # Chunk 3: Solution Approaches (one chunk per approach)
        for i, approach in enumerate(problem_data.approaches):
            approach_text = f"""
            Problem: {problem_data.title}
            Approach: {approach.name}
            Time Complexity: {approach.time_complexity}
            Space Complexity: {approach.space_complexity}
            
            Explanation:
            {approach.explanation}
            """
            
            # Add code snippets if available
            if approach.code:
                approach_text += "\n\nCode Implementations:\n"
                for lang, code in approach.code.items():
                    approach_text += f"\n{lang}:\n{code}\n"
            
            chunks.append({
                "id": f"{base_metadata['problem_id']}_approach_{i}",
                "text": approach_text.strip(),
                "metadata": {
                    **base_metadata, 
                    **{
                        "chunk_type": "solution_approach",
                        "approach_name": approach.name,
                        "time_complexity": approach.time_complexity,
                        "space_complexity": approach.space_complexity,
                        "is_optimal": approach.name == problem_data.optimal_approach
                    }
                }
            })

        # Chunk 4: Hints and Common Mistakes
        hints_text = f"""
        Problem: {problem_data.title}
        Type: Hints and Guidance
        
        Hints:
        {chr(10).join([f"{i+1}. {hint}" for i, hint in enumerate(problem_data.hints)])}
        
        Common Mistakes:
        {chr(10).join([f"- {mistake}" for mistake in problem_data.common_mistakes])}
        
        Edge Cases:
        {chr(10).join([f"- {edge_case}" for edge_case in problem_data.edge_cases])}
        """
        chunks.append({
            "id": f"{base_metadata['problem_id']}_hints",
            "text": hints_text.strip(),
            "metadata": {**base_metadata, **{"chunk_type": "hints_guidance"}}
        })

        return chunks

    def ingest_problem(self, problem_data: Problem):
        """
        Main method to ingest a problem: chunk, embed, and store.
        """
        # 1. Chunk the problem data
        chunks = self.create_chunks_from_problem(problem_data)
        print(f"Created {len(chunks)} chunks for problem '{problem_data.title}'")

        # 2. Prepare data for ChromaDB
        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for chunk in chunks:
            # 3. Generate embedding for each chunk's text
            embedding = self.generate_embedding(chunk["text"])
            
            ids.append(chunk["id"])
            embeddings.append(embedding)
            documents.append(chunk["text"])
            metadatas.append(chunk["metadata"])

        # 4. Upsert the batch into ChromaDB
        problem_collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        return len(chunks)

    def search_similar_problems(self, query: str, n_results: int = 3, filters: 'Optional[Dict]' = None):
        """Search for problems similar to the query."""
        query_embedding = self.generate_embedding(query)
        
        results = problem_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filters
        )
        return results

# Create a singleton instance to be imported
problem_service = ProblemService()