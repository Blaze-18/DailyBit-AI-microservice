# Daily Bit AI 🚀

An intelligent AI-powered programming tutor and coding assistant built with FastAPI. Provides contextual help for programming topics and coding problems using RAG (Retrieval-Augmented Generation) technology.

## 🌟 Features

- **Smart Topic Assistance**: Get detailed explanations on programming topics (Algorithms, Data Structures, etc.)
- **Coding Problem Help**: Step-by-step guidance for LeetCode-style problems
- **Context-Aware Responses**: AI understands whether you're asking about a topic or specific problem
- **Multi-Language Support**: Code examples in Python, Java, and JavaScript
- **Knowledge Base**: Built-in repository of programming concepts and solutions
- **RAG Architecture**: Combines vector search with LLM generation for accurate responses

## 🏗️ Architecture
Frontend → FastAPI → RAG Pipeline → ChromaDB → Groq LLM
│ │
├─ Topic KB ──┐
└─ Problem KB ┘


## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Groq API account ([sign up here](https://console.groq.com/))
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd daily-bit-ai
   ```
2. **Set up virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  
    # On Windows: venv\Scripts\activate
    ```
3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```
4. **Environment configuration**
    ```bash
    cp .env.example .env
    ```
5.  **Create .env file with your credentials**
    ```bash
    GROQ_API_KEY=your_groq_api_key_here
    EMBEDDING_MODEL=all-MiniLM-L6-v2
    MODEL_NAME=
    CHROMA_DB_PATH=openai/gpt-oss-120b
    ```
6. **Run the application**
    ```bash
    python run.py
    ```
7. **Access the API**
    - API: http://localhost:8000
    - Docs: http://localhost:8000/docs
    - Redoc: http://localhost:8000/redoc

## 🗂️ Project Structure
```text
daily-bit-ai/
├── app/
│   ├── core/
│   │   └── config.py          # Configuration settings
│   ├── models/
│   │   ├── topic.py           # Topic Pydantic models
│   │   ├── problem.py         # Problem Pydantic models
│   │   └── qa.py             # QA request/response models
│   ├── routes/
│   │   ├── qa.py             # Main query endpoints
│   │   ├── topic_route.py    # Topic management
│   │   ├── problem_route.py  # Problem management
│   │   └── __init__.py       # Router organization
│   ├── services/
│   │   ├── llm_service.py    # Groq LLM integration
│   │   ├── qa_service.py     # RAG pipeline logic
│   │   ├── kb_service.py     # Knowledge base service
│   │   └── problem_service.py # Problem-specific logic
│   └── main.py               # FastAPI application setup
├── chroma_db/                # Vector database storage
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
└── README.md                # This file
```