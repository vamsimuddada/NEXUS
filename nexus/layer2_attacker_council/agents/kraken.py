from typing import Dict, Any
from nexus.layer2_attacker_council.base_attacker import AttackerAgent
from nexus.utils import get_logger

logger = get_logger(__name__)

class KRAKENAgent(AttackerAgent):
    """Ransomware Syndicate Agent. Aggressive, fast lateral movement."""

    def __init__(self, agent_id: str, profile: Dict[str, Any]):
        super().__init__(agent_id, profile)

    def plan_action(self, environment_state: dict) -> dict:
        total_hosts = environment_state.get('total_hosts', 1)
        if len(self.compromised_hosts) / total_hosts > 0.5:
            return {'action': 'deploy_ransomware', 'technique_id': 'T1486', 'target': 'all', 'reasoning': 'Threshold reached, deploying ransomware'}
        
        return super().plan_action(environment_state)

    def execute_action(self, action: dict, digital_twin: Any) -> dict:
        if action.get('action') == 'deploy_ransomware':
            logs = digital_twin.inject_attack_logs('T1486', 'external', 'all', 'system')
            return {'success': True, 'logs_generated': logs, 'details': 'Ransomware deployed'}
        return super().execute_action(action, digital_twin)
