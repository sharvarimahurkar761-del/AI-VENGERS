import json

class FeedbackLoop:
    @staticmethod
    def run_retraining_job(store, agent):
        """
        Simulates a scheduled job that might re-compute weights or batch update.
        Since LinUCB updates online, this just represents the trigger point
        if we were doing batch learning.
        """
        pass

    @staticmethod
    def generate_feedback_payload(action_record, outcome_record):
        """
        Produces a feedback_payload in the shape Person 1 would want 
        for retraining their risk model.
        """
        payload = {
            "user_id": action_record['user_id'],
            "features_at_decision_time": {
                "risk_score": action_record['risk_score'],
                "attributions": action_record['attributions'],
            },
            "outcome": {
                "engagement_delta": outcome_record['engagement_delta'],
                "ticket_volume_delta": outcome_record['ticket_volume_delta'],
                "satisfaction_delta": outcome_record['satisfaction_delta']
            }
        }
        return json.dumps(payload, indent=2)
