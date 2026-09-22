from typing import Dict, Any
from nexus.layer2_attacker_council.base_attacker import AttackerAgent
from nexus.utils import get_logger

logger = get_logger(__name__)

class CIPHERAgent(AttackerAgent):
    """Access Broker Agent. Focuses on initial access and shares it."""

    def __init__(self, agent_id: str, profile: Dict[str, Any]):
        super().__init__(agent_id, profile)
        self.shared_hosts = set()

    def plan_action(self, environment_state: dict) -> dict:
        new_hosts = self.compromised_hosts - self.shared_hosts
        if new_hosts:
            host_to_share = next(iter(new_hosts))
            return {
                'action': 'share_access', 
                'technique_id': 'none', 
                'target': host_to_share, 
                'reasoning': 'Sharing newly compromised host with others'
            }
            
        return super().plan_action(environment_state)

    def execute_action(self, action: dict, digital_twin: Any) -> dict:
        if action.get('action') == 'share_access':
            target = action.get('target')
            self.shared_hosts.add(target)
            return {'success': True, 'logs_generated': [], 'details': f"Shared access to {target}"}
            
        return super().execute_action(action, digital_twin)
