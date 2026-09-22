"""Proactive threat hunting module."""
import json
from typing import List, Dict, Any
from nexus.utils import get_logger, NexusLLM

logger = get_logger(__name__)

class ProactiveThreatHunter:
    """Hunts for advanced threats using LLM hypothesis generation."""

    def __init__(self):
        """Initialize threat hunter."""
        self.llm = NexusLLM()

    def generate_hypothesis(self, recent_alerts: List[Dict], psychology_profiles: Dict) -> List[Dict]:
        """LLM generates hunting hypotheses."""
        system_prompt = "You are an expert Threat Hunter. Generate 3 specific hunting hypotheses based on the context."
        user_prompt = f"Recent alerts:\n{json.dumps(recent_alerts)}\n\nAttacker Profiles:\n{json.dumps(psychology_profiles)}\n\nReturn ONLY a JSON list of dictionaries with keys: 'title', 'description', 'query'."
        
        try:
            response = self.llm.invoke(system_prompt, user_prompt)
            start = response.find('[')
            end = response.rfind(']') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                hypotheses = json.loads(json_str)
                return hypotheses
            else:
                return []
        except Exception as e:
            logger.error(f"Failed to generate hypotheses: {e}")
            return []

    def hunt(self, digital_twin: Any, hypothesis: Dict) -> List[Dict]:
        """Execute hunt query."""
        query = hypothesis.get('query', '')
        if hasattr(digital_twin, 'execute_query'):
            return digital_twin.execute_query(query)
        else:
            logger.warning("digital_twin missing execute_query")
            return []

    def correlate_events(self, events: List[Dict]) -> List[Dict]:
        """Group related events by user/host."""
        correlated = {}
        for event in events:
            key = event.get('host', event.get('user', 'unknown'))
            if key not in correlated:
                correlated[key] = []
            correlated[key].append(event)
            
        results = []
        for key, evs in correlated.items():
            results.append({
                'entity': key,
                'event_count': len(evs),
                'events': evs
            })
            
        return results
