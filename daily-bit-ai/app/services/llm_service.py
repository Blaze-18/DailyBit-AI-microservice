from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
from app.core.config import settings
from pydantic import SecretStr

llm = ChatGroq(
    model=settings.MODEL_NAME,
    api_key=SecretStr(settings.GROQ_API_KEY),
    temperature=0.7,
    max_tokens=1000
)


def ask_llm(question: str) -> str:
    """Send a question to Groq LLM and return response text."""
    message = HumanMessage(content=question)
    response = llm.invoke([message])
    content = response.content
    if isinstance(content, str):
        return content
    return str(content)
