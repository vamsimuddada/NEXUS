"""SIGMA rule generation module."""
import os
import yaml
import json
from typing import List, Dict, Any
from nexus.utils import get_logger, NexusLLM

logger = get_logger(__name__)

class SigmaRuleGenerator:
    """Generates new SIGMA rules using LLM."""

    def __init__(self):
        """Initialize with LLM."""
        self.llm = NexusLLM.get_rules_llm()

    def generate_rule(self, missed_attack: Dict) -> str:
        """Prompt LLM to generate a SIGMA rule for a missed attack."""
        system_prompt = "You are an expert SOC analyst writing SIGMA rules. Output ONLY valid YAML with no markdown formatting."
        user_prompt = f"Write a SIGMA rule to detect the following attack event:\n{yaml.dump(missed_attack)}\n"
        
        try:
            rule_str = self.llm.invoke(system_prompt, user_prompt)
            if self.validate_rule(rule_str):
                return rule_str
            else:
                logger.error("Generated rule failed validation.")
                return ""
        except Exception as e:
            logger.error(f"Failed to generate rule: {e}")
            return ""

    def generate_rules_for_gaps(self, gap_analysis: Dict) -> List[str]:
        """Generate rules for all missed attacks in a gap analysis."""
        missed = gap_analysis.get('missed_attacks', [])
        rules = []
        for atk in missed:
            rule = self.generate_rule(atk)
            if rule:
                rules.append(rule)
        return rules

    def validate_rule(self, rule_yaml: str) -> bool:
        """Validate YAML syntax and required fields."""
        try:
            rule = yaml.safe_load(rule_yaml)
            
            if not isinstance(rule, dict):
                return False
                
            has_title = 'title' in rule
            has_logsource = 'logsource' in rule
            has_detection = 'detection' in rule
            
            if has_title and has_logsource and has_detection:
                return True
            return False
        except yaml.YAMLError:
            return False

    def test_rule(self, rule_yaml: str, test_events: List[Dict]) -> Dict:
        """Test rule against events using field matching (simulated)."""
        matched = []
        try:
            rule_dict = yaml.safe_load(rule_yaml)
            detection = rule_dict.get('detection', {})
            
            search_terms = []
            for k, v in detection.items():
                if isinstance(v, dict):
                    for mk, mv in v.items():
                        search_terms.append(str(mv).lower())
                elif isinstance(v, str):
                    search_terms.append(v.lower())
            
            for event in test_events:
                event_str = json.dumps(event).lower()
                if search_terms and any(term in event_str for term in search_terms if term):
                    matched.append(event)
        except Exception as e:
            logger.error(f"Rule testing failed: {e}")

        return {
            'tested_events': len(test_events),
            'matched_events': len(matched),
            'matches': matched
        }

    def save_rule(self, rule_yaml: str, output_dir: str) -> str:
        """Save rule to file."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        try:
            rule_dict = yaml.safe_load(rule_yaml)
            title = rule_dict.get('title', 'generated_rule').replace(' ', '_').lower()
            filepath = os.path.join(output_dir, f"{title}.yml")
            with open(filepath, 'w') as f:
                f.write(rule_yaml)
            return filepath
        except Exception as e:
            logger.error(f"Failed to save rule: {e}")
            return ""
