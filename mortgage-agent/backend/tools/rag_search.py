"""RAG search tool for mortgage knowledge base"""
import os
from dotenv import load_dotenv
import chak


load_dotenv()


async def query_mortgage_rag(question: str) -> str:
    """
    Search mortgage knowledge base for professional information.
    
    This tool queries the RAG system containing authoritative information
    about US mortgage and real estate transactions.
    
    Args:
        question: User's question about mortgage/real estate
        
    Returns:
        Relevant knowledge from the database
    """
    # Simulate RAG search using qwen-plus
    api_key = os.getenv("BAILIAN_API_KEY")
    temp_conv = chak.Conversation(
        "bailian/qwen-plus",
        api_key=api_key
    )
    
    prompt = f"""As a mortgage knowledge base system, provide relevant professional knowledge for this query:

Query: {question}

Return 2-3 concise knowledge base entries in this format:
[Knowledge Entry 1] Title: ...
Content: ...

[Knowledge Entry 2] Title: ...
Content: ...

Keep it professional and concise."""
    
    response = await temp_conv.asend(prompt)
    return f"[RAG Search Results]\n{response.content}"
