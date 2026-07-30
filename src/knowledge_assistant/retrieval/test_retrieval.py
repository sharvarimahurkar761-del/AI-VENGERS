import sys
from knowledge_assistant.retrieval.retriever import retrieve

def main():
    # If the user passed a query, use that instead
    if len(sys.argv) > 1:
        queries = [" ".join(sys.argv[1:])]
    else:
        # Default test queries provided by the user
        queries = [
            "How do I get my data out of the platform?",
            "I forgot my password and can't log in",
            "What does the integrations feature do?"
        ]
        
    print("Loading model and connecting to Qdrant...")
    print("(This might take a couple of seconds on the first run)\n")
        
    for query in queries:
        print(f"{'='*60}")
        print(f"QUERY: \"{query}\"")
        print(f"{'='*60}")
        
        # Retrieve top 2 results for manual sanity checking
        results = retrieve(query, top_k=2)
        
        for i, res in enumerate(results, 1):
            title = res['title']
            score = res['score']
            doc_type = res['doc_type']
            content = res['content']
            
            # Create a short snippet replacing newlines with spaces for a cleaner output
            clean_content = content.replace('\n', ' ').strip()
            snippet = clean_content[:150] + "..." if len(clean_content) > 150 else clean_content
            
            print(f"Result {i}:")
            print(f"  Title:    {title}")
            print(f"  Type:     {doc_type}")
            print(f"  Score:    {score:.4f}")
            print(f"  Snippet:  {snippet}")
            print("-" * 40)
        print("\n")

if __name__ == "__main__":
    main()
