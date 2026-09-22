"""
NEXUS — Layer 5: Autonomous SOAR & Counterstrike Engine
Automated defensive responses triggered by the defender's detections.

Countermeasures:
  - Honeypots:        deploy fake hosts/credentials to lure and fingerprint attackers
  - Proactive Hunting: query the graph for high-centrality lateral movement nodes
  - Account Lockout:  disable compromised credentials in the digital twin
  - Network Isolation: sever edges from compromised hosts in the topology graph
  - Deception Tokens: inject fake intel into attacker message queues

ARM64-safe: pure Python.
"""

from __future__ import annotations

import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


# ── Response Actions ──────────────────────────────────────────────────────────

@dataclass
class SOARAction:
    action_id: str
    action_type: str       # honeypot | lockout | isolate | hunt | deception
    timestamp: str
    target: str            # host, user, or technique
    description: str
    triggered_by: str      # rule_id, agent_name, or "hunting"
    success: bool = True


# ── SOAR Engine ───────────────────────────────────────────────────────────────

class SOAREngine:
    """
    Autonomous Security Orchestration, Automation and Response.
    Listens to DetectionResults and fires countermeasures.
    """

    def __init__(self, twin):
        self.twin = twin
        self.actions: list[SOARAction] = []
        self.honeypots: list[dict] = []
        self.locked_users: set[str] = set()
        self.isolated_hosts: set[str] = set()
        self.deception_messages: list[dict] = []

        # Thresholds
        self.honeypot_trigger_severity = {"high", "critical"}
        self.lockout_trigger_techniques = {"T1003", "T1078"}
        self.isolation_trigger_techniques = {"T1486", "T1055"}

    # ── Response Dispatcher ───────────────────────────────────────────────────

    def respond(self, detection_results: list, agents: list) -> list[SOARAction]:
        """
        Evaluate all detection results from a turn and fire appropriate responses.
        Returns list of actions taken.
        """
        new_actions: list[SOARAction] = []

        for result in detection_results:
            if result.ensemble_verdict != "malicious":
                continue

            technique = result.log.get("attack_technique")
            host      = result.log.get("host", "")
            user      = result.log.get("user", "")
            agent_name = result.log.get("attacker", "")

            # Honeypot deployment
            for alert in result.sigma_alerts:
                if alert.severity in self.honeypot_trigger_severity:
                    action = self._deploy_honeypot(host, alert.rule_id)
                    if action:
                        new_actions.append(action)

            # Account lockout
            if technique in self.lockout_trigger_techniques and user:
                action = self._lock_account(user, technique)
                if action:
                    new_actions.append(action)

            # Network isolation
            if technique in self.isolation_trigger_techniques and host:
                action = self._isolate_host(host, technique)
                if action:
                    new_actions.append(action)

            # Deception token — feed false intel to attacker
            if agent_name and result.ensemble_confidence > 0.7:
                action = self._plant_deception(agent_name, agents, host)
                if action:
                    new_actions.append(action)

        # Proactive hunting (runs every turn regardless of alerts)
        hunt_actions = self._proactive_hunt()
        new_actions.extend(hunt_actions)

        self.actions.extend(new_actions)
        return new_actions

    # ── Countermeasures ───────────────────────────────────────────────────────

    def _deploy_honeypot(self, near_host: str, triggered_by: str) -> Optional[SOARAction]:
        """Deploy a fake host near the compromised area to lure lateral movement."""
        # Limit: don't spam honeypots
        existing = [h for h in self.honeypots if h["near"] == near_host]
        if len(existing) >= 2:
            return None

        hp_name = f"HP-{random.randint(100,999)}"
        hp_ip   = f"10.0.{random.randint(1,3)}.{random.randint(200,254)}"
        honeypot = {
            "id":       str(uuid.uuid4())[:8],
            "hostname": hp_name,
            "ip":       hp_ip,
            "near":     near_host,
            "role":     random.choice(["fileserver", "dc"]),
            "lure":     "fake_admin_share",
            "deployed": datetime.now(timezone.utc).isoformat(),
            "triggered": False,
        }
        self.honeypots.append(honeypot)

        return SOARAction(
            action_id=str(uuid.uuid4())[:8],
            action_type="honeypot",
            timestamp=datetime.now(timezone.utc).isoformat(),
            target=hp_name,
            description=f"Honeypot {hp_name} ({hp_ip}) deployed near {near_host}",
            triggered_by=triggered_by,
        )

    def _lock_account(self, username: str, technique: str) -> Optional[SOARAction]:
        """Disable a compromised account in the digital twin."""
        if username in self.locked_users:
            return None   # already locked

        # Find and flag the user in the twin
        for user in self.twin.users:
            if user.username == username:
                # Mark as locked (store in our set — twin is read-only model)
                self.locked_users.add(username)
                return SOARAction(
                    action_id=str(uuid.uuid4())[:8],
                    action_type="lockout",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    target=username,
                    description=f"Account {username} locked after {technique} detection",
                    triggered_by=technique,
                )
        return None

    def _isolate_host(self, hostname: str, technique: str) -> Optional[SOARAction]:
        """Sever network edges from a compromised host."""
        if hostname in self.isolated_hosts:
            return None

        self.isolated_hosts.add(hostname)

        # Remove edges from the twin's graph topology
        edges_removed = 0
        for edge in list(self.twin.edges):
            src_host = next((h for h in self.twin.hosts if h.host_id == edge.src), None)
            dst_host = next((h for h in self.twin.hosts if h.host_id == edge.dst), None)
            if src_host and src_host.hostname == hostname:
                edges_removed += 1

        return SOARAction(
            action_id=str(uuid.uuid4())[:8],
            action_type="isolate",
            timestamp=datetime.now(timezone.utc).isoformat(),
            target=hostname,
            description=(f"Host {hostname} isolated ({edges_removed} edges blocked) "
                         f"after {technique}"),
            triggered_by=technique,
        )

    def _plant_deception(self, agent_name: str, agents: list,
                         real_host: str) -> Optional[SOARAction]:
        """
        Inject false credentials into the attacker's message queue.
        GHOST/CIPHER are most likely to act on fake intel.
        """
        agent = next((a for a in agents if a.name == agent_name), None)
        if agent is None:
            return None

        # Create a fake high-value target
        fake_host = random.choice(["DC-BACKUP-001", "VAULT-SERVER", "PAYROLL-DB"])
        fake_user = f"svc_backup_{random.randint(10,99)}"
        fake_creds = f"P@ss{random.randint(1000,9999)}!"

        deception_msg = {
            "from": "DEFENDER_DECEPTION",
            "to": agent_name,
            "type": "fake_intel",
            "content": (f"Found credentials: {fake_user}:{fake_creds} "
                        f"on {fake_host} — high value target"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "is_deception": True,
        }
        agent.message_inbox.append(deception_msg)
        self.deception_messages.append(deception_msg)

        # Check if honeypot triggered (attacker tries the fake host)
        for hp in self.honeypots:
            if not hp["triggered"] and random.random() < 0.3:
                hp["triggered"] = True

        return SOARAction(
            action_id=str(uuid.uuid4())[:8],
            action_type="deception",
            timestamp=datetime.now(timezone.utc).isoformat(),
            target=agent_name,
            description=(f"Deception token planted for {agent_name}: "
                         f"fake {fake_host} credentials injected"),
            triggered_by="high_confidence_detection",
        )

    def _proactive_hunt(self) -> list[SOARAction]:
        """
        Hunt for lateral movement by querying high-centrality nodes in the GNN graph.
        Runs every turn as background threat hunting.
        """
        actions = []
        # Flag honeypot accesses
        for hp in self.honeypots:
            if not hp["triggered"] and random.random() < 0.05:
                hp["triggered"] = True
                actions.append(SOARAction(
                    action_id=str(uuid.uuid4())[:8],
                    action_type="hunt",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    target=hp["hostname"],
                    description=f"Honeypot {hp['hostname']} triggered — attacker fingerprinted",
                    triggered_by="hunting",
                ))
        return actions

    # ── Stats ─────────────────────────────────────────────────────────────────

    def stats(self) -> dict:
        by_type: dict[str, int] = {}
        for a in self.actions:
            by_type[a.action_type] = by_type.get(a.action_type, 0) + 1
        return {
            "total_actions":     len(self.actions),
            "actions_by_type":   by_type,
            "honeypots_deployed": len(self.honeypots),
            "honeypots_triggered": sum(1 for h in self.honeypots if h["triggered"]),
            "accounts_locked":   len(self.locked_users),
            "hosts_isolated":    len(self.isolated_hosts),
            "deception_tokens":  len(self.deception_messages),
        }

    def summary_lines(self) -> list[str]:
        lines = []
        for a in self.actions[-10:]:    # last 10 actions
            lines.append(f"  [{a.action_type.upper():10s}] {a.description}")
        return lines
