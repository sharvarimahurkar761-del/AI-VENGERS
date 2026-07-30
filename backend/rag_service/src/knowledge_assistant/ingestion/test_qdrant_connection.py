import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

def test_connection():
    # Load environment variables from .env
    load_dotenv()
    
    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
    
    print(f"Connecting to Qdrant at {qdrant_host}:{qdrant_port}...")
    
    try:
        # Initialize the Qdrant client
        client = QdrantClient(host=qdrant_host, port=qdrant_port)
        
        # Get list of existing collections to verify connection
        collections = client.get_collections()
        
        print("\n✅ Successfully connected to Qdrant!")
        print(f"Existing collections: {collections.collections}")
        
    except Exception as e:
        print(f"\n❌ Failed to connect to Qdrant. Error:")
        print(e)
        print("\nPlease ensure the Qdrant Docker container is running and ports are exposed.")

if __name__ == "__main__":
    test_connection()
