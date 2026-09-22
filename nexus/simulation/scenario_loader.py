import yaml
import os
from typing import Dict, List, Optional
from nexus.utils import get_logger

logger = get_logger(__name__)

class ScenarioLoader:
    """Scenario Loader for simulation engine."""
    
    BUILTIN_SCENARIOS = {
        'apt_campaign': {
            'name': 'apt_campaign',
            'attackers': ['StealthAPT', 'InitialAccessBroker'],
            'rounds': 20,
            'focus': 'stealth_exfiltration'
        },
        'ransomware_blitz': {
            'name': 'ransomware_blitz',
            'attackers': ['RansomwareGang'],
            'rounds': 10,
            'focus': 'rapid_encryption'
        },
        'full_war': {
            'name': 'full_war',
            'attackers': ['StealthAPT', 'RansomwareGang', 'InitialAccessBroker'],
            'rounds': 50,
            'focus': 'total_compromise'
        }
    }
    
    @classmethod
    def load_scenario(cls, path: str) -> Dict:
        """Loads a scenario configuration from a YAML file."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Scenario file not found: {path}")
            
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
            
    @classmethod
    def list_scenarios(cls, scenarios_dir: Optional[str] = None) -> Dict:
        """Lists all available scenarios (built-in and dynamically loaded)."""
        scenarios = cls.BUILTIN_SCENARIOS.copy()
        
        if scenarios_dir and os.path.exists(scenarios_dir):
            for filename in os.listdir(scenarios_dir):
                if filename.endswith(('.yaml', '.yml')):
                    path = os.path.join(scenarios_dir, filename)
                    try:
                        scenario = cls.load_scenario(path)
                        if 'name' in scenario:
                            scenarios[scenario['name']] = scenario
                    except Exception as e:
                        logger.error(f"Failed to load scenario from {path}: {e}")
                        
        return scenarios
        
    @classmethod
    def create_scenario(cls, name: str, attackers: List[str], rounds: int, config: Dict) -> Dict:
        """Helper to create a scenario dictionary dynamically."""
        scenario = {
            'name': name,
            'attackers': attackers,
            'rounds': rounds,
            'config': config
        }
        return scenario
