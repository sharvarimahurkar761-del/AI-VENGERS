from sentence_transformers import SentenceTransformer
from typing import List

class DocumentEmbedder:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initializes the sentence transformer model.
        all-MiniLM-L6-v2 is lightweight and maps sentences & paragraphs to a 384 dimensional dense vector space.
        """
        self.model = SentenceTransformer(model_name)
        
    def embed_chunks(self, texts: List[str]) -> List[List[float]]:
        """
        Takes a list of string chunks and returns their vector embeddings.
        """
        # Returns a list of vectors (float arrays)
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings.tolist()
        
    def get_vector_size(self) -> int:
        """
        Returns the embedding dimension for the loaded model.
        """
        return self.model.get_sentence_embedding_dimension()
