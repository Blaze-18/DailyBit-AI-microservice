# app/models/topic.py
from pydantic import BaseModel
from typing import List, Dict, Optional

class CodeSnippet(BaseModel):
    code: str
    description: str

class CodeExamples(BaseModel):
    java: Optional[CodeSnippet] = None
    python: Optional[CodeSnippet] = None
    javascript: Optional[CodeSnippet] = None

class TopicMetadata(BaseModel):
    prerequisites: List[str] = []
    category: str
    difficulty: str

class TopicJSON(BaseModel):
    title: str
    metadata: TopicMetadata
    concept: str
    key_properties: List[str]
    code: Optional[CodeExamples] = None
    complexity: Optional[Dict[str, str]] = None