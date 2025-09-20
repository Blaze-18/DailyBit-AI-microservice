# app/services/llm_service.py
import json
from typing import Dict, List
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
            response = self.llm.invoke([human_message], response_format={ "type": "json_object" })
        
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
    
    async def generate_quiz(self, topic: str, difficulty: str = "intermediate", num_questions: int = 5) -> Dict:
        """
        Generate a programming quiz for a specific topic.
        """
        prompt = f"""Generate a {difficulty} level programming quiz about {topic} with {num_questions} questions.

        Requirements:
        1. Each question must be about programming concepts related to {topic}
        2. Provide 4 multiple choice options (A, B, C, D) for each question
        3. Mark the correct answer clearly
        4. Provide a detailed explanation for each correct answer
        5. Return ONLY valid JSON in this exact format:
        {{
            "topic": "{topic}",
            "difficulty": "{difficulty}",
            "questions": [
                {{
                    "question": "question text",
                    "options": ["A. option1", "B. option2", "C. option3", "D. option4"],
                    "correct_answer": "A",
                    "explanation": "detailed explanation"
                }}
            ]
        }}

        Important: Return ONLY the JSON object, no other text.
        """
        
        try:
            response = self.generate_response(prompt)
            
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                quiz_data = json.loads(json_str)
                return {"success": True, "quiz": quiz_data}
            else:
                return {"success": False, "error": "Failed to parse quiz JSON from LLM response"}
                
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"Invalid JSON response: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Quiz generation failed: {str(e)}"}
    
    async def evaluate_quiz_answers(self, questions: List[Dict], user_answers: List[str]) -> Dict:
        """
        Evaluate user's quiz answers and provide explanations.
        """
        if len(user_answers) != len(questions):
            return {"success": False, "error": "Number of answers doesn't match number of questions"}
        
        evaluations = []
        correct_count = 0
        
        for i, (question, user_answer) in enumerate(zip(questions, user_answers)):
            correct_answer = question['correct_answer']
            is_correct = user_answer.strip().upper() == correct_answer.strip().upper()
            
            if is_correct:
                correct_count += 1
            
            evaluations.append({
                "question": question['question'],
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": question['explanation']
            })
        
        score_percentage = (correct_count / len(questions)) * 100
        
        return {
            "success": True,
            "result": {
                "total_questions": len(questions),
                "correct_answers": correct_count,
                "score_percentage": round(score_percentage, 2),
                "evaluations": evaluations
            }
        }

# Create singleton instance
llm_service = LLMService()