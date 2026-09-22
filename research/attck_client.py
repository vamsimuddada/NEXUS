"""
NEXUS — MITRE ATT&CK Integration
Live lookups against the MITRE ATT&CK STIX dataset.

Provides:
  - Technique metadata (name, tactic, description, detection notes)
  - Tactic chain validation (does this TTP sequence make sense?)
  - SIGMA rule enrichment (add ATT&CK context to generated rules)
  - Navigator overlay data (JSON for ATT&CK Navigator heatmap)

Falls back to a bundled static dict when offline.
ARM64-safe: pure Python + mitreattack-python (optional).
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional


# ── Static fallback data ──────────────────────────────────────────────────────
# Covers all 8 techniques used by the NEXUS twin — always available offline.

_STATIC_TECHNIQUES: dict[str, dict] = {
    "T1078": {
        "name": "Valid Accounts",
        "tactic": "initial-access",
        "tactic_name": "Initial Access",
        "description": "Adversaries may obtain and abuse credentials of existing accounts.",
        "detection": "Monitor for logon events with anomalous source IPs or times.",
        "platforms": ["Windows", "Linux", "macOS"],
        "data_sources": ["Logon Session", "User Account"],
        "subtechniques": ["T1078.001", "T1078.002", "T1078.003", "T1078.004"],
    },
    "T1021": {
        "name": "Remote Services",
        "tactic": "lateral-movement",
        "tactic_name": "Lateral Movement",
        "description": "Adversaries may use valid accounts to log into a service via remote desktop.",
        "detection": "Monitor for unusual RDP, SMB, or WinRM sessions.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["Network Traffic", "Logon Session"],
        "subtechniques": ["T1021.001", "T1021.002", "T1021.006"],
    },
    "T1059": {
        "name": "Command and Scripting Interpreter",
        "tactic": "execution",
        "tactic_name": "Execution",
        "description": "Adversaries may abuse command and script interpreters to execute commands.",
        "detection": "Monitor for PowerShell, cmd.exe, or wscript spawned by unusual parents.",
        "platforms": ["Windows", "Linux", "macOS"],
        "data_sources": ["Process", "Command"],
        "subtechniques": ["T1059.001", "T1059.003"],
    },
    "T1055": {
        "name": "Process Injection",
        "tactic": "defense-evasion",
        "tactic_name": "Defense Evasion",
        "description": "Adversaries may inject code into processes to evade detection.",
        "detection": "Monitor for Sysmon Event 10 (ProcessAccess) targeting LSASS.",
        "platforms": ["Windows", "Linux"],
        "data_sources": ["Process"],
        "subtechniques": ["T1055.001", "T1055.002", "T1055.012"],
    },
    "T1083": {
        "name": "File and Directory Discovery",
        "tactic": "discovery",
        "tactic_name": "Discovery",
        "description": "Adversaries may enumerate files and directories.",
        "detection": "Monitor for unusual directory traversal commands.",
        "platforms": ["Windows", "Linux", "macOS"],
        "data_sources": ["File", "Process"],
        "subtechniques": [],
    },
    "T1003": {
        "name": "OS Credential Dumping",
        "tactic": "credential-access",
        "tactic_name": "Credential Access",
        "description": "Adversaries may attempt to dump credentials from LSASS memory.",
        "detection": "Monitor for access to LSASS (Event 4662) and Mimikatz signatures.",
        "platforms": ["Windows"],
        "data_sources": ["Process", "Active Directory"],
        "subtechniques": ["T1003.001", "T1003.002"],
    },
    "T1486": {
        "name": "Data Encrypted for Impact",
        "tactic": "impact",
        "tactic_name": "Impact",
        "description": "Adversaries may encrypt data to interrupt availability (ransomware).",
        "detection": "Monitor for mass file modifications and shadow copy deletion.",
        "platforms": ["Windows", "Linux", "macOS"],
        "data_sources": ["File", "Process"],
        "subtechniques": [],
    },
    "T1071": {
        "name": "Application Layer Protocol",
        "tactic": "command-and-control",
        "tactic_name": "Command and Control",
        "description": "Adversaries may use application layer protocols for C2 communication.",
        "detection": "Monitor outbound connections to unusual destinations on common ports.",
        "platforms": ["Windows", "Linux", "macOS"],
        "data_sources": ["Network Traffic"],
        "subtechniques": ["T1071.001", "T1071.004"],
    },
}

# Kill-chain phase order for tactic validation
_TACTIC_ORDER = [
    "reconnaissance", "resource-development", "initial-access",
    "execution", "persistence", "privilege-escalation",
    "defense-evasion", "credential-access", "discovery",
    "lateral-movement", "collection", "command-and-control",
    "exfiltration", "impact",
]


# ── ATT&CK Client ─────────────────────────────────────────────────────────────

class ATTCKClient:
    """
    MITRE ATT&CK lookup client.
    Uses mitreattack-python + live STIX data when available,
    falls back to static bundled dict offline.
    """

    def __init__(self, use_live: bool = True):
        self._live_src = None
        self._use_live = use_live
        if use_live:
            self._init_live()

    def _init_live(self):
        try:
            from mitreattack.stix20 import MitreAttackData
            # Use bundled enterprise ATT&CK STIX file if available
            stix_path = Path(__file__).parent.parent / "data" / "enterprise-attack.json"
            if stix_path.exists():
                self._live_src = MitreAttackData(str(stix_path))
                print(f"[ATT&CK] Loaded from local STIX: {stix_path}")
            else:
                print("[ATT&CK] No local STIX file — using static fallback")
        except Exception as e:
            print(f"[ATT&CK] mitreattack-python unavailable ({e}) — using static fallback")

    # ── Lookup ────────────────────────────────────────────────────────────────

    def get_technique(self, technique_id: str) -> dict:
        """Return technique metadata. Always returns a dict (never raises)."""
        # Try live first
        if self._live_src:
            try:
                tech = self._live_src.get_object_by_attack_id(
                    technique_id, "technique"
                )
                if tech:
                    tactics = [
                        phase.phase_name
                        for phase in getattr(tech, "kill_chain_phases", [])
                        if phase.kill_chain_name == "mitre-attack"
                    ]
                    return {
                        "name":         tech.name,
                        "tactic":       tactics[0] if tactics else "unknown",
                        "tactic_name":  tactics[0].replace("-", " ").title() if tactics else "Unknown",
                        "description":  getattr(tech, "description", "")[:300],
                        "detection":    getattr(tech, "x_mitre_detection", ""),
                        "platforms":    getattr(tech, "x_mitre_platforms", []),
                        "data_sources": getattr(tech, "x_mitre_data_sources", []),
                        "subtechniques": [],
                        "source": "live",
                    }
            except Exception:
                pass

        # Static fallback
        data = dict(_STATIC_TECHNIQUES.get(technique_id, {
            "name":         technique_id,
            "tactic":       "unknown",
            "tactic_name":  "Unknown",
            "description":  f"Technique {technique_id} — no metadata available.",
            "detection":    "",
            "platforms":    [],
            "data_sources": [],
            "subtechniques": [],
        }))
        data["source"] = "static"
        return data

    def get_tactic_name(self, technique_id: str) -> str:
        return self.get_technique(technique_id).get("tactic_name", "Unknown")

    def get_detection_note(self, technique_id: str) -> str:
        return self.get_technique(technique_id).get("detection", "")

    # ── Tactic chain validation ───────────────────────────────────────────────

    def validate_tactic_chain(self, technique_ids: list[str]) -> dict:
        """
        Check whether a sequence of techniques follows a plausible kill-chain order.
        Returns a validation report.
        """
        tactics = []
        for tid in technique_ids:
            meta = self.get_technique(tid)
            tactic = meta.get("tactic", "unknown")
            tactics.append((tid, tactic))

        # Check for out-of-order jumps
        violations = []
        for i in range(1, len(tactics)):
            prev_tid, prev_tactic = tactics[i-1]
            curr_tid, curr_tactic = tactics[i]
            if (prev_tactic in _TACTIC_ORDER
                    and curr_tactic in _TACTIC_ORDER):
                prev_idx = _TACTIC_ORDER.index(prev_tactic)
                curr_idx = _TACTIC_ORDER.index(curr_tactic)
                if curr_idx < prev_idx - 2:   # allow some reordering
                    violations.append({
                        "from": f"{prev_tid} ({prev_tactic})",
                        "to":   f"{curr_tid} ({curr_tactic})",
                        "note": "Unusual kill-chain reversal",
                    })

        tactic_seq = [t for _, t in tactics]
        covered_phases = list(dict.fromkeys(
            t for t in tactic_seq if t in _TACTIC_ORDER
        ))

        return {
            "technique_count":  len(technique_ids),
            "tactic_sequence":  tactic_seq,
            "covered_phases":   covered_phases,
            "violations":       violations,
            "is_plausible":     len(violations) == 0,
            "completeness":     round(len(covered_phases) / len(_TACTIC_ORDER), 2),
        }

    # ── SIGMA rule enrichment ────────────────────────────────────────────────

    def enrich_sigma_rule(self, rule) -> dict:
        """
        Add ATT&CK metadata to a SigmaRule.
        Returns an enriched dict (does not mutate the rule object).
        """
        meta = self.get_technique(rule.technique)
        return {
            "rule_id":        rule.rule_id,
            "title":          rule.title,
            "severity":       rule.severity,
            "technique":      rule.technique,
            "technique_name": meta["name"],
            "tactic":         meta["tactic_name"],
            "detection_note": meta["detection"],
            "platforms":      meta["platforms"],
            "data_sources":   meta["data_sources"],
            "auto_generated": rule.auto_generated,
            "hit_count":      rule.hit_count,
            "attck_url":      f"https://attack.mitre.org/techniques/{rule.technique}/",
        }

    def enrich_all_rules(self, sigma_engine) -> list[dict]:
        """Enrich all rules in a SigmaEngine with ATT&CK metadata."""
        return [self.enrich_sigma_rule(r) for r in sigma_engine.rules]

    # ── Navigator overlay ────────────────────────────────────────────────────

    def navigator_layer(self, technique_stats: list[dict],
                        campaign_id: str = "nexus") -> dict:
        """
        Generate an ATT&CK Navigator layer JSON from campaign technique stats.
        Import the output at https://mitre-attack.github.io/attack-navigator/
        """
        techniques = []
        for stat in technique_stats:
            tid = stat["technique"]
            meta = self.get_technique(tid)
            # Score: evasion_rate → red (attacker winning), detection_rate → blue
            evasion = stat.get("evasion_rate", 0)
            score   = round(evasion * 100)
            color   = (f"#{'%02x' % int(255*evasion)}0000"   # red gradient
                       if evasion > 0.3
                       else "#0000ff")
            techniques.append({
                "techniqueID": tid,
                "tactic":      meta.get("tactic", ""),
                "score":       score,
                "color":       color,
                "comment":     (
                    f"Uses: {stat.get('uses',0)} | "
                    f"Evasion: {evasion:.1%} | "
                    f"Detection: {stat.get('detection_rate',0):.1%}"
                ),
                "enabled":     True,
                "metadata":    [
                    {"name": "Attacker", "value": stat.get("top_attacker", "mixed")},
                    {"name": "NEXUS campaign", "value": campaign_id},
                ],
            })

        return {
            "name":        f"NEXUS Campaign {campaign_id}",
            "versions":    {"attack": "14", "navigator": "4.9", "layer": "4.5"},
            "domain":      "enterprise-attack",
            "description": f"NEXUS co-evolution simulation results — campaign {campaign_id}",
            "filters":     {"platforms": ["Windows"]},
            "sorting":     3,
            "layout":      {"layout": "side", "showID": True, "showName": True},
            "hideDisabled": False,
            "techniques":   techniques,
            "gradient":     {"colors": ["#ff0000", "#ffffff", "#0000ff"],
                             "minValue": 0, "maxValue": 100},
            "legendItems": [
                {"label": "High evasion (attacker winning)", "color": "#ff0000"},
                {"label": "High detection (defender winning)", "color": "#0000ff"},
            ],
            "metadata": [{"name": "generated_by", "value": "NEXUS"}],
        }

    def save_navigator_layer(self, technique_stats: list[dict],
                              campaign_id: str,
                              path: str = "data/research/navigator_layer.json") -> str:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        layer = self.navigator_layer(technique_stats, campaign_id)
        with open(path, "w") as f:
            json.dump(layer, f, indent=2)
        print(f"[ATT&CK] Navigator layer → {path}")
        return path


# ── Singleton ─────────────────────────────────────────────────────────────────

_client: Optional[ATTCKClient] = None

def get_client(use_live: bool = True) -> ATTCKClient:
    global _client
    if _client is None:
        _client = ATTCKClient(use_live=use_live)
    return _client
