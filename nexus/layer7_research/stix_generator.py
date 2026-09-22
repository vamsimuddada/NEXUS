import json
import uuid
from typing import Dict, List
from pathlib import Path
from datetime import datetime, timezone
from nexus.utils import get_logger

logger = get_logger(__name__)

class StixBundleGenerator:
    """Generates STIX 2.1 bundles to represent threat intel from simulations."""

    def __init__(self):
        pass

    def _get_timestamp(self) -> str:
        """Returns the current UTC timestamp formatted for STIX."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def _generate_id(self, type_name: str) -> str:
        """Generates a STIX identifier for a given object type."""
        return f"{type_name}--{uuid.uuid4()}"

    def create_indicator(self, technique_id: str, pattern: str, name: str) -> Dict:
        """Creates a STIX 2.1 Indicator object."""
        return {
            "type": "indicator",
            "spec_version": "2.1",
            "id": self._generate_id("indicator"),
            "created": self._get_timestamp(),
            "modified": self._get_timestamp(),
            "name": name,
            "pattern": pattern,
            "pattern_type": "stix",
            "valid_from": self._get_timestamp(),
            "description": f"Indicator for technique {technique_id}"
        }

    def create_attack_pattern(self, technique_id: str, name: str) -> Dict:
        """Creates a STIX 2.1 Attack Pattern object."""
        return {
            "type": "attack-pattern",
            "spec_version": "2.1",
            "id": self._generate_id("attack-pattern"),
            "created": self._get_timestamp(),
            "modified": self._get_timestamp(),
            "name": name,
            "external_references": [
                {
                    "source_name": "mitre-attack",
                    "external_id": technique_id
                }
            ]
        }

    def create_campaign(self, sim_id: str, attacker_id: str, techniques: List[str]) -> Dict:
        """Creates a STIX 2.1 Campaign object."""
        return {
            "type": "campaign",
            "spec_version": "2.1",
            "id": self._generate_id("campaign"),
            "created": self._get_timestamp(),
            "modified": self._get_timestamp(),
            "name": f"Simulation Campaign {sim_id}",
            "description": f"Campaign conducted by {attacker_id} in simulation {sim_id}",
            "aliases": [sim_id]
        }

    def generate_bundle(self, sim_results: Dict) -> str:
        """Generates a complete STIX 2.1 bundle containing all relevant objects."""
        objects = []
        
        sim_id = sim_results.get("sim_id", "unknown-sim")
        attacker_id = sim_results.get("attacker_id", "unknown-attacker")
        techniques_used = sim_results.get("techniques", ["T1190"])

        campaign = self.create_campaign(sim_id, attacker_id, techniques_used)
        objects.append(campaign)

        for i, tech in enumerate(techniques_used):
            ap = self.create_attack_pattern(tech, f"Attack Pattern {tech}")
            ind = self.create_indicator(tech, f"[process:name = 'malware_{i}.exe']", f"Indicator for {tech}")
            objects.extend([ap, ind])
            
            # Relationship between indicator and attack pattern
            rel = {
                "type": "relationship",
                "spec_version": "2.1",
                "id": self._generate_id("relationship"),
                "created": self._get_timestamp(),
                "modified": self._get_timestamp(),
                "relationship_type": "indicates",
                "source_ref": ind["id"],
                "target_ref": ap["id"]
            }
            objects.append(rel)

        bundle = {
            "type": "bundle",
            "id": f"bundle--{uuid.uuid4()}",
            "objects": objects
        }
        return json.dumps(bundle, indent=2)

    def save_bundle(self, bundle: str, output_path: str) -> None:
        """Saves the STIX bundle JSON string to a file."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(bundle)
        logger.info(f"Saved STIX bundle to {output_path}")
