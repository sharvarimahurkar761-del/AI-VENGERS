import random
import uuid
from mocks import RiskEngineClient, KnowledgeAssistantClient

class Simulator:
    def __init__(self, risk_client: RiskEngineClient, kg_client: KnowledgeAssistantClient):
        self.risk_client = risk_client
        self.kg_client = kg_client
        
        # Ground truth mapping (hidden from agent)
        self.ground_truth = {
            'usage_decline': 'guided_tutorial',
            'negative_sentiment': 'incentive',
            'support_delay': 'human_handoff',
            'onboarding_gap': 'guided_tutorial'
        }
        self.causes = list(self.ground_truth.keys())

    def generate_user_episode(self, force_cause=None, force_risk_score=None):
        user_id = str(uuid.uuid4())
        true_cause = force_cause if force_cause else random.choice(self.causes)
        
        risk_profile = self.risk_client.get_risk_score(user_id, _injected_cause=true_cause)
        
        if force_risk_score is not None:
            risk_profile['risk_score'] = force_risk_score
            
        kg_response = self.kg_client.get_knowledge_response(user_id, "mock issue text")
        
        best_action = self.ground_truth[true_cause]
        
        return {
            'user_id': user_id,
            'risk_profile': risk_profile,
            'kg_response': kg_response,
            'true_cause': true_cause,
            'best_action': best_action
        }

class RewardFunction:
    @staticmethod
    def calculate_reward(chosen_action, best_action):
        import random
        # Base signal: 1.0 if matching, 0.0 otherwise
        base_signal = 1.0 if chosen_action == best_action else 0.0
        
        # Independent noise per metric
        noise_std = 0.2
        engagement_delta = base_signal + random.gauss(0, noise_std)
        satisfaction_delta = base_signal + random.gauss(0, noise_std)
        # ticket_volume goes DOWN when base signal is good
        ticket_volume_delta = -base_signal + random.gauss(0, noise_std)
        
        # Combined reward for the bandit
        reward = (engagement_delta + satisfaction_delta - ticket_volume_delta) / 3.0
        
        metrics = {
            'engagement_delta': engagement_delta,
            'satisfaction_delta': satisfaction_delta,
            'ticket_volume_delta': ticket_volume_delta
        }
        
        return reward, metrics
