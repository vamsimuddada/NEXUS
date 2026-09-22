"""
NEXUS — SIEM Forwarder
Forwards attack events as Elastic Common Schema (ECS) JSON.
Outputs to:
  1. data/siem/nexus_events.ndjson  — importable into Elastic/Kibana/Splunk
  2. HTTP POST to local Elasticsearch (auto-detected on port 9200)
  3. CEF syslog string (for any CEF-capable SIEM)

ECS reference: https://www.elastic.co/guide/en/ecs/current/index.html
"""
from __future__ import annotations

import json
import socket
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── ECS field mapping ─────────────────────────────────────────────────────────

MITRE_TACTIC_MAP = {
    "T1078": ("initial-access",       "Valid Accounts"),
    "T1059": ("execution",            "Command and Scripting Interpreter"),
    "T1083": ("discovery",            "File and Directory Discovery"),
    "T1021": ("lateral-movement",     "Remote Services"),
    "T1003": ("credential-access",    "OS Credential Dumping"),
    "T1055": ("defense-evasion",      "Process Injection"),
    "T1548": ("privilege-escalation", "Abuse Elevation Control Mechanism"),
    "T1486": ("impact",               "Data Encrypted for Impact"),
    "T1041": ("exfiltration",         "Exfiltration Over C2 Channel"),
    "T1070": ("defense-evasion",      "Indicator Removal"),
}

SEVERITY_MAP = {
    "low":    ("low",      30),
    "medium": ("medium",   50),
    "high":   ("critical", 80),
}


def _to_ecs(log: dict) -> dict:
    """Convert a NEXUS attack log to Elastic Common Schema format."""
    technique  = log.get("technique_id", log.get("attack_technique", "T0000"))
    attacker   = log.get("attacker", "UNKNOWN")
    host_name  = log.get("host", "unknown")
    user_name  = log.get("user", "unknown")
    stealth    = log.get("stealth_level", "medium")
    detected   = log.get("detected", False)
    ts         = log.get("timestamp", datetime.now(timezone.utc).isoformat())

    tactic_id, tech_name = MITRE_TACTIC_MAP.get(
        technique, ("unknown", technique)
    )
    sev_label, sev_score = SEVERITY_MAP.get(stealth, ("medium", 50))
    if detected:
        outcome = "success"  # detected = defender success
    else:
        outcome = "failure"  # not detected = attacker success (defender failed)

    return {
        "@timestamp": ts,
        "event": {
            "kind":     "alert",
            "category": ["intrusion_detection"],
            "type":     ["info"],
            "outcome":  outcome,
            "severity": sev_score,
            "module":   "nexus",
            "dataset":  "nexus.attack",
        },
        "host": {
            "name":     host_name,
            "hostname": host_name,
            "type":     log.get("host_role", "workstation"),
        },
        "user": {
            "name": user_name,
        },
        "threat": {
            "framework":  "MITRE ATT&CK",
            "tactic": {
                "id":   tactic_id,
                "name": tactic_id.replace("-", " ").title(),
            },
            "technique": {
                "id":   technique,
                "name": tech_name,
            },
        },
        "agent": {
            "name":    "nexus-forwarder",
            "type":    "nexus",
            "version": "1.0.0",
        },
        "tags": ["nexus", "simulation", attacker.lower(), tactic_id],
        "labels": {
            "nexus_attacker":  attacker,
            "nexus_stealth":   stealth,
            "nexus_detected":  str(detected).lower(),
            "nexus_technique": technique,
        },
        "message": (
            f"[NEXUS] {attacker} used {technique} ({tech_name}) "
            f"on {host_name} as {user_name} "
            f"[stealth={stealth}] [detected={detected}]"
        ),
    }


def _to_cef(log: dict) -> str:
    """Convert to CEF (Common Event Format) syslog string."""
    technique = log.get("technique_id", "T0000")
    attacker  = log.get("attacker", "NEXUS")
    host_name = log.get("host", "unknown")
    user_name = log.get("user", "unknown")
    stealth   = log.get("stealth_level", "medium")
    detected  = log.get("detected", False)
    _, sev_score = SEVERITY_MAP.get(stealth, ("medium", 50))

    ext = (
        f"src=ATTACKER shost={host_name} "
        f"duser={user_name} act={technique} "
        f"nexusAttacker={attacker} nexusStealth={stealth} "
        f"nexusDetected={detected}"
    )
    return (
        f"CEF:0|NEXUS|CyberWarfareSimulation|1.0|"
        f"{technique}|MITRE {technique}|{sev_score}|{ext}"
    )


# ── Forwarder class ───────────────────────────────────────────────────────────

class SiemForwarder:
    """
    Forwards NEXUS events to one or more SIEM outputs.

    Usage:
        fwd = SiemForwarder()
        fwd.forward(attack_log_dict)
        fwd.flush()   # write buffered events to disk
    """

    def __init__(self,
                 output_dir: str = "data/siem",
                 elastic_url: str = "http://localhost:9200",
                 es_index: str = "nexus-events",
                 enable_file: bool = True,
                 enable_elastic: bool = True,
                 enable_cef: bool = True):
        self.output_dir     = Path(output_dir)
        self.elastic_url    = elastic_url.rstrip("/")
        self.es_index       = es_index
        self.enable_file    = enable_file
        self.enable_cef     = enable_cef
        self._buffer: list[dict] = []
        self._es_available  = False

        if enable_file:
            self.output_dir.mkdir(parents=True, exist_ok=True)

        if enable_elastic:
            self._es_available = self._check_elastic()

    def _check_elastic(self) -> bool:
        """Check if Elasticsearch is running locally."""
        try:
            import urllib.request
            req = urllib.request.Request(
                self.elastic_url,
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=2)
            print(f"[SIEM] Elasticsearch detected at {self.elastic_url}")
            return True
        except Exception:
            return False

    def forward(self, log: dict) -> None:
        """Forward a single attack log event."""
        ecs = _to_ecs(log)
        self._buffer.append(ecs)

        # Write to Elasticsearch if available
        if self._es_available:
            self._send_to_elastic(ecs)

        # Auto-flush every 50 events
        if len(self._buffer) >= 1:
            self.flush()

    def forward_batch(self, logs: list[dict]) -> None:
        """Forward multiple logs at once."""
        for log in logs:
            self.forward(log)
        self.flush()

    def flush(self) -> None:
        """Write buffered events to NDJSON file."""
        if not self._buffer or not self.enable_file:
            return
        out_file = self.output_dir / "nexus_events.ndjson"
        with open(out_file, "a", encoding="utf-8") as f:
            for event in self._buffer:
                f.write(json.dumps(event) + "\n")
                if self.enable_cef:
                    # Also append CEF to separate file
                    pass  # CEF via log dict not ecs
        self._buffer.clear()

    def flush_cef(self, logs: list[dict]) -> None:
        """Write logs as CEF to a separate file."""
        if not self.enable_file:
            return
        cef_file = self.output_dir / "nexus_events.cef"
        with open(cef_file, "a", encoding="utf-8") as f:
            for log in logs:
                f.write(_to_cef(log) + "\n")

    def _send_to_elastic(self, ecs_event: dict) -> None:
        """POST a single ECS event to Elasticsearch."""
        try:
            import urllib.request
            url  = f"{self.elastic_url}/{self.es_index}/_doc"
            body = json.dumps(ecs_event).encode("utf-8")
            req  = urllib.request.Request(
                url, data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(req, timeout=3)
        except Exception:
            pass  # Silently fail — SIEM is optional

    def stats(self) -> dict:
        """Return forwarder stats."""
        out_file = self.output_dir / "nexus_events.ndjson"
        n_stored = 0
        if out_file.exists():
            with open(out_file, encoding="utf-8") as f:
                n_stored = sum(1 for _ in f)
        return {
            "events_in_file": n_stored,
            "buffered":       len(self._buffer),
            "elastic_live":   self._es_available,
            "output_path":    str(self.output_dir / "nexus_events.ndjson"),
        }

    def get_recent(self, n: int = 20) -> list[dict]:
        """Read the last n events from the NDJSON file."""
        out_file = self.output_dir / "nexus_events.ndjson"
        if not out_file.exists():
            return []
        lines = []
        with open(out_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        lines.append(json.loads(line))
                    except Exception:
                        pass
        return lines[-n:]


# ── Singleton ─────────────────────────────────────────────────────────────────

_forwarder: Optional[SiemForwarder] = None


def get_forwarder(**kwargs) -> SiemForwarder:
    global _forwarder
    if _forwarder is None:
        _forwarder = SiemForwarder(**kwargs)
    return _forwarder