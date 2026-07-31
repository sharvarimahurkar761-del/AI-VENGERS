import numpy as np


class ContextualBandit:
    def __init__(self, actions, alpha=1.0):
        self.actions = actions
        self.n_actions = len(actions)
        self.alpha = alpha

        # Features: risk_score (1), usage_decline (1), negative_sentiment (1),
        # support_delay (1), onboarding_gap (1), confidence (1)
        # Total = 6 features
        self.d = 6

        # LinUCB parameters
        self.A = {a: np.identity(self.d) for a in self.actions}
        self.b = {a: np.zeros((self.d, 1)) for a in self.actions}
        self.theta = {a: np.zeros((self.d, 1)) for a in self.actions}

    def extract_features(self, risk_profile, kg_response):
        risk_score = risk_profile.get('risk_score', 0.0)
        confidence = kg_response.get('confidence', 0.0)

        attrs = {item['feature']: item['impact']
                 for item in risk_profile.get('attributions', [])}
        f1 = attrs.get('usage_decline', 0.0)
        f2 = attrs.get('negative_sentiment', 0.0)
        f3 = attrs.get('support_delay', 0.0)
        f4 = attrs.get('onboarding_gap', 0.0)

        return np.array([risk_score, f1, f2, f3, f4, confidence]).reshape(-1, 1)

    def choose_action(self, context_vector):
        p = {}
        for a in self.actions:
            A_inv = np.linalg.inv(self.A[a])
            self.theta[a] = A_inv.dot(self.b[a])

            # Expected reward
            mean = self.theta[a].T.dot(context_vector)[0, 0]
            # Confidence interval
            cb = self.alpha * \
                np.sqrt(context_vector.T.dot(A_inv).dot(context_vector))[0, 0]

            p[a] = mean + cb

        # Break ties randomly
        max_p = max(p.values())
        best_actions = [a for a, val in p.items() if val == max_p]
        return np.random.choice(best_actions)

    def update(self, action, context_vector, reward):
        self.A[action] += context_vector.dot(context_vector.T)
        self.b[action] += reward * context_vector
