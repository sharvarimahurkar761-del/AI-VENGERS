import numpy as np
from train import train_agent
from feedback import FeedbackLoop
from aggregate import Aggregator
import random


def moving_average(a, n=50):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def run_evaluation():
    print("Training Agent... (Simulating 1500 users)")
    agent, store, rewards, simulator = train_agent(episodes=1500)

    # 1. Training Progress
    ma = moving_average(rewards, n=100)
    print("\n--- 1. Training Progress ---")
    print(f"First 100 episodes avg reward: {ma[0]:.2f}")
    print(f"Last 100 episodes avg reward: {ma[-1]:.2f}")
    print("Trending up? ", "YES" if ma[-1] > ma[0] else "NO")

    # 2. Claim-2 Test (Same risk score, different attributions -> different action)
    print("\n--- 2. Claim-2 Test ---")

    user1 = simulator.generate_user_episode(
        force_cause='usage_decline', force_risk_score=0.8)
    user2 = simulator.generate_user_episode(
        force_cause='support_delay', force_risk_score=0.8)

    vec1 = agent.extract_features(user1['risk_profile'], user1['kg_response'])
    action1 = agent.choose_action(vec1)

    vec2 = agent.extract_features(user2['risk_profile'], user2['kg_response'])
    action2 = agent.choose_action(vec2)

    print(f"User 1 (Dominant: usage_decline, Score: 0.8) -> Action: {action1}")
    print(f"User 2 (Dominant: support_delay, Score: 0.8) -> Action: {action2}")

    if action1 != action2:
        print("Claim-2 Test Result: PASS")
    else:
        print("Claim-2 Test Result: FAIL (Agent chose same action despite different attributions)")

    # 3. Policy Recovery Table
    print("\n--- 3. Policy Recovery Table ---")
    match_count = 0
    total_evals = 400

    print(f"{'Dominant Cause':<20} | {'Bandit Action':<20} | {'Ground Truth':<20}")
    print("-" * 65)

    for cause, truth in simulator.ground_truth.items():
        cause_matches = 0
        trials = 100
        action_counts = {}
        for _ in range(trials):
            u = simulator.generate_user_episode(force_cause=cause)
            v = agent.extract_features(u['risk_profile'], u['kg_response'])
            a = agent.choose_action(v)
            action_counts[a] = action_counts.get(a, 0) + 1
            if a == truth:
                cause_matches += 1

        most_picked = max(action_counts, key=action_counts.get)
        print(f"{cause:<20} | {most_picked:<20} | {truth:<20}")
        match_count += cause_matches

    accuracy = (match_count / total_evals) * 100
    print(f"Overall Match: {accuracy:.1f}%")

    # 4. Aggregation / Root-cause Report
    print("\n--- 4. Aggregation / Root-cause Report ---")
    report = Aggregator.generate_report(store)
    print(report)

    # 5. Example Feedback Payload
    print("\n--- 5. Example Feedback Payload ---")
    if len(store.action_log) > 0:
        sample_action = store.action_log[-1]
        sample_outcome = store.outcome_log[-1]
        payload = FeedbackLoop.generate_feedback_payload(
            sample_action, sample_outcome)
        print(payload)

    # 6. Ambiguous-Attribution Stress Test
    print("\n--- 6. Ambiguous-Attribution Stress Test ---")
    print("Simulating 100 users with ambiguous attributions (negative_sentiment and support_delay both high)")

    # Disable exploration for pure greedy inference
    original_alpha = agent.alpha
    agent.alpha = 0.0

    ambiguous_action_counts = {}
    for _ in range(100):
        # Force a user episode but we will manually override the attributions to be ambiguous
        user = simulator.generate_user_episode()
        # Create an ambiguous risk profile
        ambiguous_profile = user['risk_profile'].copy()
        ambiguous_profile['risk_score'] = 0.0
        ambiguous_kg = user['kg_response'].copy()
        ambiguous_kg['confidence'] = 0.0
        ambiguous_profile['attributions'] = [
            {"feature": "usage_decline", "impact": random.uniform(0.0, 0.05)},
            {"feature": "negative_sentiment",
                "impact": random.uniform(0.3, 0.8)},
            {"feature": "support_delay", "impact": random.uniform(0.3, 0.8)},
            {"feature": "onboarding_gap", "impact": random.uniform(0.0, 0.05)}
        ]

        vec = agent.extract_features(ambiguous_profile, ambiguous_kg)
        action = agent.choose_action(vec)
        ambiguous_action_counts[action] = ambiguous_action_counts.get(
            action, 0) + 1

    for action, count in ambiguous_action_counts.items():
        print(f"{count}% {action}")

    # Check if the choices are reasonable
    # Both negative_sentiment -> incentive and support_delay -> human_handoff should be chosen roughly equally
    incentive_pct = ambiguous_action_counts.get('incentive', 0)
    human_handoff_pct = ambiguous_action_counts.get('human_handoff', 0)

    print("\nAre choices reasonable given the mixed attribution?")
    if incentive_pct > 10 and human_handoff_pct > 10:
        print(
            f"YES: The agent gracefully splits decisions between incentive ({incentive_pct}%) and human_handoff ({human_handoff_pct}%), matching the ambiguous causes.")
    else:
        print("NO: The agent is skewed or choosing unrelated actions heavily.")

    agent.alpha = original_alpha


if __name__ == "__main__":
    run_evaluation()
