"""
NEXUS — Layer 7: STIX 2.1 Bundle Generator
Converts battle reports and campaign records into structured STIX 2.1 bundles.

Produces:
  - ThreatActor objects   (one per attacker persona)
  - AttackPattern objects (one per MITRE ATT&CK technique observed)
  - Campaign objects      (per NEXUS campaign)
  - Indicator objects     (from auto-generated SIGMA rules)
  - Relationship objects  (links ThreatActor → AttackPattern, etc.)
  - Sighting objects      (each detection event)
  - Bundle                (wraps all of the above)

ARM64-safe: pure Python + stix2 library.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import stix2


def _parse_ts(ts) -> datetime:
    """Parse any ISO timestamp string or datetime into a timezone-aware datetime."""
    if isinstance(ts, datetime):
        return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)
    for fmt in (
        "%Y-%m-%dT%H:%M:%S.%f+00:00", "%Y-%m-%dT%H:%M:%S+00:00",
        "%Y-%m-%dT%H:%M:%S.%fZ",      "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f",       "%Y-%m-%dT%H:%M:%S",
    ):
        try:
            return datetime.strptime(str(ts), fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return datetime.now(timezone.utc)



# ── MITRE ATT&CK technique → STIX external reference ─────────────────────────

def _attck_ref(technique_id: str) -> stix2.ExternalReference:
    return stix2.ExternalReference(
        source_name="mitre-attack",
        url=f"https://attack.mitre.org/techniques/{technique_id}/",
        external_id=technique_id,
    )


# ── Agent personality descriptors ─────────────────────────────────────────────

_AGENT_META = {
    "VIPER":  {"aliases": ["APT-VIPER"], "description": "Nation-state APT operator. Patient, low-and-slow, living-off-the-land."},
    "KRAKEN": {"aliases": ["KRAKEN-SYNDICTE"], "description": "Ransomware syndicate operator. Fast, aggressive, double-extortion."},
    "GHOST":  {"aliases": ["INSIDER-GHOST"], "description": "Disgruntled insider threat. Env-aware, credential abuser."},
    "HYDRA":  {"aliases": ["HYDRA-COLLECTIVE"], "description": "Hacktivist collective. Chaotic, disruptive, defacement-focused."},
    "NOVA":   {"aliases": ["NOVA-AI"], "description": "AI-native adversarial ML attacker. Probes and evades detection systems."},
    "CIPHER": {"aliases": ["CIPHER-BROKER"], "description": "Criminal initial-access broker. Specialises in credential theft and access sales."},
}


# ── STIX Bundle Generator ─────────────────────────────────────────────────────

class STIXBundleGenerator:
    """
    Generates STIX 2.1 bundles from NEXUS battle/campaign data.

    Usage:
        gen = STIXBundleGenerator(identity_name="NEXUS-SOC")
        bundle = gen.from_campaign(campaign_record)
        gen.save(bundle, "data/stix/campaign_001.json")
    """

    def __init__(self, identity_name: str = "NEXUS Autonomous SOC"):
        self.identity = stix2.Identity(
            name=identity_name,
            identity_class="system",
            description="NEXUS autonomous cybersecurity simulation platform.",
        )
        self._objects: list = [self.identity]
        self._threat_actors: dict[str, stix2.ThreatActor] = {}
        self._attack_patterns: dict[str, stix2.AttackPattern] = {}

    def _get_or_create_threat_actor(self, agent_name: str) -> stix2.ThreatActor:
        if agent_name in self._threat_actors:
            return self._threat_actors[agent_name]
        meta = _AGENT_META.get(agent_name, {
            "aliases": [agent_name],
            "description": f"NEXUS attacker agent {agent_name}.",
        })
        ta = stix2.ThreatActor(
            name=agent_name,
            aliases=meta["aliases"],
            description=meta["description"],
            threat_actor_types=["nation-state" if agent_name == "VIPER"
                                 else "crime-syndicate" if agent_name == "KRAKEN"
                                 else "insider-threat" if agent_name == "GHOST"
                                 else "activist" if agent_name == "HYDRA"
                                 else "unknown"],
            sophistication=("expert" if agent_name in ("VIPER", "NOVA")
                            else "intermediate" if agent_name in ("KRAKEN", "CIPHER")
                            else "novice"),
        )
        self._threat_actors[agent_name] = ta
        self._objects.append(ta)
        return ta

    def _get_or_create_attack_pattern(self, technique_id: str) -> stix2.AttackPattern:
        if technique_id in self._attack_patterns:
            return self._attack_patterns[technique_id]
        names = {
            "T1078": "Valid Accounts",
            "T1021": "Remote Services",
            "T1059": "Command and Scripting Interpreter",
            "T1055": "Process Injection",
            "T1083": "File and Directory Discovery",
            "T1003": "OS Credential Dumping",
            "T1486": "Data Encrypted for Impact",
            "T1071": "Application Layer Protocol",
        }
        ap = stix2.AttackPattern(
            name=names.get(technique_id, technique_id),
            description=f"MITRE ATT&CK technique {technique_id}",
            external_references=[_attck_ref(technique_id)],
        )
        self._attack_patterns[technique_id] = ap
        self._objects.append(ap)
        return ap

    # ── From Battle Report ─────────────────────────────────────────────────────

    def from_battle(self, battle_report) -> stix2.Bundle:
        """Generate a STIX bundle from a single BattleReport."""
        self._objects = [self.identity]
        self._threat_actors = {}
        self._attack_patterns = {}

        # Campaign object for this battle
        campaign = stix2.Campaign(
            name=f"NEXUS Battle {battle_report.battle_id}",
            description=(
                f"Simulated cyber battle. Winner: {battle_report.winner}. "
                f"Turns: {battle_report.num_turns}. "
                f"F1={battle_report.metrics.get('f1_score', 0):.3f}"
            ),
            first_seen=_parse_ts(battle_report.timestamp),
            last_seen=_parse_ts(battle_report.timestamp),
            objective="Adversarial co-evolution simulation",
        )
        self._objects.append(campaign)

        # Build ThreatActors, AttackPatterns, Relationships per attack log
        seen_pairs: set[tuple] = set()
        sightings: list[stix2.Sighting] = []

        for log in battle_report.attacker_logs:
            agent_name = log.get("attacker", "UNKNOWN")
            technique   = log.get("attack_technique")
            if not technique:
                continue

            ta = self._get_or_create_threat_actor(agent_name)
            ap = self._get_or_create_attack_pattern(technique)

            pair = (ta.id, ap.id)
            if pair not in seen_pairs:
                seen_pairs.add(pair)
                rel = stix2.Relationship(
                    relationship_type="uses",
                    source_ref=ta.id,
                    target_ref=ap.id,
                    description=f"{agent_name} used {technique} during battle {battle_report.battle_id}",
                )
                self._objects.append(rel)

                # ThreatActor attributed to campaign
                attr = stix2.Relationship(
                    relationship_type="attributed-to",
                    source_ref=campaign.id,
                    target_ref=ta.id,
                )
                self._objects.append(attr)

        # Indicators from auto-generated SIGMA rules
        for result in battle_report.detection_results:
            if (result.get("sigma_fired")
                    and result.get("ensemble_verdict") == "malicious"
                    and result.get("true_label") == "malicious"):
                technique = result.get("technique")
                if not technique:
                    continue
                ap = self._get_or_create_attack_pattern(technique)
                indicator = stix2.Indicator(
                    name=f"NEXUS Detection: {technique}",
                    description=(
                        f"Detected via SIGMA+GNN+LLM ensemble. "
                        f"GNN score={result.get('gnn_score', 0):.2f}, "
                        f"confidence={result.get('ensemble_confidence', 0):.2f}"
                    ),
                    pattern=f"[process:command_line MATCHES '{technique}']",
                    pattern_type="stix",
                    indicator_types=["malicious-activity"],
                    valid_from=_parse_ts(battle_report.timestamp),
                    created_by_ref=self.identity.id,
                )
                self._objects.append(indicator)
                ind_rel = stix2.Relationship(
                    relationship_type="indicates",
                    source_ref=indicator.id,
                    target_ref=ap.id,
                )
                self._objects.append(ind_rel)

        return stix2.Bundle(objects=self._objects)

    # ── From Campaign Record ───────────────────────────────────────────────────

    def from_campaign(self, campaign_record) -> stix2.Bundle:
        """Generate a comprehensive STIX bundle from a full CampaignRecord."""
        self._objects = [self.identity]
        self._threat_actors = {}
        self._attack_patterns = {}

        # Top-level campaign
        cid = campaign_record.campaign_id
        campaign = stix2.Campaign(
            name=f"NEXUS Campaign {cid}",
            description=(
                f"{campaign_record.battles_completed} battles. "
                f"F1 range: {min(campaign_record.f1_history):.3f}–"
                f"{max(campaign_record.f1_history):.3f}. "
                f"SIGMA rules: {campaign_record.sigma_rule_history[0]}→"
                f"{campaign_record.sigma_rule_history[-1]}. "
                f"NOVA peak evasion: {max(campaign_record.nova_evasion_history):.1%}."
            ),
            first_seen=_parse_ts(campaign_record.start_time),
            last_seen=datetime.now(timezone.utc),
            objective="Adversarial co-evolution research simulation",
        )
        self._objects.append(campaign)

        # All agents and all techniques from final ELO table
        for row in campaign_record.final_elo_table:
            name = row["entity"]
            if name == "DEFENDER":
                continue
            ta = self._get_or_create_threat_actor(name)
            rel = stix2.Relationship(
                relationship_type="attributed-to",
                source_ref=campaign.id,
                target_ref=ta.id,
            )
            self._objects.append(rel)

        # Technique effectiveness as AttackPatterns
        for stat in campaign_record.technique_stats:
            tech = stat["technique"]
            ap = self._get_or_create_attack_pattern(tech)
            # Note evasion data as a custom indicator
            indicator = stix2.Indicator(
                name=f"Technique Effectiveness: {tech}",
                description=(
                    f"Technique {tech} used {stat['uses']} times. "
                    f"Evasion rate: {stat['evasion_rate']:.1%}. "
                    f"Detection rate: {stat['detection_rate']:.1%}."
                ),
                pattern=f"[process:command_line MATCHES '{tech}']",
                pattern_type="stix",
                indicator_types=["malicious-activity"],
                valid_from=_parse_ts(campaign_record.start_time),
                created_by_ref=self.identity.id,
            )
            self._objects.append(indicator)
            self._objects.append(stix2.Relationship(
                relationship_type="indicates",
                source_ref=indicator.id,
                target_ref=ap.id,
            ))

        return stix2.Bundle(objects=self._objects)

    # ── Save ──────────────────────────────────────────────────────────────────

    def save(self, bundle: stix2.Bundle, path: str) -> str:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(bundle.serialize(pretty=True))
        print(f"[STIX] Bundle saved → {path} ({len(bundle.objects)} objects)")
        return path

    def object_count(self, bundle: stix2.Bundle) -> dict:
        counts: dict[str, int] = {}
        for obj in bundle.objects:
            t = obj.get("type", "unknown")
            counts[t] = counts.get(t, 0) + 1
        return counts
