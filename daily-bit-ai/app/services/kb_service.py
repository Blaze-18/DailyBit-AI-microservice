# app/services/kb_service.py
from typing import Dict, List
import uuid
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from app.core.config import settings 
from app.models.topic import TopicJSON 


# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
collection = chroma_client.get_or_create_collection(
    name="topics",
    metadata={"hnsw:space": "cosine"}
)

class KnowledgeBaseService:
    
    @staticmethod
    def generate_embedding(text: str) -> List[float]:
        """Generates an embedding vector for a given text using OpenAI."""
        try:
            model = SentenceTransformer(settings.EMBEDDING_MODEL)
            embedding = model.encode(text).tolist()
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

    @staticmethod
    def create_chunks_from_topic(topic_data: TopicJSON) -> List[Dict]:
        """Breaks down the topic JSON into logical chunks for embedding."""
        chunks = []
        base_metadata = {
            "topic": topic_data.title,
            "category": topic_data.metadata.category,
            "difficulty": topic_data.metadata.difficulty,
            "prerequisites": ",".join(topic_data.metadata.prerequisites)
        }

        # Chunk 1: Concept and Key Properties
        chunk1_text = f"Topic: {topic_data.title}\nType: Concept\n\nConcept: {topic_data.concept}\n\nKey Properties:\n" + "\n".join([f"- {prop}" for prop in topic_data.key_properties])
        chunks.append({
            "id": str(uuid.uuid4()),
            "text": chunk1_text,
            "metadata": {**base_metadata, **{"chunk_type": "concept"}}
        })

        # Chunk 2: Code Examples
        if topic_data.code and topic_data.code.python:
            chunk2_text = f"Topic: {topic_data.title}\nType: Code Example\nLanguage: Python\n\nDescription: {topic_data.code.python.description}\n\nCode:\n{topic_data.code.python.code}"
            chunks.append({
                "id": str(uuid.uuid4()),
                "text": chunk2_text,
                "metadata": {**base_metadata, **{"chunk_type": "code", "language": "python"}}
            })

        # Chunk 3: Complexity
        if topic_data.complexity:
            comp_text = f"Topic: {topic_data.title}\nType: Complexity Analysis\n\n"
            for op, comp in topic_data.complexity.items():
                comp_text += f"{op}: {comp}\n"
            chunks.append({
                "id": str(uuid.uuid4()),
                "text": comp_text,
                "metadata": {**base_metadata, **{"chunk_type": "complexity"}}
            })
        return chunks

    def ingest_topic(self, topic_data: TopicJSON):
        """
        Main method to ingest a topic: chunk, embed, and store.
        """
        # 1. Chunk the incoming JSON data
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