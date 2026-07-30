import sys
from knowledge_assistant.retrieval.retriever import retrieve
from knowledge_assistant.generation.generator import generate_response

def test_pipeline(query: str):
    print(f"\n{'='*80}")
    print(f"QUERY: \"{query}\"")
    print(f"{'='*80}")
    
    print("1. Retrieving context from Qdrant...")
    chunks = retrieve(query, top_k=3)
    
    print(f"   Retrieved {len(chunks)} chunks.")
    for i, chunk in enumerate(chunks, 1):
        print(f"   - {chunk['title']} (Score: {chunk['score']:.2f})")
        
    print("\n2. Generating response via Groq (llama-3.3-70b-versatile)...")
    try:
        result = generate_response(query, chunks)
        
        print("\n--- LLM RESPONSE ---")
        print(result["response_text"])
        print("--------------------")
        
        print(f"\nCited Documents: {result['cited_doc_ids']}")
        print(f"Rough Confidence Score: {result['confidence_score']:.2f}")
    except Exception as e:
        print(f"Generation failed: {e}")

def main():
    queries = [
        "I forgot my password and can't log in",
        "Can I integrate this with Salesforce specifically?"
    ]
    
    for q in queries:
        test_pipeline(q)

if __name__ == "__main__":
    main()
