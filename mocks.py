import datetime
import random
import json

class RiskEngineClient:
    """Mock for Person 1 - Risk & Behavior Engine"""
    
    def get_risk_score(self, user_id: str, _injected_cause: str = None) -> dict:
        """
        GET /risk/score/{user_id}
        Returns synthetic risk data.
        _injected_cause is only used for simulation purposes to drive ground truth.
        """
        causes = ['usage_decline', 'negative_sentiment', 'support_delay', 'onboarding_gap']
        dominant_cause = _injected_cause if _injected_cause else random.choice(causes)
        
        # Base random attributions (small impacts)
        attributions = {
            'usage_decline': random.uniform(0.0, 0.1),
            'negative_sentiment': random.uniform(0.0, 0.1),
            'support_delay': random.uniform(0.0, 0.1),
            'onboarding_gap': random.uniform(0.0, 0.1)
        }
        
        # Amplify the dominant cause
        if dominant_cause == 'usage_decline':
            attributions['usage_decline'] = random.uniform(0.4, 0.8)
        elif dominant_cause == 'negative_sentiment':
            attributions['negative_sentiment'] = random.uniform(0.4, 0.8)
        elif dominant_cause == 'support_delay':
            attributions['support_delay'] = random.uniform(0.4, 0.8)
        elif dominant_cause == 'onboarding_gap':
            attributions['onboarding_gap'] = random.uniform(0.4, 0.8)

        # Format as requested
        attr_list = [{"feature": k, "impact": round(v, 2)} for k, v in attributions.items()]
        
        # Risk score: somewhat arbitrary but let's make it realistic (0.0 to 1.0)
        risk_score = min(1.0, max(0.0, random.gauss(0.6, 0.15)))
        
        return {
            "user_id": user_id,
            "risk_score": round(risk_score, 2),
            "attributions": attr_list,
            "model_version": "mock-risk-v1",
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat() + "Z"
        }

class KnowledgeAssistantClient:
    """Mock for Person 2 - Knowledge Assistant"""
    
    def get_knowledge_response(self, user_id: str, issue_text: str) -> dict:
        """
        POST /knowledge/respond
        Returns synthetic knowledge retrieval data.
        """
        confidence = random.uniform(0.4, 0.95)
        return {
            "retrieved_docs": [
                {
                    "doc_id": f"doc_{random.randint(1000, 9999)}",
                    "title": "How to use the new feature",
                    "snippet": "To use this feature, navigate to...",
                    "relevance": round(random.uniform(0.5, 1.0), 2)
                }
            ],
            "grounded_response": "Based on the documentation, you should...",
            "confidence": round(confidence, 2),
            "model_version": "mock-rag-v2"
        }
