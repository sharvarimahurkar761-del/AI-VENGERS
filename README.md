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

---

# PulseIQ Action Policy & Feedback Loop

This is the Action Policy & Feedback Loop subsystem for PulseIQ. It uses a Contextual Bandit (LinUCB) to dynamically select the best intervention action for at-risk users, based on risk scores, behavioral attributions, and RAG knowledge assistance confidence.

## Getting Started

### Prerequisites
- Python 3.8+
- `numpy`

### Installation
```bash
pip install numpy
```

### Running the Validation
Run the evaluation script to see the agent learn and validate all requirements:
```bash
python evaluate.py
```

## Validation Outputs Explained

1. **Training Progress**: Shows the average reward over the first and last 100 episodes. It should trend up, indicating the bandit is learning from the simulated engagement rewards.
2. **Claim-2 Test**: Proves the bandit uses the detailed *attributions* vector, not just the raw risk score. It generates two synthetic users with the same exact `risk_score` (0.8) but different dominant attributions, and shows the bandit selects different actions.
3. **Policy Recovery Table**: Compares what the trained bandit thinks is the best action for each root cause against the hidden ground truth mapping. It should match with high accuracy.
4. **Aggregation / Root-cause Report**: Uses K-Means clustering over the log history to cluster users by attribution behavior and reports the dominant cause, recommended action, and average outcome for each cluster.
5. **Example Feedback Payload**: An example JSON payload that will be sent to Person 1 (Risk Engine) for retraining.

## Swapping to Real Endpoints

Once Person 1 (Risk Engine) and Person 2 (Knowledge Assistant) publish their real HTTP endpoints, you can integrate them with zero interface changes to the core system:

1. Open `mocks.py`.
2. In `RiskEngineClient.get_risk_score(self, user_id, _injected_cause=None)`, replace the mock generation with a real `requests.get(f"https://api.example.internal/risk/score/{user_id}")` call and return the JSON response.
3. In `KnowledgeAssistantClient.get_knowledge_response(self, user_id, issue_text)`, replace the mock generation with a real `requests.post("https://api.example.internal/knowledge/respond", json={"user_id": user_id, "issue_text": issue_text})` call and return the JSON response.

**Handling Schema Mismatches:** If Person 1 or Person 2's real response doesn't exactly match the mock schema (e.g., a missing field or different value range), log a warning rather than crashing. Use `.get()` with safe fallbacks in `agent.py` to ensure a schema mismatch is visible but doesn't take down the whole pipeline during integration.

**Hardcoded Assumptions to Revisit:**
- **Fixed $k=4$ in aggregation:** The aggregation layer uses a fixed $k=4$ to match our known synthetic causes. Once real data is flowing, revisit this clustering logic to determine $k$ dynamically (e.g., elbow method or silhouette score).
- **ATTRIBUTION_ACTION_MAP (Reward Simulation):** The current ground-truth mapping in `env.py` is hardcoded for synthetic testing. In the real system, you won't simulate rewards—you will measure real user engagement—so the `Simulator` and `RewardFunction` will be retired, but ensure the live system is capturing actual outcomes appropriately.
