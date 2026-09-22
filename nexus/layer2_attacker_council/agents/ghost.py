import random
from typing import Dict, Any
from nexus.layer2_attacker_council.base_attacker import AttackerAgent
from nexus.utils import get_logger

logger = get_logger(__name__)

class GHOSTAgent(AttackerAgent):
    """Insider Threat Agent. Uses valid credentials, hesitates sometimes."""

    def __init__(self, agent_id: str, profile: Dict[str, Any]):
        super().__init__(agent_id, profile)

    def plan_action(self, environment_state: dict) -> dict:
        if random.random() < 0.2:
            return {'action': 'idle', 'technique_id': 'none', 'target': 'none', 'reasoning': 'Hesitating due to emotional conflict'}
        return super().plan_action(environment_state)
