# app/services/llm_service.py
from typing import Dict
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from app.core.config import settings
from pydantic import SecretStr

class LLMService:
    def __init__(self):
        self.llm = ChatGroq(
            model=settings.MODEL_NAME,
            api_key=SecretStr(settings.GROQ_API_KEY),
            temperature=0.7,
            max_tokens=1000
        )
    
    from typing import Optional

    def generate_response(self, question: str, context: Optional[str] = None) -> str:
        """
        Generate a response using the LLM, optionally with context from RAG.
        """
        if context:
            # Create a system message with context
            system_message = SystemMessage(
                content=f"""You are an AI programming tutor. Answer the student's question based on the context provided.
                
                Context information:
                {context}
                
                Instructions:
                1. Answer based ONLY on the context provided
                2. If the context doesn't contain the answer, say "I don't have enough information about this specific topic."
                3. Be concise and helpful
                4. If asked for code, provide clean, well-commented examples"""
            )
            
            human_message = HumanMessage(content=question)
            
            response = self.llm.invoke([system_message, human_message])
        else:
            # Fallback without context
            human_message = HumanMessage(content=question)
            response = self.llm.invoke([human_message])
        
        content = response.content
        return content if isinstance(content, str) else str(content)
    
    async def generate_rag_response(self, query: str, context: Optional[str] = None, search_options: Optional[Dict] = None) -> Dict:
        """
        Complete RAG pipeline: search + LLM response generation
        """
        try:
            # Import here to avoid circular imports
            from app.services.qa_service import qa_service
            
            # Step 1: Perform similarity search
            chunks = qa_service.retrieve_relevant_chunks_with_context(
                query=query,
                context=context,
                n_results=search_options.get('n_results', 5) if search_options else 5
            )
            
            # Step 2: Check search success
            similarity_threshold = search_options.get('similarity_threshold', 0.7) if search_options else 0.7
            is_successful = qa_service.is_search_successful(chunks, similarity_threshold)
            
            # Step 3: Generate LLM response
            if chunks:
                context_text = qa_service._format_context_for_llm(chunks)
                llm_response = self.generate_response(query, context_text)
            else:
                # Fallback to general knowledge
                llm_response = self.generate_response(query)
            
            # Step 4: Prepare response
            return {
                "success": True,
                "query": query,
                "response": llm_response,
                "search_metadata": {
                    "chunks_found": len(chunks),
                    "context_quality": "high" if is_successful else "low",
                    "fallback_to_general_knowledge": len(chunks) == 0,
                    "similarity_threshold": similarity_threshold
                },
                "llm_metadata": {
                    "model": self.llm.model_name,
                    "provider": "groq"
                },
                "sources": chunks
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"RAG pipeline failed: {str(e)}",
                "query": query,
                "response": "",
                "search_metadata": {},
                "llm_metadata": {},
                "sources": []
            }
    
    def ask_llm_simple(self, question: str) -> str:
        """Simple LLM query without RAG"""
        return self.generate_response(question)

# Create singleton instance
llm_service = LLMService()