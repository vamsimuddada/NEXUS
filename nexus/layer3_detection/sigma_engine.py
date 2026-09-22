import os
import yaml
import re
from typing import Dict, List, Any
from nexus.utils import get_logger

logger = get_logger(__name__)

class SigmaDetectionEngine:
    """
    Custom SIGMA rule evaluator without pySigma dependency.
    Evaluates log events against a set of SIGMA rules in YAML format.
    """

    def __init__(self):
        self.rules: List[Dict] = []
        self.stats = {
            "total_rules": 0,
            "total_evaluations": 0,
            "total_matches": 0,
            "match_rate": 0.0
        }

    def load_rules(self, rules_dir: str) -> int:
        """
        Recursively load all .yml/.yaml files from a directory and parse them.
        
        Args:
            rules_dir: Directory containing YAML rule files.
            
        Returns:
            Number of successfully loaded rules.
        """
        loaded = 0
        if not os.path.exists(rules_dir):
            logger.warning(f"Rules directory not found: {rules_dir}")
            return loaded

        for root, _, files in os.walk(rules_dir):
            for file in files:
                if file.endswith((".yml", ".yaml")):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r') as f:
                            rule_yaml = f.read()
                            if self.add_rule(rule_yaml):
                                loaded += 1
                    except Exception as e:
                        logger.error(f"Failed to load rule from {filepath}: {e}")
        return loaded

    def add_rule(self, rule_yaml: str) -> bool:
        """
        Parse and add a single rule from a YAML string.
        
        Args:
            rule_yaml: YAML string representing the rule.
            
        Returns:
            True if added successfully, False otherwise.
        """
        try:
            rule = yaml.safe_load(rule_yaml)
            if not rule or not isinstance(rule, dict):
                return False
            
            # Basic validation
            if 'title' not in rule or 'detection' not in rule:
                return False
                
            self.rules.append(rule)
            self.stats["total_rules"] += 1
            return True
        except Exception as e:
            logger.error(f"Failed to parse rule YAML: {e}")
            return False

    def _evaluate_condition(self, field_conditions: Dict, event: Dict) -> bool:
        """
        Match field values with modifiers like contains, startswith, endswith, regex.
        
        Args:
            field_conditions: Dictionary of fields to modifiers to values.
            event: Log event dictionary.
            
        Returns:
            True if event matches conditions, False otherwise.
        """
        for key, expected_value in field_conditions.items():
            parts = key.split('|')
            field = parts[0]
            modifier = parts[1] if len(parts) > 1 else None

            # Flatten event for simpler access if nested
            event_val = event.get(field)
            if event_val is None:
                return False
                
            event_val_str = str(event_val)
            expected_val_str = str(expected_value)

            if modifier == 'contains':
                if expected_val_str.lower() not in event_val_str.lower():
                    return False
            elif modifier == 'startswith':
                if not event_val_str.lower().startswith(expected_val_str.lower()):
                    return False
            elif modifier == 'endswith':
                if not event_val_str.lower().endswith(expected_val_str.lower()):
                    return False
            elif modifier == 'regex':
                if not re.search(expected_val_str, event_val_str):
                    return False
            else:
                if event_val_str.lower() != expected_val_str.lower():
                    return False
                    
        return True

    def _evaluate_rule(self, rule: Dict, event: Dict) -> bool:
        """
        Check if event matches rule's detection section.
        
        Args:
            rule: Rule dictionary.
            event: Log event dictionary.
            
        Returns:
            True if matched, False otherwise.
        """
        detection = rule.get("detection", {})
        if not detection:
            return False
            
        selection = detection.get("selection", {})
        if not selection:
            return False
            
        # Simplified evaluation: checks only the 'selection' criteria
        return self._evaluate_condition(selection, event)

    def evaluate(self, log_event: Dict) -> List[Dict]:
        """
        Return all matching rules for a log event.
        
        Args:
            log_event: Log event to evaluate.
            
        Returns:
            List of matched rule dictionaries.
        """
        self.stats["total_evaluations"] += 1
        matches = []
        for rule in self.rules:
            if self._evaluate_rule(rule, log_event):
                self.stats["total_matches"] += 1
                matches.append({
                    "rule_id": rule.get("id", "unknown"),
                    "title": rule.get("title", "unknown"),
                    "level": rule.get("level", "unknown"),
                    "tags": rule.get("tags", []),
                    "description": rule.get("description", "")
                })
                
        if self.stats["total_evaluations"] > 0:
            self.stats["match_rate"] = self.stats["total_matches"] / self.stats["total_evaluations"]
            
        return matches

    def evaluate_batch(self, log_events: List[Dict]) -> List[Dict]:
        """
        Batch evaluation of multiple log events.
        
        Args:
            log_events: List of log events to evaluate.
            
        Returns:
            List containing match results for each event, flattened or nested.
            We will return a flat list of dicts with an 'event_id' reference if available.
        """
        all_matches = []
        for event in log_events:
            matches = self.evaluate(event)
            if matches:
                all_matches.append({
                    "event": event,
                    "matches": matches
                })
        return all_matches

    def get_stats(self) -> Dict:
        """Get evaluation statistics."""
        return self.stats

    def export_rules(self, output_dir: str):
        """
        Dump all rules as YAML files to output_dir.
        
        Args:
            output_dir: Directory to dump rules to.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        for rule in self.rules:
            rule_id = rule.get("id", rule.get("title", "rule").replace(" ", "_").lower())
            filepath = os.path.join(output_dir, f"{rule_id}.yml")
            try:
                with open(filepath, 'w') as f:
                    yaml.dump(rule, f)
            except Exception as e:
                logger.error(f"Failed to export rule {rule_id}: {e}")
