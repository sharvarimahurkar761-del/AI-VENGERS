import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from qdrant_client import QdrantClient

from knowledge_assistant.ingestion.embedder import DocumentEmbedder

# Global instances for lazy loading so we don't reload the model on every query
_embedder = None
_qdrant_client = None


def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = DocumentEmbedder()
    return _embedder


def get_qdrant_client():
    global _qdrant_client
    if _qdrant_client is None:
        load_dotenv()
        host = os.getenv("QDRANT_HOST", "localhost")
        port = int(os.getenv("QDRANT_PORT", 6333))
        _qdrant_client = QdrantClient(host=host, port=port)
    return _qdrant_client


def retrieve(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Embeds the query and retrieves the top_k most relevant chunks from Qdrant.
    """
    load_dotenv()
    collection_name = os.getenv("QDRANT_COLLECTION_NAME", "pulseiq_knowledge")

    embedder = get_embedder()
    client = get_qdrant_client()

    # 1. Embed the query
    # The DocumentEmbedder takes a list and returns a list of embeddings.
    # We pass a single query and take the first vector.
    query_vector = embedder.embed_chunks([query])[0]

    # 2. Search Qdrant
    search_response = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=top_k
    )

    # 3. Format results
    results = []
    for scored_point in search_response.points:
        payload = scored_point.payload
        # Qdrant's cosine distance returns cosine similarity in the range [-1, 1].
        # We normalize this to [0.0, 1.0] for easier consumption by the generation layer.
        normalized_score = max(0.0, (scored_point.score + 1.0) / 2.0)

        results.append({
            "doc_id": payload.get("doc_id", "Unknown"),
            "title": payload.get("title", "Untitled"),
            "content": payload.get("content", ""),
            "doc_type": payload.get("doc_type", "Unknown"),
            "source_version": payload.get("source_version", "Unknown"),
            "score": normalized_score
        })

    return results
