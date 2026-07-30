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
