from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import traceback

from knowledge_assistant.retrieval.retriever import retrieve
from knowledge_assistant.generation.generator import generate_response

app = FastAPI(title="PulseIQ Knowledge Assistant API")

class KnowledgeRequest(BaseModel):
    user_id: str
    issue_text: str

class RetrievedDoc(BaseModel):
    doc_id: str
    title: str
    snippet: str
    relevance: float

class KnowledgeResponse(BaseModel):
    retrieved_docs: List[RetrievedDoc]
    grounded_response: str
    confidence: float
    model_version: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/knowledge/respond", response_model=KnowledgeResponse)
def respond_to_issue(request: KnowledgeRequest):
    try:
        # 1. Retrieve relevant chunks
        chunks = retrieve(request.issue_text, top_k=3)
        
        # Format the retrieved docs for the response
        retrieved_docs = []
        for chunk in chunks:
            content = chunk.get("content", "")
            # Truncate to first ~200 chars and clean newlines for the snippet
            clean_content = content.replace('\n', ' ').strip()
            snippet = clean_content[:200] + "..." if len(clean_content) > 200 else clean_content
            
            retrieved_docs.append(RetrievedDoc(
                doc_id=chunk.get("doc_id", "unknown"),
                title=chunk.get("title", "Untitled"),
                snippet=snippet,
                relevance=chunk.get("score", 0.0)
            ))
            
        # 2. Generate grounded response
        gen_result = generate_response(request.issue_text, chunks)
        
        # 3. Construct and return final response
        return KnowledgeResponse(
            retrieved_docs=retrieved_docs,
            grounded_response=gen_result.get("response_text", ""),
            confidence=gen_result.get("confidence_score", 0.0),
            model_version="llama-3.3-70b-versatile"
        )
        
    except Exception as e:
        error_msg = f"Failed to process knowledge request: {str(e)}"
        print(f"ERROR: {error_msg}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)
