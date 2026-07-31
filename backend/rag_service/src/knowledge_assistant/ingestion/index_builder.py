import os
import uuid
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from knowledge_assistant.ingestion.chunker import load_and_chunk_documents
from knowledge_assistant.ingestion.embedder import DocumentEmbedder


def build_index():
    # Load environment variables
    load_dotenv()

    # Construct absolute path to the raw_docs directory
    base_dir = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    raw_docs_dir = os.path.join(base_dir, 'data', 'raw_docs')

    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
    collection_name = os.getenv("QDRANT_COLLECTION_NAME", "pulseiq_knowledge")

    print(f"Loading and chunking documents from {raw_docs_dir}...")
    chunks = load_and_chunk_documents(raw_docs_dir)

    if not chunks:
        print("No documents found to ingest.")
        return

    num_docs = len(set(c.doc_id for c in chunks))
    print(f"Generated {len(chunks)} chunks from {num_docs} documents.")

    print("\nInitializing embedder model (all-MiniLM-L6-v2)...")
    embedder = DocumentEmbedder()
    vector_size = embedder.get_vector_size()

    print("\nEmbedding chunks...")
    texts = [c.content for c in chunks]
    embeddings = embedder.embed_chunks(texts)

    print(f"\nConnecting to Qdrant at {qdrant_host}:{qdrant_port}...")
    client = QdrantClient(host=qdrant_host, port=qdrant_port)

    # Check if collection exists
    collections_response = client.get_collections()
    collection_names = [c.name for c in collections_response.collections]

    if collection_name not in collection_names:
        print(
            f"Creating collection '{collection_name}' with vector size {vector_size}...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size, distance=Distance.COSINE),
        )
    else:
        print(f"Collection '{collection_name}' already exists.")

    print("\nUpserting vectors into Qdrant...")
    points = []

    # Create Qdrant PointStructs for each chunk
    for chunk, vector in zip(chunks, embeddings):
        point_id = str(uuid.uuid4())  # Qdrant requires UUIDs or integers
        points.append(
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "chunk_id": chunk.chunk_id,
                    "doc_id": chunk.doc_id,
                    "title": chunk.title,
                    "content": chunk.content,
                    "source_version": chunk.source_version,
                    "doc_type": chunk.doc_type
                }
            )
        )

    # Upsert in bulk
    client.upsert(
        collection_name=collection_name,
        points=points
    )

    print(
        f"\n✅ Successfully ingested {num_docs} documents into {len(chunks)} chunks!")


if __name__ == "__main__":
    build_index()
