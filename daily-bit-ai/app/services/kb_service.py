# app/services/kb_service.py
from typing import Dict, List
import uuid
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.models.topic import Topic, Category, Difficulty  # Import the NEW models

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
collection = chroma_client.get_or_create_collection(
    name="topics",
    metadata={"hnsw:space": "cosine"}
)

# Initialize embedding model
embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)

class KnowledgeBaseService:
    
    @staticmethod
    def generate_embedding(text: str) -> List[float]:
        """Generates an embedding vector for a given text using SentenceTransformers."""
        try:
            embedding = embedding_model.encode(text).tolist()
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

    @staticmethod
    def create_chunks_from_topic(topic_data: Topic) -> List[Dict]:
        """Breaks down the advanced topic into logical chunks for embedding."""
        chunks = []
        base_metadata = {
            "topic": topic_data.title,
            "topic_id": topic_data.id or str(uuid.uuid4()),
            "category": topic_data.category.value,
            "difficulty": topic_data.difficulty.value,
            "prerequisites": ",".join(topic_data.prerequisites),
            "related_topics": ",".join(topic_data.related_topics)
        }

        # Chunk 1: Core Definition and Key Ideas
        chunk1_text = f"""
        Topic: {topic_data.title}
        Type: Core Concept
        
        Definition: {topic_data.definition}
        
        Key Ideas:
        {chr(10).join([f"- {idea}" for idea in topic_data.key_ideas])}
        """
        chunks.append({
            "id": f"{base_metadata['topic_id']}_core",
            "text": chunk1_text.strip(),
            "metadata": {**base_metadata, **{"chunk_type": "core_concept"}}
        })

        # Chunk 2: Detailed Explanation
        if topic_data.detailed_explanation:
            chunk2_text = f"""
            Topic: {topic_data.title}
            Type: Detailed Explanation
            
            {topic_data.detailed_explanation}
            """
            chunks.append({
                "id": f"{base_metadata['topic_id']}_explanation",
                "text": chunk2_text.strip(),
                "metadata": {**base_metadata, **{"chunk_type": "detailed_explanation"}}
            })

        # Chunk 3: Algorithm Steps (if applicable)
        if topic_data.algorithm_steps:
            chunk3_text = f"""
            Topic: {topic_data.title}
            Type: Algorithm Steps
            
            Step-by-Step Process:
            {chr(10).join([f"{i+1}. {step}" for i, step in enumerate(topic_data.algorithm_steps)])}
            """
            chunks.append({
                "id": f"{base_metadata['topic_id']}_steps",
                "text": chunk3_text.strip(),
                "metadata": {**base_metadata, **{"chunk_type": "algorithm_steps"}}
            })

        # Chunk 4: Complexity Analysis
        complexity_text = f"""
        Topic: {topic_data.title}
        Type: Complexity Analysis
        
        Time Complexity:
        {chr(10).join([f"- {op}: {comp}" for op, comp in topic_data.complexity.time.items()])}
        
        Space Complexity: {topic_data.complexity.space.value}
        """
        if topic_data.complexity.notes:
            complexity_text += f"\n\nNotes: {topic_data.complexity.notes}"
        
        chunks.append({
            "id": f"{base_metadata['topic_id']}_complexity",
            "text": complexity_text.strip(),
            "metadata": {**base_metadata, **{"chunk_type": "complexity"}}
        })

        # Chunk 5: Code Examples (one chunk per language)
        for i, code_example in enumerate(topic_data.code_examples):
            chunk_code_text = f"""
            Topic: {topic_data.title}
            Type: Code Example
            Language: {code_example.language}
            
            Description: {code_example.description}
            
            Code:
            {code_example.code}
            """
            chunks.append({
                "id": f"{base_metadata['topic_id']}_code_{code_example.language}_{i}",
                "text": chunk_code_text.strip(),
                "metadata": {
                    **base_metadata, 
                    **{
                        "chunk_type": "code_example",
                        "language": code_example.language,
                        "example_index": str(i)
                    }
                }
            })

        # Chunk 6: Practical Applications
        applications_text = f"""
        Topic: {topic_data.title}
        Type: Practical Applications
        
        Use Cases:
        {chr(10).join([f"- {use_case}" for use_case in topic_data.use_cases])}
        
        Advantages:
        {chr(10).join([f"- {adv}" for adv in topic_data.advantages])}
        
        Disadvantages:
        {chr(10).join([f"- {disadv}" for disadv in topic_data.disadvantages])}
        """
        chunks.append({
            "id": f"{base_metadata['topic_id']}_applications",
            "text": applications_text.strip(),
            "metadata": {**base_metadata, **{"chunk_type": "practical_applications"}}
        })

        # Chunk 7: Problem Patterns
        if topic_data.problem_patterns:
            patterns_text = f"""
            Topic: {topic_data.title}
            Type: Problem Patterns
            
            """
            for pattern in topic_data.problem_patterns:
                patterns_text += f"""
            Pattern: {pattern.name}
            Description: {pattern.description}
            Example Problems: {", ".join(pattern.example_problems)}
            
            """
            
            chunks.append({
                "id": f"{base_metadata['topic_id']}_patterns",
                "text": patterns_text.strip(),
                "metadata": {**base_metadata, **{"chunk_type": "problem_patterns"}}
            })

        # Chunk 8: Common Mistakes and Implementation Notes
        mistakes_notes_text = f"""
        Topic: {topic_data.title}
        Type: Implementation Guide
        
        Common Mistakes:
        {chr(10).join([f"- {mistake}" for mistake in topic_data.common_mistakes])}
        """
        
        if topic_data.implementation_notes:
            mistakes_notes_text += f"""
            
        Implementation Notes:
        {topic_data.implementation_notes}
        """
        
        chunks.append({
            "id": f"{base_metadata['topic_id']}_implementation",
            "text": mistakes_notes_text.strip(),
            "metadata": {**base_metadata, **{"chunk_type": "implementation_guide"}}
        })

        return chunks

    def ingest_topic(self, topic_data: Topic):
        """
        Main method to ingest a topic: chunk, embed, and store.
        """
        # 1. Chunk the incoming topic data
        chunks = self.create_chunks_from_topic(topic_data)
        print(f"Created {len(chunks)} chunks for topic '{topic_data.title}'")

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
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        return len(chunks)

# Create a singleton instance to be imported
kb_service = KnowledgeBaseService()