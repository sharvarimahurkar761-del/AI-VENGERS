from env import Simulator, RewardFunction
from mocks import RiskEngineClient, KnowledgeAssistantClient
from agent import ContextualBandit
from delivery import MockDeliverer
from logging_store import MemoryStore


def train_agent(episodes=1500):
    risk_client = RiskEngineClient()
    kg_client = KnowledgeAssistantClient()
    simulator = Simulator(risk_client, kg_client)

    actions = ['guided_tutorial', 'proactive_nudge',
               'human_handoff', 'incentive']
    # alpha controls exploration. A smaller alpha allows it to converge faster
    # to what it learned in an easy simulation environment like this.
    agent = ContextualBandit(actions=actions, alpha=0.5)
    deliverer = MockDeliverer()
    store = MemoryStore()

    rewards = []

    for i in range(episodes):
        user_data = simulator.generate_user_episode()

        context_vec = agent.extract_features(
            user_data['risk_profile'], user_data['kg_response'])
        chosen_action = agent.choose_action(context_vec)

        reward, metrics = RewardFunction.calculate_reward(
            chosen_action, user_data['best_action'])

        deliverer.deliver(user_data['user_id'],
                          chosen_action, user_data['risk_profile'])

        store.log_action(
            user_id=user_data['user_id'],
            action=chosen_action,
            risk_score=user_data['risk_profile']['risk_score'],
            attributions=user_data['risk_profile']['attributions'],
            retrieval_confidence=user_data['kg_response']['confidence']
        )

        store.log_outcome(
            user_id=user_data['user_id'],
            action=chosen_action,
            metrics=metrics
        )

        agent.update(chosen_action, context_vec, reward)
        rewards.append(reward)

    return agent, store, rewards, simulator
