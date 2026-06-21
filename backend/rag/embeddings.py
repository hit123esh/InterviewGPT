"""
InterviewGPT — Resume Embeddings & ChromaDB Indexing

Handles embedding generation and storage in ChromaDB.
"""

import logging
from typing import Optional
import chromadb
from backend.config import get_settings
from backend.rag.chunking import chunk_resume_text

logger = logging.getLogger(__name__)
settings = get_settings()

_chroma_client: Optional[chromadb.ClientAPI] = None


def get_chroma_client() -> chromadb.ClientAPI:
    """Get or create ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        try:
            _chroma_client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
            )
        except Exception:
            logger.warning("ChromaDB HTTP client failed, using persistent client")
            _chroma_client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR
            )
    return _chroma_client


async def index_resume(resume) -> str:
    """
    Index a resume's text into ChromaDB.
    Creates a collection per user and adds resume chunks.
    """
    if not resume.raw_text:
        return ""

    client = get_chroma_client()
    collection_name = f"user_{str(resume.user_id).replace('-', '_')}"

    # Get or create collection
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    # Chunk the resume text
    chunks = chunk_resume_text(resume.raw_text)

    if not chunks:
        return collection_name

    # Prepare data for ChromaDB
    ids = [f"{resume.id}_{chunk['index']}" for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [
        {
            "resume_id": str(resume.id),
            "chunk_index": chunk["index"],
            "section": chunk["section_hint"],
        }
        for chunk in chunks
    ]

    # Upsert chunks (ChromaDB handles embedding via its default model)
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    logger.info(f"Indexed {len(chunks)} chunks for resume {resume.id}")
    return collection_name


async def delete_resume_embeddings(user_id: str, resume_id: str):
    """Remove resume embeddings from ChromaDB."""
    try:
        client = get_chroma_client()
        collection_name = f"user_{user_id.replace('-', '_')}"
        collection = client.get_collection(name=collection_name)
        
        # Delete by resume_id metadata filter
        collection.delete(
            where={"resume_id": resume_id}
        )
    except Exception as e:
        logger.warning(f"Failed to delete embeddings: {e}")
