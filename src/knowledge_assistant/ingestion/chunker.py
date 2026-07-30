import os
import glob
from dataclasses import dataclass
from typing import List
import re
import datetime

@dataclass
class DocumentChunk:
    chunk_id: str
    doc_id: str
    title: str
    content: str
    source_version: str
    doc_type: str

def infer_doc_type(filename: str) -> str:
    filename_lower = filename.lower()
    if filename_lower.startswith('faq'):
        return "faq"
    elif filename_lower.startswith('doc'):
        return "product_doc"
    elif filename_lower.startswith('support'):
        return "resolution_log"
    return "unknown"

def split_text(text: str, max_chars: int = 2000, overlap_chars: int = 300) -> List[str]:
    """
    Splits text into chunks of roughly max_chars, with an overlap.
    Prefers splitting on paragraphs, then sentences.
    """
    # Split by paragraphs first (double newline)
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    current_chunk = ""
    
    for p in paragraphs:
        if len(current_chunk) + len(p) < max_chars:
            current_chunk += p + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # Handle case where a single paragraph is larger than max_chars
            if len(p) > max_chars:
                # Split by sentences
                sentences = re.split(r'(?<=[.!?]) +', p)
                current_chunk = ""
                for s in sentences:
                    if len(current_chunk) + len(s) < max_chars:
                        current_chunk += s + " "
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = s + " "
            else:
                # Start a new chunk with overlap from the previous one
                overlap_text = chunks[-1][-overlap_chars:] if chunks else ""
                
                # Try to find a clean break in the overlap text to avoid mid-word splits
                overlap_lines = overlap_text.split('\n')
                if len(overlap_lines) > 1:
                    overlap_text = "\n".join(overlap_lines[1:])
                else:
                    overlap_words = overlap_text.split(' ')
                    overlap_text = " ".join(overlap_words[1:])
                    
                current_chunk = overlap_text + "\n\n" + p + "\n\n"
                
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def load_and_chunk_documents(raw_docs_dir: str) -> List[DocumentChunk]:
    chunks = []
    timestamp = datetime.datetime.now().isoformat()
    
    # Find all Markdown and text files
    files = glob.glob(os.path.join(raw_docs_dir, "*.md")) + glob.glob(os.path.join(raw_docs_dir, "*.txt"))
    
    for file_path in files:
        filename = os.path.basename(file_path)
        doc_id = os.path.splitext(filename)[0]
        doc_type = infer_doc_type(filename)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        lines = content.strip().split('\n')
        # Infer title from the first line (strip markdown headers)
        title = lines[0].lstrip('#').strip() if lines else doc_id
        
        # Split into chunks of ~2000 characters (~500 tokens)
        text_chunks = split_text(content, max_chars=2000, overlap_chars=300)
        
        for i, text_content in enumerate(text_chunks):
            chunk = DocumentChunk(
                chunk_id=f"{doc_id}_chunk_{i}",
                doc_id=doc_id,
                title=title,
                content=text_content,
                source_version=timestamp,
                doc_type=doc_type
            )
            chunks.append(chunk)
            
    return chunks
