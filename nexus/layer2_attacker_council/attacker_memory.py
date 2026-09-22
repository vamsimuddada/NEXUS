from typing import List, Dict, Any
from collections import defaultdict
from nexus.utils import get_logger

logger = get_logger(__name__)

class AttackerMemory:
    """In-memory experience store for attacker agents."""

    def __init__(self):
        self.experiences: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.tactic_outcomes: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    def store_experience(self, agent_id: str, experience: Dict[str, Any]) -> None:
        """Store a new experience for an agent."""
        self.experiences[agent_id].append(experience)
        logger.debug(f"Stored experience for {agent_id}")

    def recall_similar(self, agent_id: str, situation: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Recall similar experiences using keyword matching."""
        if agent_id not in self.experiences:
            return []
        
        words = set(situation.lower().split())
        scored_experiences = []
        
        for exp in self.experiences[agent_id]:
            exp_text = str(exp).lower()
            score = sum(1 for word in words if word in exp_text)
            if score > 0:
                scored_experiences.append((score, exp))
                
        scored_experiences.sort(key=lambda x: x[0], reverse=True)
        return [exp for score, exp in scored_experiences[:top_k]]

    def get_agent_history(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get the full experience history for an agent."""
        return self.experiences.get(agent_id, [])

    def store_tactic_outcome(self, agent_id: str, technique_id: str, success: bool, detected: bool) -> None:
        """Store the outcome of a specific tactic."""
        self.tactic_outcomes[agent_id].append({
            'technique_id': technique_id,
            'success': success,
            'detected': detected
        })

    def get_technique_success_rate(self, agent_id: str, technique_id: str) -> float:
        """Get the success rate of a specific technique for an agent."""
        outcomes = [o for o in self.tactic_outcomes.get(agent_id, []) if o['technique_id'] == technique_id]
        if not outcomes:
            return 0.0
        successes = sum(1 for o in outcomes if o['success'])
        return successes / len(outcomes)

    def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get overall statistics for an agent."""
        outcomes = self.tactic_outcomes.get(agent_id, [])
        total_actions = len(outcomes)
        if total_actions == 0:
            return {'total_actions': 0, 'success_rate': 0.0, 'detection_rate': 0.0}
            
        successes = sum(1 for o in outcomes if o['success'])
        detections = sum(1 for o in outcomes if o['detected'])
        
        return {
            'total_actions': total_actions,
            'success_rate': successes / total_actions,
            'detection_rate': detections / total_actions
        }
