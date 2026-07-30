import os
import re
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

class Generator:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set. Please set it in your .env file.")
        
        # Point the OpenAI client to Groq's base URL
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = "llama-3.3-70b-versatile"
        
    def generate_response(self, query: str, retrieved_chunks: List[Dict[str, Any]], confidence_threshold: float = 0.4) -> Dict[str, Any]:
        # 1. PRE-GENERATION CHECK
        # If we have no chunks, or the top chunk is below our relevance threshold, skip the LLM.
        top_score = retrieved_chunks[0].get("score", 0.0) if retrieved_chunks else 0.0
        
        if top_score < confidence_threshold:
            return {
                "response_text": "I don't have enough information to answer this confidently. This has been flagged for a human support agent to review.",
                "cited_doc_ids": [],
                "confidence_score": round(top_score, 2)
            }
        
        # 2. Format the retrieved context
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            doc_id = chunk.get("doc_id", f"doc_{i}")
            title = chunk.get("title", "Untitled")
            content = chunk.get("content", "")
            context_parts.append(f"--- Document ID: {doc_id} | Title: {title} ---\n{content}\n")
            
        context_str = "\n".join(context_parts)
        
        # 3. Build the strict system prompt
        system_prompt = (
            "You are a helpful knowledge assistant for PulseIQ. Your task is to answer the user's question based ONLY on the provided context.\n\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. You must ONLY use the information from the provided context. Do not use outside or general knowledge.\n"
            "2. If the context does not contain enough information to answer the question, say so explicitly (e.g. 'I do not have enough information to answer that.') instead of guessing or making things up.\n"
            "3. Cite the document(s) you used for each part of your answer by referencing the Title or Document ID inside brackets. (e.g. 'According to [FAQ: How to Reset Your Password]...')\n"
        )
        
        user_message = f"Context Information:\n\n{context_str}\n\nUser Question: {query}"
        
        # 4. Call the LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.0 # Low temperature for factual grounding
        )
        
        response_text = response.choices[0].message.content
        
        # 5. Extract citations and validate them
        cited_doc_ids = set()
        has_fabrication = False
        
        # Find explicit bracketed citations like [Document Title], [doc_id], or [doc_id | Title]
        bracket_citations = re.findall(r'\[(.*?)\]', response_text)
        
        for citation in bracket_citations:
            citation_matched = False
            # Split citation by common separators to handle formats like [doc_id | Title]
            parts = [p.strip() for p in citation.split('|')]
            
            for chunk in retrieved_chunks:
                doc_id = chunk.get("doc_id", "")
                title = chunk.get("title", "")
                
                if doc_id in parts or title in parts:
                    cited_doc_ids.add(doc_id)
                    citation_matched = True
                    break
            
            # Post-generation check: if citation wasn't found in context
            if not citation_matched:
                print(f"WARNING: Citation validation failed. LLM fabricated citation: [{citation}]")
                has_fabrication = True
                
        # Substring fallback for valid chunks
        for chunk in retrieved_chunks:
            doc_id = chunk.get("doc_id", "")
            title = chunk.get("title", "")
            if (doc_id and doc_id in response_text) or (title and title in response_text):
                cited_doc_ids.add(doc_id)
                
        cited_doc_ids = list(cited_doc_ids)
        
        # 6. Gradient confidence score heuristic
        response_lower = response_text.lower()
        is_hedged = "do not have enough information" in response_lower or "does not contain enough information" in response_lower
        
        # Calculate citation density (0.0 to 1.0)
        density = min(1.0, len(cited_doc_ids) / max(1, len(retrieved_chunks)))
        
        if has_fabrication:
            # Band: 0.0 - 0.1 (Hallucination/Fabricated citation)
            confidence = 0.05
        elif is_hedged:
            if len(cited_doc_ids) > 0:
                # Band: 0.55 - 0.75 (Partially answered / Workaround offered)
                confidence = 0.55 + (density * 0.20)
            else:
                # Band: 0.15 - 0.35 (No relevant content, explicitly cannot help)
                confidence = 0.25
        else:
            # Band: 0.85 - 1.0 (Fully answered, no hedging)
            confidence = 0.85 + (density * 0.15)

        return {
            "response_text": response_text,
            "cited_doc_ids": cited_doc_ids,
            "confidence_score": round(confidence, 2)
        }

def generate_response(query: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    gen = Generator()
    return gen.generate_response(query, retrieved_chunks)
