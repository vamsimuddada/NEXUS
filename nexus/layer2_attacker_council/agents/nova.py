from typing import Dict, Any
from nexus.layer2_attacker_council.base_attacker import AttackerAgent
from nexus.utils import get_logger

logger = get_logger(__name__)

class NOVAAgent(AttackerAgent):
    """AI-Native Attacker. 4-phase cycle: PROBE, MEASURE, CRAFT, EXPLOIT."""

    def __init__(self, agent_id: str, profile: Dict[str, Any]):
        super().__init__(agent_id, profile)
        self.nova_phase = 0
        self.phases = ['PROBE', 'MEASURE', 'CRAFT', 'EXPLOIT']

    def plan_action(self, environment_state: dict) -> dict:
        current_nova_phase = self.phases[self.nova_phase % 4]
        self.nova_phase += 1
        
        # Guide LLM to act according to the specific phase
        environment_state['nova_phase'] = current_nova_phase
        return super().plan_action(environment_state)
