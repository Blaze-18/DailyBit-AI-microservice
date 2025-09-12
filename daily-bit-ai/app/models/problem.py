# app/models/problem.py
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Optional, Literal
from enum import Enum
from datetime import datetime

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class ProblemSource(str, Enum):
    LEETCODE = "leetcode"
    CODEFORCES = "codeforces"
    HACKERRANK = "hackerrank"
    CUSTOM = "custom"

class SolutionApproach(BaseModel):
    name: str = Field(..., description="Name of the approach, e.g., 'Two Pointers', 'Dynamic Programming'")
    time_complexity: str = Field(..., description="Time complexity of this approach")
    space_complexity: str = Field(..., description="Space complexity of this approach")
    explanation: str = Field(..., description="Detailed explanation of the approach")
    code: Dict[str, str] = Field(..., description="Code implementations by language")

class TestCase(BaseModel):
    input: str = Field(..., description="Input for the test case")
    output: str = Field(..., description="Expected output")
    explanation: Optional[str] = Field(None, description="Explanation of why this test case is important")

class ProblemMetadata(BaseModel):
    source: ProblemSource
    source_id: Optional[str] = Field(None, description="ID from the source platform, e.g., '1' for Two Sum")
    created_date: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    popularity: Optional[float] = Field(None, description="Popularity score if available")
    acceptance_rate: Optional[float] = Field(None, description="Acceptance rate if available")

class Problem(BaseModel):
    # Core Identification
    id: Optional[str] = Field(None, description="Unique identifier for the problem")
    title: str = Field(..., min_length=1, description="Title of the problem")
    
    # Metadata
    metadata: ProblemMetadata
    difficulty: Difficulty
    topics: List[str] = Field(..., description="Related topics, e.g., ['Array', 'Hash Table']")
    companies: Optional[List[str]] = Field(None, description="Companies that ask this problem")
    
    # Problem Content
    description: str = Field(..., description="Full problem description")
    constraints: List[str] = Field(..., description="Problem constraints")
    examples: List[TestCase] = Field(..., description="Example test cases")
    
    # Solutions
    approaches: List[SolutionApproach] = Field(..., description="Different solution approaches")
    optimal_approach: str = Field(..., description="Name of the optimal approach")
    
    # Hints and Tips
    hints: List[str] = Field(..., description="Progressive hints for stuck students")
    common_mistakes: List[str] = Field(..., description="Common mistakes students make")
    edge_cases: List[str] = Field(..., description="Important edge cases to consider")
    
    # Follow-up
    similar_problems: List[str] = Field(..., description="IDs or titles of similar problems")
    follow_up_questions: Optional[List[str]] = Field(None, description="Follow-up questions to think about")
    
    # Resources
    discussion_links: Optional[List[HttpUrl]] = Field(None, description="Links to helpful discussions")
    video_solutions: Optional[List[HttpUrl]] = Field(None, description="Links to video solutions")