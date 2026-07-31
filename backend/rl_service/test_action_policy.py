import pytest
import numpy as np
import json
from train import train_agent
from feedback import FeedbackLoop
from aggregate import Aggregator


@pytest.fixture(scope="module")
def trained_system():
    # Train once for the whole test module to save time
    agent, store, rewards, simulator = train_agent(episodes=1500)
    return agent, store, rewards, simulator


def moving_average(a, n=50):
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def test_reward_trends_upward(trained_system):
    _, _, rewards, _ = trained_system
    ma = moving_average(rewards, n=100)
    assert ma[-1] > ma[0], f"Reward did not trend upward. Start: {ma[0]}, End: {ma[-1]}"


def test_claim2_same_score_different_actions(trained_system):
    agent, _, _, simulator = trained_system

    user1 = simulator.generate_user_episode(
        force_cause='usage_decline', force_risk_score=0.8)
    user2 = simulator.generate_user_episode(
        force_cause='support_delay', force_risk_score=0.8)

    vec1 = agent.extract_features(user1['risk_profile'], user1['kg_response'])
    action1 = agent.choose_action(vec1)

    vec2 = agent.extract_features(user2['risk_profile'], user2['kg_response'])
    action2 = agent.choose_action(vec2)

    assert action1 != action2, f"Expected different actions for different attributions, got {action1} for both"


def test_policy_recovery_above_threshold(trained_system):
    agent, _, _, simulator = trained_system
    match_count = 0
    total_evals = 400

    for cause, truth in simulator.ground_truth.items():
        cause_matches = 0
        trials = 100
        for _ in range(trials):
            u = simulator.generate_user_episode(force_cause=cause)
            v = agent.extract_features(u['risk_profile'], u['kg_response'])
            a = agent.choose_action(v)
            if a == truth:
                cause_matches += 1
        match_count += cause_matches

    accuracy = (match_count / total_evals) * 100
    assert accuracy >= 90.0, f"Policy recovery accuracy too low: {accuracy}%"


def test_aggregation_finds_all_known_causes(trained_system):
    _, store, _, simulator = trained_system

    for _ in range(3):  # Run 3 times with different random seeds implicitly
        report = Aggregator.generate_report(store)
        lines = [line for line in report.split('\n') if line.strip()]
        assert len(
            lines) == 4, f"Expected exactly 4 clusters in report, got {len(lines)}"

        for cause in simulator.ground_truth.keys():
            assert cause in report, f"Cause {cause} missing from aggregation report:\n{report}"


def test_feedback_payload_schema(trained_system):
    _, store, _, _ = trained_system
    assert len(store.action_log) > 0

    sample_action = store.action_log[-1]
    sample_outcome = store.outcome_log[-1]

    payload_str = FeedbackLoop.generate_feedback_payload(
        sample_action, sample_outcome)
    payload = json.loads(payload_str)

    assert "user_id" in payload
    assert "features_at_decision_time" in payload
    assert "outcome" in payload

    outcome = payload["outcome"]
    assert "engagement_delta" in outcome
    assert "ticket_volume_delta" in outcome
    assert "satisfaction_delta" in outcome

    # Verify independent noise
    assert len(set([outcome["engagement_delta"], outcome["ticket_volume_delta"],
               outcome["satisfaction_delta"]])) > 1, "Metrics are identical, independent noise not working"
