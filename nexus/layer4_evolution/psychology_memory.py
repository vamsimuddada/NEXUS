"""Attacker psychology memory module."""
from typing import List, Dict, Any
from nexus.utils import get_logger

logger = get_logger(__name__)

class AttackerPsychologyMemory:
    """Tracks and predicts attacker behavior."""

    def __init__(self):
        """In-memory storage."""
        self.memory: Dict[str, List[Dict]] = {}

    def record_behavior(self, agent_id: str, action: Dict, outcome: Dict) -> None:
        """Store behavioral data."""
        if agent_id not in self.memory:
            self.memory[agent_id] = []
        
        record = {
            'action': action,
            'outcome': outcome
        }
        self.memory[agent_id].append(record)

    def get_agent_profile(self, agent_id: str) -> Dict:
        """Compute profile of an agent."""
        history = self.memory.get(agent_id, [])
        
        techs = {}
        successes = 0
        detections = 0
        
        for item in history:
            tech = item['action'].get('technique_id', 'unknown')
            techs[tech] = techs.get(tech, 0) + 1
            
            if item['outcome'].get('success', False):
                successes += 1
            if item['outcome'].get('detected', False):
                detections += 1
                
        total = len(history) if history else 1
        
        return {
            'preferred_techniques': techs,
            'success_rate': successes / total if total > 0 else 0,
            'detection_rate': detections / total if total > 0 else 0,
            'stealth_level': 1.0 - (detections / total) if total > 0 else 1.0,
            'risk_assessment': 'high' if (successes / total) > 0.5 else 'low'
        }

    def predict_next_action(self, agent_id: str, current_state: Dict) -> List[Dict]:
        """Predict likely next techniques."""
        profile = self.get_agent_profile(agent_id)
        prefs = profile.get('preferred_techniques', {})
        
        sorted_prefs = sorted(prefs.items(), key=lambda x: x[1], reverse=True)
        predictions = []
        
        total_actions = sum(prefs.values()) or 1
        for tech, count in sorted_prefs:
            confidence = count / total_actions
            predictions.append({'technique_id': tech, 'confidence': confidence})
            
        return predictions

    def compare_agents(self, agent_ids: List[str]) -> Dict:
        """Comparative analysis of multiple agents."""
        comparison = {}
        for aid in agent_ids:
            comparison[aid] = self.get_agent_profile(aid)
        return comparison

    def detect_behavioral_shift(self, agent_id: str, window: int = 10) -> Dict:
        """Detect if agent changed tactics."""
        history = self.memory.get(agent_id, [])
        if len(history) < window * 2:
            return {'shift_detected': False, 'reason': 'insufficient_data'}
            
        old_window = history[-window*2:-window]
        new_window = history[-window:]
        
        old_techs = {item['action'].get('technique_id') for item in old_window}
        new_techs = {item['action'].get('technique_id') for item in new_window}
        
        intersection = old_techs.intersection(new_techs)
        shift = len(intersection) < len(old_techs) * 0.5
        
        return {
            'shift_detected': shift,
            'old_techniques': list(old_techs),
            'new_techniques': list(new_techs)
        }
