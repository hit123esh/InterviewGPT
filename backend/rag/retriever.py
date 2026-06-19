"""
InterviewGPT — RAG Retriever

Performs semantic search over resume embeddings in ChromaDB
to retrieve relevant context for interview question generation.
"""

import logging
from typing import List, Optional
from rag.embeddings import get_chroma_client

logger = logging.getLogger(__name__)


async def retrieve_resume_context(
    user_id: str,
    query: str,
    n_results: int = 5,
    section_filter: Optional[str] = None,
) -> List[dict]:
    """
    Retrieve relevant resume chunks based on a query.
    
    Args:
        user_id: User's UUID string
        query: Search query (e.g., "Tell me about their FastAPI experience")
        n_results: Number of results to return
        section_filter: Optional filter by section (e.g., "projects", "experience")
    
    Returns:
        List of dicts with 'text', 'section', 'score' keys
    """
    try:
        client = get_chroma_client()
        collection_name = f"user_{user_id.replace('-', '_')}"
        
        try:
            collection = client.get_collection(name=collection_name)
        except Exception:
            logger.warning(f"Collection not found for user {user_id}")
            return []

        # Build query params
        where_filter = None
        if section_filter:
            where_filter = {"section": section_filter}

        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter,
        )

        if not results or not results["documents"]:
            return []

        # Format results
        chunks = []
        for i, doc in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][i] if results["metadatas"] else {}
            distance = results["distances"][0][i] if results["distances"] else 0
            chunks.append({
                "text": doc,
                "section": metadata.get("section", "unknown"),
                "score": 1 - distance,  # Convert distance to similarity
                "resume_id": metadata.get("resume_id", ""),
            })

        return chunks

    except Exception as e:
        logger.error(f"Resume retrieval failed: {e}")
        return []


async def get_resume_context_string(
    user_id: str,
    query: str,
    n_results: int = 5,
) -> str:
    """
    Get formatted resume context string for LLM prompt injection.
    """
    chunks = await retrieve_resume_context(user_id, query, n_results)
    
    if not chunks:
        return "No resume context available."

    context_parts = []
    for chunk in chunks:
        section = chunk["section"].replace("_", " ").title()
        context_parts.append(f"[{section}]\n{chunk['text']}")

    return "\n\n---\n\n".join(context_parts)
