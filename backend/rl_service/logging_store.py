import datetime

class MemoryStore:
    def __init__(self):
        self.action_log = []
        self.outcome_log = []

    def log_action(self, user_id, action, risk_score, attributions, retrieval_confidence):
        timestamp = datetime.datetime.now(datetime.UTC).isoformat() + "Z"
        record = {
            'user_id': user_id,
            'action': action,
            'timestamp': timestamp,
            'risk_score': risk_score,
            'attributions': attributions,
            'retrieval_confidence': retrieval_confidence
        }
        self.action_log.append(record)
        return record

    def log_outcome(self, user_id, action, metrics):
        timestamp = datetime.datetime.now(datetime.UTC).isoformat() + "Z"
        record = {
            'user_id': user_id,
            'action_id': action,
            'engagement_delta': round(metrics['engagement_delta'], 3),
            'ticket_volume_delta': round(metrics['ticket_volume_delta'], 3),
            'satisfaction_delta': round(metrics['satisfaction_delta'], 3),
            'measured_at': timestamp
        }
        self.outcome_log.append(record)
        return record
