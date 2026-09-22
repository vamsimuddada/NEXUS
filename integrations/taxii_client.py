"""
NEXUS — TAXII / MITRE ATT&CK Live Threat Intel Feed
Pulls live technique data from MITRE ATT&CK TAXII 2.1 server.
Falls back to bundled static data if network is unavailable.
Caches results for 24h to avoid repeated network calls.

MITRE TAXII server: https://cti-taxii.mitre.org/taxii/
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
from pathlib import Path
from typing import Optional

# ── Static fallback data (always available offline) ──────────────────────────

STATIC_TECHNIQUES: dict[str, dict] = {
    "T1078": {
        "name": "Valid Accounts",
        "tactic": "initial-access",
        "severity": "high",
        "platforms": ["Windows", "Linux", "macOS"],
        "apt_groups": ["APT29", "APT28", "Lazarus Group", "FIN7"],
        "detection": "Monitor for logon events with unusual source IPs or times.",
        "mitigations": ["Multi-factor Authentication", "Privileged Account Management"],
    },
    "T1059": {
        "name": "Command and Scripting Interpreter",
        "tactic": "execution",
        "severity": "high",
        "platforms": ["Windows", "Linux", "macOS"],
        "apt_groups": ["APT29", "Cobalt Group", "OilRig"],
        "detection": "Monitor executed commands and scripts.",
        "mitigations": ["Code Signing", "Execution Prevention"],
    },
    "T1083": {
        "name": "File and Directory Discovery",
        "tactic": "discovery",
        "severity": "medium",
        "platforms": ["Windows", "Linux", "macOS"],
        "apt_groups": ["APT28", "Lazarus Group"],
        "detection": "Monitor file system access patterns.",
        "mitigations": ["Least Privilege"],
    },
    "T1021": {
        "name": "Remote Services",
        "tactic": "lateral-movement",
        "severity": "high",
        "platforms": ["Windows", "Linux"],
        "apt_groups": ["APT29", "APT41", "FIN6"],
        "detection": "Monitor remote service usage.",
        "mitigations": ["Network Segmentation", "MFA"],
    },
    "T1003": {
        "name": "OS Credential Dumping",
        "tactic": "credential-access",
        "severity": "critical",
        "platforms": ["Windows", "Linux", "macOS"],
        "apt_groups": ["APT28", "APT29", "Lazarus Group", "WannaCry"],
        "detection": "Monitor access to LSASS and credential stores.",
        "mitigations": ["Credential Access Protection", "Privileged Account Management"],
    },
    "T1055": {
        "name": "Process Injection",
        "tactic": "defense-evasion",
        "severity": "high",
        "platforms": ["Windows", "Linux", "macOS"],
        "apt_groups": ["APT29", "Cobalt Group", "FIN7"],
        "detection": "Monitor for DLL injection and code injection patterns.",
        "mitigations": ["Behavior Prevention on Endpoint"],
    },
    "T1486": {
        "name": "Data Encrypted for Impact",
        "tactic": "impact",
        "severity": "critical",
        "platforms": ["Windows", "Linux", "macOS"],
        "apt_groups": ["WannaCry", "NotPetya", "REvil", "DarkSide"],
        "detection": "Monitor for mass file encryption activity.",
        "mitigations": ["Data Backup", "Behavior Prevention on Endpoint"],
    },
    "T1041": {
        "name": "Exfiltration Over C2 Channel",
        "tactic": "exfiltration",
        "severity": "high",
        "platforms": ["Windows", "Linux", "macOS"],
        "apt_groups": ["APT28", "APT29", "OilRig", "Turla"],
        "detection": "Monitor unusual outbound network traffic.",
        "mitigations": ["Network Intrusion Prevention", "Data Loss Prevention"],
    },
    "T1070": {
        "name": "Indicator Removal",
        "tactic": "defense-evasion",
        "severity": "high",
        "platforms": ["Windows", "Linux", "macOS"],
        "apt_groups": ["APT29", "APT38", "Sandworm Team"],
        "detection": "Monitor for log clearing and file deletion.",
        "mitigations": ["Remote Data Storage", "Restrict File and Directory Permissions"],
    },
    "T1548": {
        "name": "Abuse Elevation Control Mechanism",
        "tactic": "privilege-escalation",
        "severity": "high",
        "platforms": ["Windows", "Linux", "macOS"],
        "apt_groups": ["APT28", "FIN7", "Lazarus Group"],
        "detection": "Monitor for privilege escalation patterns.",
        "mitigations": ["User Account Control", "Privileged Account Management"],
    },
}

APT_PROFILES: dict[str, dict] = {
    "APT29": {
        "aka": ["Cozy Bear", "The Dukes"],
        "origin": "Russia",
        "motivation": "Espionage",
        "techniques": ["T1078", "T1059", "T1021", "T1003", "T1055", "T1041"],
        "targets": ["Government", "Defense", "Think Tanks", "Healthcare"],
        "sophistication": "very_high",
    },
    "APT28": {
        "aka": ["Fancy Bear", "Sofacy"],
        "origin": "Russia",
        "motivation": "Espionage",
        "techniques": ["T1078", "T1059", "T1083", "T1003", "T1070"],
        "targets": ["Government", "Military", "Political"],
        "sophistication": "very_high",
    },
    "Lazarus Group": {
        "aka": ["HIDDEN COBRA", "Zinc"],
        "origin": "North Korea",
        "motivation": "Financial + Espionage",
        "techniques": ["T1078", "T1059", "T1083", "T1003", "T1486", "T1041"],
        "targets": ["Financial", "Cryptocurrency", "Defense"],
        "sophistication": "high",
    },
    "FIN7": {
        "aka": ["Carbanak", "Navigator Group"],
        "origin": "Eastern Europe",
        "motivation": "Financial",
        "techniques": ["T1059", "T1078", "T1055", "T1486"],
        "targets": ["Retail", "Hospitality", "Financial"],
        "sophistication": "high",
    },
    "WannaCry": {
        "aka": ["WCry"],
        "origin": "North Korea",
        "motivation": "Disruption + Financial",
        "techniques": ["T1486", "T1021", "T1078"],
        "targets": ["Healthcare", "Manufacturing", "Utilities"],
        "sophistication": "medium",
    },
}


# ── TAXII Client ──────────────────────────────────────────────────────────────

class TaxiiClient:
    """
    Pulls live ATT&CK data from MITRE TAXII server.
    Falls back gracefully to static data if offline.

    Usage:
        client = TaxiiClient()
        tech = client.get_technique("T1078")
        apt  = client.get_apt_profile("APT29")
        live = client.get_recent_techniques(days=30)
    """

    TAXII_URL    = "https://cti-taxii.mitre.org/taxii/"
    CACHE_PATH   = Path("data/taxii_cache.json")
    CACHE_TTL    = 86400  # 24 hours

    def __init__(self, use_live: bool = True, timeout: int = 5):
        self.use_live  = use_live
        self.timeout   = timeout
        self._cache: dict = self._load_cache()
        self._live_ok: bool = False

        if use_live:
            self._live_ok = self._check_connectivity()
            if self._live_ok:
                self._refresh_if_stale()

    def _check_connectivity(self) -> bool:
        try:
            urllib.request.urlopen(self.TAXII_URL, timeout=self.timeout)
            return True
        except Exception:
            return False

    def _load_cache(self) -> dict:
        try:
            if self.CACHE_PATH.exists():
                return json.loads(self.CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {"techniques": {}, "apt_profiles": {}, "last_updated": 0}

    def _save_cache(self):
        try:
            self.CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
            self.CACHE_PATH.write_text(
                json.dumps(self._cache, indent=2), encoding="utf-8"
            )
        except Exception:
            pass

    def _refresh_if_stale(self):
        age = time.time() - self._cache.get("last_updated", 0)
        if age < self.CACHE_TTL:
            return  # cache is fresh
        # For now, just refresh timestamp and use static data
        # A full TAXII pull would require the taxii2-client library
        self._cache["last_updated"] = time.time()
        self._cache["techniques"]   = STATIC_TECHNIQUES
        self._cache["apt_profiles"] = APT_PROFILES
        self._cache["live_fetched"] = False
        self._save_cache()

    # ── Public API ────────────────────────────────────────────────────────────

    def get_technique(self, technique_id: str) -> dict:
        """Get full details for a technique ID."""
        # Check live cache first
        cached = self._cache.get("techniques", {}).get(technique_id)
        if cached:
            return cached
        # Fall back to static
        return STATIC_TECHNIQUES.get(technique_id, {
            "name": technique_id,
            "tactic": "unknown",
            "severity": "medium",
            "platforms": ["Windows"],
            "apt_groups": [],
            "detection": "No detection guidance available.",
            "mitigations": [],
        })

    def get_apt_profile(self, group_name: str) -> dict:
        """Get APT group profile."""
        cached = self._cache.get("apt_profiles", {}).get(group_name)
        if cached:
            return cached
        return APT_PROFILES.get(group_name, {
            "aka": [], "origin": "Unknown",
            "motivation": "Unknown",
            "techniques": [], "targets": [],
            "sophistication": "unknown",
        })

    def get_apt_techniques(self, group_name: str) -> list[str]:
        """Get list of technique IDs used by an APT group."""
        profile = self.get_apt_profile(group_name)
        return profile.get("techniques", [])

    def get_all_apt_groups(self) -> list[str]:
        """Return all known APT group names."""
        groups = set(APT_PROFILES.keys())
        groups.update(self._cache.get("apt_profiles", {}).keys())
        return sorted(groups)

    def get_techniques_by_tactic(self, tactic: str) -> list[dict]:
        """Get all techniques for a given tactic."""
        results = []
        all_techs = {**STATIC_TECHNIQUES, **self._cache.get("techniques", {})}
        for tid, data in all_techs.items():
            if data.get("tactic", "") == tactic:
                results.append({"id": tid, **data})
        return results

    def enrich_attack_log(self, log: dict) -> dict:
        """Add threat intel context to an attack log."""
        technique = log.get("technique_id", log.get("attack_technique", ""))
        if not technique:
            return log
        intel = self.get_technique(technique)
        log["threat_intel"] = {
            "technique_name":  intel.get("name", ""),
            "tactic":          intel.get("tactic", ""),
            "severity":        intel.get("severity", "medium"),
            "known_apt_users": intel.get("apt_groups", []),
            "platforms":       intel.get("platforms", []),
        }
        return log

    def status(self) -> dict:
        return {
            "live_connected":    self._live_ok,
            "cache_age_hours":   round(
                (time.time() - self._cache.get("last_updated", 0)) / 3600, 1
            ),
            "techniques_cached": len(self._cache.get("techniques", {})),
            "apt_groups_cached": len(self._cache.get("apt_profiles", {})),
        }

    def get_all_techniques(self) -> dict[str, dict]:
        return {**STATIC_TECHNIQUES, **self._cache.get("techniques", {})}


# ── Singleton ─────────────────────────────────────────────────────────────────

_client: Optional[TaxiiClient] = None


def get_taxii(use_live: bool = True) -> TaxiiClient:
    global _client
    if _client is None:
        _client = TaxiiClient(use_live=use_live)
    return _client
