"""
NEXUS — Attacker Coalition Engine
Agents read each other's messages and genuinely alter their strategy.

Rules:
  CIPHER broadcasts access → VIPER/KRAKEN/NOVA switch target to the sold host
  NOVA shares threshold    → all agents adjust stealth to stay below it
  VIPER shares intel       → GHOST/CIPHER prioritise the flagged user/host
  KRAKEN detonates         → HYDRA amplifies with defacement on same host
  GHOST leaks credentials  → CIPHER immediately re-sells them
  Any agent detected       → remaining agents raise stealth level one tier
"""

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from attackers.base_agent import BaseAttackerAgent


# ── Stealth escalation ────────────────────────────────────────────────────────

_STEALTH_UP = {"low": "medium", "medium": "high", "high": "high"}


def _stealth_up(agent: "BaseAttackerAgent"):
    """Raise agent's next action stealth by one tier."""
    # Stored as a preferred override for the next turn
    if not hasattr(agent, "_stealth_override"):
        agent._stealth_override = None
    current = agent._stealth_override or "medium"
    agent._stealth_override = _STEALTH_UP.get(current, "high")


# ── Message processors ────────────────────────────────────────────────────────

def process_coalition_messages(agents: list["BaseAttackerAgent"],
                                twin) -> dict[str, list[str]]:
    """
    Read every agent's inbox and apply coalition strategy changes.
    Returns a dict of agent_name → list of actions taken (for logging).
    """
    actions: dict[str, list[str]] = {a.name: [] for a in agents}
    agent_map = {a.name: a for a in agents}

    for agent in agents:
        for msg in list(agent.message_inbox):
            sender   = msg.get("from", "")
            msg_type = msg.get("type", "")
            content  = msg.get("content", "")

            # ── CIPHER access sale → pivot target ────────────────────────────
            if msg_type == "access_sale" and sender == "CIPHER":
                # Extract host names from content
                hosts_in_msg = [
                    h.hostname for h in twin.hosts
                    if h.hostname in content
                ]
                if hosts_in_msg and agent.name in ("VIPER", "KRAKEN", "NOVA"):
                    # Override next target to the sold host
                    agent._target_override = hosts_in_msg[0]
                    actions[agent.name].append(
                        f"Pivoting to CIPHER's sold host: {hosts_in_msg[0]}"
                    )

            # ── NOVA threshold intel → stealth adjustment ─────────────────────
            if msg_type == "intel" and sender == "NOVA" and "threshold" in content.lower():
                # Parse estimated threshold from message if possible
                import re
                match = re.search(r"threshold.*?([0-9]\.[0-9]+)", content)
                if match:
                    est = float(match.group(1))
                    agent._nova_threshold_hint = est
                    # Agents with high stealth already don't need to change
                    if agent.name not in ("NOVA",):
                        _stealth_up(agent)
                        actions[agent.name].append(
                            f"Raising stealth — NOVA reports threshold≈{est:.3f}"
                        )

            # ── VIPER intel → target prioritisation ───────────────────────────
            if msg_type == "intel" and sender == "VIPER":
                if agent.name in ("GHOST", "CIPHER"):
                    # Try to find a host mentioned
                    for h in twin.hosts:
                        if h.hostname in content:
                            agent._target_override = h.hostname
                            actions[agent.name].append(
                                f"VIPER intel: prioritising {h.hostname}"
                            )
                            break

            # ── KRAKEN detonation → HYDRA amplifies ──────────────────────────
            if msg_type == "intel" and sender == "KRAKEN" and "encrypt" in content.lower():
                if agent.name == "HYDRA":
                    # HYDRA targets the same host for defacement
                    for h in twin.hosts:
                        if h.hostname in content:
                            agent._target_override = h.hostname
                            actions[agent.name].append(
                                f"Amplifying KRAKEN: defacing {h.hostname}"
                            )
                            break

            # ── GHOST leaks creds → CIPHER re-sells ──────────────────────────
            if msg_type == "intel" and sender == "GHOST" and "cred" in content.lower():
                if agent.name == "CIPHER":
                    agent._resell_flag = True
                    actions[agent.name].append("GHOST leak received — queued for resale")

            # ── Detection alert → all raise stealth ───────────────────────────
            if msg_type == "detection_alert":
                _stealth_up(agent)
                actions[agent.name].append(
                    f"Detection alert from {sender} — raising stealth"
                )

        # Clear processed messages
        agent.message_inbox = []

    return actions


def broadcast_detection_alert(detected_agent: "BaseAttackerAgent",
                               all_agents: list["BaseAttackerAgent"]):
    """When an agent is detected, warn the rest of the council."""
    for other in all_agents:
        if other.name != detected_agent.name:
            other.message_inbox.append({
                "from":      detected_agent.name,
                "to":        other.name,
                "type":      "detection_alert",
                "content":   f"{detected_agent.name} was detected — raise stealth",
                "timestamp": "",
            })


def nova_broadcast_threshold(nova_agent: "BaseAttackerAgent",
                              all_agents: list["BaseAttackerAgent"],
                              threshold_estimate: float):
    """NOVA shares its learned threshold with the council."""
    for other in all_agents:
        if other.name != "NOVA":
            other.message_inbox.append({
                "from":    "NOVA",
                "to":      other.name,
                "type":    "intel",
                "content": f"Estimated detection threshold ≈ {threshold_estimate:.4f}. "
                           f"Keep GNN score below this value.",
                "timestamp": "",
            })


def apply_target_override(agent: "BaseAttackerAgent", twin) -> dict | None:
    """
    If the agent has a pending target override (from coalition intel),
    return a pre-built action dict aimed at that host.
    Returns None if no override pending.
    """
    override_host = getattr(agent, "_target_override", None)
    if not override_host:
        return None

    # Consume the override
    agent._target_override = None

    host = next((h for h in twin.hosts if h.hostname == override_host), None)
    if not host:
        return None

    technique = (agent.preferred_techniques[0]
                 if agent.preferred_techniques else "T1078")

    stealth = getattr(agent, "_stealth_override", None) or "medium"
    if hasattr(agent, "_stealth_override"):
        agent._stealth_override = None   # consume

    return {
        "action":          f"Coalition-directed attack on {override_host}",
        "technique_id":    technique,
        "target_host_role": host.role,
        "rationale":       f"Coalition intel directed pivot to {override_host}",
        "stealth_level":   stealth,
        "_coalition_target": override_host,
    }


def apply_stealth_override(agent: "BaseAttackerAgent", action: dict) -> dict:
    """Apply any pending stealth override to an action dict."""
    override = getattr(agent, "_stealth_override", None)
    if override:
        action = dict(action)
        action["stealth_level"] = override
        agent._stealth_override = None
    return action
