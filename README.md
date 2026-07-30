# AI-VENGERS

# PulseIQ – Explainable AI Customer Intelligence Platform

## Overview
PulseIQ is an Explainable AI Customer Intelligence Platform featuring a Risk & Behavior Engine.

### Features
- Feature engineering
- Data preprocessing
- PyTorch risk prediction
- SHAP explainability
- FastAPI REST API
- Feedback collection
- Automated retraining

### Tech Stack
- Python, PyTorch, FastAPI, SHAP, Pandas, NumPy, Scikit-learn, Uvicorn, Pytest

### Installation
- Create a virtual environment.
- Install dependencies: `pip install -r requirements.txt`
- Run the API: `uvicorn app.main:app --reload`
- Execute tests: `pytest`

### API Endpoints
- `GET /`
- `POST /risk/score`
- `POST /feedback`

---

# PulseIQ - Knowledge Assistant (RAG)

**Status:** Complete

This is the Retrieval-Augmented Generation (RAG) subsystem of the PulseIQ project. It provides an intelligent backend service for document ingestion, semantic search, and LLM-powered response generation. It takes user queries, embeds them, retrieves relevant document chunks from Qdrant, and securely uses Llama 3.3 to answer the query, strictly grounding the response in the provided context.

## How to Run Locally

1. **Start the Vector Database (Qdrant)**
   Ensure Docker Desktop is running, then start the Qdrant container:
   ```bash
   docker-compose up -d
   ```

2. **Run Document Ingestion**
   Ingest the sample files from `data/raw_docs/` into Qdrant:
   ```bash
   $env:PYTHONPATH="src"
   python src/knowledge_assistant/ingestion/index_builder.py
   ```

3. **Start the API Server**
   Start the FastAPI development server:
   ```bash
   $env:PYTHONPATH="src"
   uvicorn knowledge_assistant.api.main:app --reload --port 8080
   ```

## API Contract

**Endpoint:** `POST /knowledge/respond`

**Request:**
```json
{
  "user_id": "user_123",
  "issue_text": "I need to dump out all my logs into a CSV or PDF for compliance, how?"
}
```

**Response:**
```json
{
  "retrieved_docs": [
    {
      "doc_id": "faq_export_data",
      "title": "FAQ: How to Export Your Data",
      "snippet": "To export data from a specific dashboard view: 1. Navigate to the desired dashboard...",
      "relevance": 0.85
    }
  ],
  "grounded_response": "To export all your logs for compliance purposes, you can follow these steps as outlined in [FAQ: How to Export Your Data]...",
  "confidence": 0.9,
  "model_version": "llama-3.3-70b-versatile"
}
```

## Evaluation Results

To view the groundedness and hallucination results, check out the evaluation report:
[Evaluation Report](src/knowledge_assistant/eval/eval_report.md)

### Known Limitations

**Confidence Scoring Heuristic:** The current confidence score heuristic uses the presence of hedging language and citation density as a proxy for answer helpfulness. As a result, it cannot reliably distinguish between an LLM offering a genuinely helpful partial/workaround answer and an LLM merely citing a document to prove it was checked and found irrelevant. Both behaviors yield similar confidence scores (e.g. 0.55-0.75). A more accurate future fix would involve the LLM generator or judge directly outputting a helpfulness label (fully/partial/none) to drive the confidence score, rather than relying on a citation-density proxy.
