"""
NEXUS — Layer 2: Base Attacker Agent
All six attacker personas inherit from this class.
Uses the Anthropic API for LLM-driven decision making.
ARM64-safe: pure Python, no native deps.
"""

from __future__ import annotations

import json
import os
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

# ── Memory entry ──────────────────────────────────────────────────────────────

@dataclass
class MemoryEntry:
    timestamp: str
    action: str
    technique: str
    success: bool
    target_host: str
    notes: str = ""


# ── Campaign state ────────────────────────────────────────────────────────────

@dataclass
class CampaignState:
    phase: str = "reconnaissance"       # recon → initial_access → execution →
                                        # lateral_movement → exfiltration
    compromised_hosts: list[str] = field(default_factory=list)
    compromised_users: list[str] = field(default_factory=list)
    gathered_intel: list[str] = field(default_factory=list)
    detected: bool = False
    turn: int = 0


# ── Base Agent ────────────────────────────────────────────────────────────────

class BaseAttackerAgent(ABC):
    """
    Abstract base for all NEXUS attacker personas.
    Subclasses define: name, personality_prompt, preferred_techniques.
    """

    # Override in subclass
    name: str = "UNKNOWN"
    personality_prompt: str = "You are a generic attacker."
    preferred_techniques: list[str] = []
    elo: int = 1000

    def __init__(self, twin, llm_provider: str = "anthropic"):
        """
        Args:
            twin: DigitalTwin instance (the environment)
            llm_provider: 'anthropic' | 'openai' | 'mock'
        """
        self.twin = twin
        self.llm_provider = llm_provider
        self.memory: list[MemoryEntry] = []
        self.state = CampaignState()
        self.message_inbox: list[dict] = []   # inter-agent comms
        self.logs_generated: list[dict] = []  # attack logs this agent produced

    # ── LLM Decision ─────────────────────────────────────────────────────────

    def decide_next_action(self) -> dict:
        """
        Ask the LLM what to do next, given current campaign state and memory.
        Returns a structured action dict.
        """
        context = self._build_context()
        recent_mem = [{"technique": m.technique, "host": m.target_host, "ok": m.success}
                      for m in self.memory[-3:]]
        prompt = (
            f"{self.personality_prompt}\n\n"
            f"Turn:{self.state.turn} Phase:{self.state.phase} "
            f"Compromised:{self.state.compromised_hosts}\n"
            f"Recent actions:{json.dumps(recent_mem)}\n"
            f"Hosts:{len(self.twin.hosts)} Users:{len(self.twin.users)}\n"
            f"Allowed techniques:{','.join(self.preferred_techniques or ['T1078'])}\n\n"
            f"Reply ONLY with valid JSON:\n"
            f'{{"action":"...","technique_id":"T1078","target_host_role":"dc|fileserver|workstation|webserver|db",'
            f'"rationale":"1 sentence","stealth_level":"low|medium|high"}}'
        )
        # Enrich prompt with semantic memory
        try:
            from integrations.vector_memory import get_memory
            mem = get_memory(self.name)
            if mem.count() > 0:
                similar = mem.search(
                    f"technique {' '.join(self.preferred_techniques[:2])} detected",
                    top_k=2, category="attack"
                )
                if similar:
                    mem_ctx = " | ".join(s["content"][:80] for s in similar)
                    prompt += f"\nMemory context:{mem_ctx}"
        except Exception:
            pass
        raw = self._call_llm(prompt)
        return self._parse_action(raw)

    def _call_llm(self, prompt: str) -> str:
        """Call the configured LLM provider."""
        if self.llm_provider == "mock":
            return self._mock_response()

        if self.llm_provider == "anthropic":
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                msg = client.messages.create(
                    model=os.getenv("NEXUS_LLM_MODEL", "claude-3-haiku-20240307"),
                    max_tokens=512,
                    messages=[{"role": "user", "content": prompt}],
                )
                return msg.content[0].text
            except Exception as e:
                print(f"[{self.name}] Anthropic API error: {e}. Falling back to mock.")
                return self._mock_response()

        if self.llm_provider == "gemini":
            try:
                from core.gemini_provider import get_gemini
                provider = get_gemini()
                if not provider.available:
                    return self._mock_response()
                result = provider.call(prompt, max_tokens=512)
                return result if result else self._mock_response()
            except Exception as e:
                print(f"[{self.name}] Gemini API error: {e}. Falling back to mock.")
                return self._mock_response()

        if self.llm_provider == "ollama":
            try:
                from core.ollama_provider import get_ollama
                provider = get_ollama()
                if not provider.available:
                    return self._mock_response()
                result = provider.call(prompt, max_tokens=128)
                return result if result else self._mock_response()
            except Exception as e:
                print(f"[{self.name}] Ollama error: {e}. Falling back to mock.")
                return self._mock_response()

        if self.llm_provider == "openai":
            try:
                import openai
                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=512,
                )
                return resp.choices[0].message.content
            except Exception as e:
                print(f"[{self.name}] OpenAI API error: {e}. Falling back to mock.")
                return self._mock_response()

        return self._mock_response()

    def _mock_response(self) -> str:
        """Fallback deterministic response — no API key needed."""
        technique = random.choice(self.preferred_techniques or ["T1078"])
        role = random.choice(["dc", "fileserver", "workstation"])
        return json.dumps({
            "action": f"Executing {technique} via mock decision engine",
            "technique_id": technique,
            "target_host_role": role,
            "rationale": "Mock fallback — no LLM key configured.",
            "stealth_level": "medium",
        })

    def _parse_action(self, raw: str) -> dict:
        """Safely parse and constrain an LLM action to this persona's scope."""
        try:
            # Strip markdown fences if present
            clean = raw.strip().strip("```json").strip("```").strip()
            action = json.loads(clean)
        except Exception:
            action = {}
        return self._normalise_action(action)

    def _normalise_action(self, action: object) -> dict:
        """Keep LLM output inside the simulated persona's supported action set."""
        allowed_techniques = self.preferred_techniques or ["T1078"]
        if not isinstance(action, dict):
            action = {}

        requested = str(action.get("technique_id", "")).strip().upper()
        technique = (requested if requested in allowed_techniques
                     else random.choice(allowed_techniques))

        role = str(action.get("target_host_role", "workstation")).lower()
        valid_roles = {"dc", "fileserver", "workstation", "webserver", "db"}
        if role not in valid_roles:
            role = "workstation"

        stealth = str(action.get("stealth_level", "medium")).lower()
        if stealth not in {"low", "medium", "high"}:
            stealth = "medium"

        rationale = str(action.get("rationale", "")).strip()
        if requested and requested != technique:
            rationale = (rationale + " ").strip() + (
                f"Technique {requested} was outside this persona's supported set; "
                f"using {technique}."
            )

        return {
            "action": str(action.get("action", "fallback_recon")).strip() or "fallback_recon",
            "technique_id": technique,
            "target_host_role": role,
            "rationale": rationale or "Validated attacker action.",
            "stealth_level": stealth,
        }

    def _build_context(self) -> str:
        return f"Agent {self.name} | Turn {self.state.turn} | Phase {self.state.phase}"

    # ── Execute Action ────────────────────────────────────────────────────────

    def execute_action(self, action: dict) -> dict:
        """
        Execute the decided action against the digital twin.
        Returns the generated attack log entry.
        """
        # Coalition hooks and tests can call execute_action directly, so apply
        # the same validation used for LLM output at this boundary as well.
        action = self._normalise_action(action)
        role = action["target_host_role"]
        candidates = [h for h in self.twin.hosts if h.role == role]
        target_host = random.choice(candidates) if candidates else random.choice(self.twin.hosts)
        user = random.choice(self.twin.users)

        log = self.twin.generate_attack_log(
            technique_id=action["technique_id"],
            attacker_name=self.name,
            user=user,
            target_host=target_host,
        )
        log["stealth_level"] = action.get("stealth_level", "medium")
        log["agent_rationale"] = action.get("rationale", "")

        self.logs_generated.append(log)

        # Store in vector memory
        try:
            from integrations.vector_memory import get_memory
            mem = get_memory(self.name)
            detected = log.get("detected", False)
            mem.store_attack(
                technique=action.get("technique_id", ""),
                host=target_host.hostname,
                stealth=action.get("stealth_level", "medium"),
                detected=bool(detected),
                rationale=action.get("rationale", ""),
            )
        except Exception:
            pass

        # Update campaign state
        self.state.turn += 1
        if target_host.hostname not in self.state.compromised_hosts:
            self.state.compromised_hosts.append(target_host.hostname)
        self._advance_phase()

        # Record memory
        self.memory.append(MemoryEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            action=action.get("action", ""),
            technique=action.get("technique_id", ""),
            success=True,
            target_host=target_host.hostname,
            notes=action.get("rationale", ""),
        ))

        return log

    def _advance_phase(self):
        """Simple phase progression based on turn count."""
        phases = ["reconnaissance", "initial_access", "execution",
                  "lateral_movement", "exfiltration"]
        idx = phases.index(self.state.phase)
        if self.state.turn % 3 == 0 and idx < len(phases) - 1:
            self.state.phase = phases[idx + 1]

    # ── Inter-Agent Communication ─────────────────────────────────────────────

    def send_message(self, recipient: "BaseAttackerAgent", content: str,
                     msg_type: str = "intel"):
        """Send a message to another attacker agent."""
        msg = {
            "from": self.name,
            "to": recipient.name,
            "type": msg_type,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        recipient.message_inbox.append(msg)

    def broadcast(self, agents: list["BaseAttackerAgent"], content: str,
                  msg_type: str = "intel"):
        """Broadcast a message to all other agents."""
        for agent in agents:
            if agent.name != self.name:
                self.send_message(agent, content, msg_type)

    # ── Abstract interface ────────────────────────────────────────────────────

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return this agent's full system/personality prompt."""
        ...

    # ── Utility ───────────────────────────────────────────────────────────────

    def run_turn(self) -> dict:
        """One full turn: decide → execute → return log."""
        action = self.decide_next_action()
        log = self.execute_action(action)
        return log

    def status(self) -> dict:
        return {
            "agent": self.name,
            "elo": self.elo,
            "turn": self.state.turn,
            "phase": self.state.phase,
            "compromised_hosts": self.state.compromised_hosts,
            "logs_generated": len(self.logs_generated),
        }
