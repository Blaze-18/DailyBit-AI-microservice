# app/models/topic.py
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Optional, Literal
from enum import Enum
from datetime import datetime

# --- Enums for Controlled Vocabulary ---
class Difficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class Category(str, Enum):
    DATA_STRUCTURE = "data_structure"
    ALGORITHM = "algorithm"
    PROGRAMMING_CONCEPT = "programming_concept"
    SYSTEM_DESIGN = "system_design"
    DATABASE = "database"

class ComplexityClass(str, Enum):
    CONSTANT = "O(1)"
    LOGARITHMIC = "O(log n)"
    LINEAR = "O(n)"
    LINEARITHMIC = "O(n log n)"
    QUADRATIC = "O(n²)"
    CUBIC = "O(n³)"
    EXPONENTIAL = "O(2^n)"
    FACTORIAL = "O(n!)"

# --- Sub-Models ---
class CodeExample(BaseModel):
    code: str = Field(..., description="The code snippet itself")
    language: str = Field(..., description="Programming language, e.g., python, javascript, java, cpp")
    description: str = Field(..., description="Explanation of what the code does")
    # Optional field for complexity specific to this implementation
    complexity: Optional[Dict[str, ComplexityClass]] = None

class ComplexityAnalysis(BaseModel):
    time: Dict[str, ComplexityClass] = Field(..., description="Time complexity for various operations")
    space: ComplexityClass = Field(..., description="Worst-case auxiliary space complexity")
    best_case: Optional[Dict[str, ComplexityClass]] = None
    average_case: Optional[Dict[str, ComplexityClass]] = None
    worst_case: Optional[Dict[str, ComplexityClass]] = None
    notes: Optional[str] = Field(None, description="Additional notes on complexity")

class VisualAid(BaseModel):
    type: Literal["image", "diagram", "animation", "graph"]
    # Can be a URL to an image or a base64-encoded string for simplicity
    url: Optional[HttpUrl] = None
    base64_data: Optional[str] = Field(None, description="Base64 encoded image data")
    caption: str = Field(..., description="Caption explaining the visual")

class ProblemPattern(BaseModel):
    name: str = Field(..., description="Name of the pattern, e.g., 'Two Pointers', 'Sliding Window'")
    description: str = Field(..., description="How this topic relates to the pattern")
    example_problems: List[str] = Field(..., description="List of example problem titles or LeetCode IDs")

# --- Main Topic Model ---
class TopicMetadata(BaseModel):
    version: str = Field("2.0", description="Version of the topic schema")
    authors: Optional[List[str]] = None
    created_date: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    review_status: Literal["draft", "reviewed", "approved"] = "draft"

class Topic(BaseModel):
    # Core Identification
    id: Optional[str] = Field(None, description="Unique identifier for the topic")
    title: str = Field(..., min_length=1, description="Name of the topic, e.g., 'Linked List', 'QuickSort'")
    nickname: Optional[str] = Field(None, description="Common nickname, e.g., 'DFS', 'BFS'")

    # Categorization & Metadata
    metadata: TopicMetadata
    category: Category
    difficulty: Difficulty
    prerequisites: List[str] = Field(..., description="List of topic IDs or names that are prerequisites")
    related_topics: List[str] = Field(..., description="List of closely related topic IDs or names")

    # Core Content
    definition: str = Field(..., description="Formal, concise definition")
    key_ideas: List[str] = Field(..., description="Bulleted list of the most important concepts")
    detailed_explanation: str = Field(..., description="In-depth walkthrough of how it works")
    algorithm_steps: Optional[List[str]] = Field(None, description="Step-by-step instructions for algorithms")

    # Visuals and Examples
    visual_aids: Optional[List[VisualAid]] = None
    code_examples: List[CodeExample] = Field(..., description="Code examples in multiple languages")
    complexity: ComplexityAnalysis

    # Practical Applications
    use_cases: List[str] = Field(..., description="Real-world applications")
    advantages: List[str] = Field(..., description="Strengths compared to alternatives")
    disadvantages: List[str] = Field(..., description="Weaknesses and limitations")
    common_mistakes: List[str] = Field(..., description="Common pitfalls and how to avoid them")

    # Problem-Solving Context
    problem_patterns: List[ProblemPattern] = Field(..., description="How this topic appears in coding problems")
    example_problems: List[str] = Field(..., description="List of classic problem names/IDs for practice")

    # Optional Advanced Content
    variations: Optional[List[str]] = Field(None, description="List of common variations, e.g., 'Doubly Linked List'")
    implementation_notes: Optional[str] = Field(None, description="Notes on edge cases and optimizations")
    resources: Optional[List[HttpUrl]] = Field(None, description="Links to external articles, videos, etc.")