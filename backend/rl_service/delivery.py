class ActionDeliverer:
    def deliver(self, user_id: str, action: str, context: dict):
        raise NotImplementedError

class MockDeliverer(ActionDeliverer):
    def deliver(self, user_id: str, action: str, context: dict):
        # Stands in for Person 4's real in-app nudge/tutorial channel
        # e.g., POST /app/nudge { user_id, action }
        pass
