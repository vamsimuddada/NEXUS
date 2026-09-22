from typing import Dict, Any
from nexus.layer2_attacker_council.base_attacker import AttackerAgent
from nexus.utils import get_logger

logger = get_logger(__name__)

class VIPERAgent(AttackerAgent):
    """Nation-State APT Agent. Patient, uses living-off-the-land."""
    
    def __init__(self, agent_id: str, profile: Dict[str, Any]):
        super().__init__(agent_id, profile)
        self.dwell_time = 0
        self.dormant_rounds = 0

    def plan_action(self, environment_state: dict) -> dict:
        self.dwell_time += 1
        if self.current_phase == 'dormant':
            self.dormant_rounds += 1
            if self.dormant_rounds >= 3:
                self.current_phase = 'recon'
                self.dormant_rounds = 0
            return {'action': 'idle', 'technique_id': 'none', 'target': 'none', 'reasoning': 'Dormant phase'}
            
        if self.is_detected:
            self.current_phase = 'dormant'
            self.dormant_rounds = 0
            return {'action': 'idle', 'technique_id': 'none', 'target': 'none', 'reasoning': 'Detected, going dormant'}

        return super().plan_action(environment_state)
