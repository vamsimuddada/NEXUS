"""
NEXUS — Layer 4: Cognitive Evolution Engine
After every battle the defender analyses what it missed and improves itself.

Three mechanisms:
  1. Rule Rewriter      — generates new SIGMA rules for missed techniques
  2. Model Updater      — triggers incremental GNN retraining on new labelled data
  3. Psychology Memory  — stores per-attacker behavioural fingerprints in SQLite
                          and optionally indexes them in ChromaDB

ARM64-safe: pure Python + sklearn + optional ChromaDB.
"""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from defender.sigma.sigma_engine import SigmaEngine, SigmaRule
from defender.gnn.graph_detector import GraphAnomalyDetector


# ─────────────────────────────────────────────────────────────────────────────
# 1. SIGMA Rule Rewriter
# ─────────────────────────────────────────────────────────────────────────────

# Maps MITRE technique → default rule template when LLM is unavailable
_TECHNIQUE_TEMPLATES: dict[str, dict] = {
    "T1078": {
        "title": "Auto: Valid Account Abuse Detected",
        "severity": "high",
        "conditions": [
            {"field": "attack_technique", "operator": "eq",  "value": "T1078"},
            {"field": "event_id",         "operator": "in",  "value": [4624, 4648]},
        ],
    },
    "T1021": {
        "title": "Auto: Remote Service Lateral Movement",
        "severity": "high",
        "conditions": [
            {"field": "attack_technique", "operator": "eq", "value": "T1021"},
        ],
    },
    "T1059": {
        "title": "Auto: Scripting Interpreter Execution",
        "severity": "medium",
        "conditions": [
            {"field": "attack_technique", "operator": "eq", "value": "T1059"},
            {"field": "event_id",         "operator": "eq", "value": 4688},
        ],
    },
    "T1055": {
        "title": "Auto: Process Injection",
        "severity": "critical",
        "conditions": [
            {"field": "attack_technique", "operator": "eq", "value": "T1055"},
            {"field": "event_id",         "operator": "eq", "value": 10},
        ],
    },
    "T1083": {
        "title": "Auto: File and Directory Discovery",
        "severity": "low",
        "conditions": [
            {"field": "attack_technique", "operator": "eq", "value": "T1083"},
        ],
    },
    "T1003": {
        "title": "Auto: Credential Dumping via LSASS",
        "severity": "critical",
        "conditions": [
            {"field": "attack_technique", "operator": "eq", "value": "T1003"},
            {"field": "event_id",         "operator": "in", "value": [4662, 4663]},
        ],
    },
    "T1486": {
        "title": "Auto: Ransomware — Mass Encryption",
        "severity": "critical",
        "conditions": [
            {"field": "attack_technique", "operator": "eq", "value": "T1486"},
        ],
    },
    "T1071": {
        "title": "Auto: C2 Beacon via Application Layer",
        "severity": "high",
        "conditions": [
            {"field": "attack_technique", "operator": "eq", "value": "T1071"},
            {"field": "event_id",         "operator": "eq", "value": 5156},
        ],
    },
}


class RuleRewriter:
    """
    Analyses missed attack techniques and generates new SIGMA rules.
    Uses the Anthropic API when available; falls back to templates.
    """

    def __init__(self, sigma: SigmaEngine, provider: str = "anthropic"):
        self.sigma = sigma
        self.provider = provider
        self._client = None
        self._init_client()
        self.rules_generated: list[SigmaRule] = []

    def _init_client(self):
        if self.provider == "anthropic":
            try:
                import anthropic
                key = os.getenv("ANTHROPIC_API_KEY", "")
                if key and key != "your-anthropic-key-here":
                    self._client = anthropic.Anthropic(api_key=key)
            except ImportError:
                pass

        elif self.provider == "gemini":
            try:
                from core.gemini_provider import get_gemini
                prov = get_gemini()
                if prov.available:
                    self._client = prov
            except Exception:
                pass

        elif self.provider == "ollama":
            try:
                from core.ollama_provider import get_ollama
                prov = get_ollama()
                if prov.available:
                    self._client = prov
            except Exception:
                pass

    def rewrite_for_missed(self, missed_techniques: list[str],
                           sample_logs: list[dict]) -> list[SigmaRule]:
        """
        For each missed technique, generate a new SIGMA rule and add it to the engine.
        Returns the list of newly created rules.
        """
        new_rules: list[SigmaRule] = []
        existing_techniques = {r.technique for r in self.sigma.rules}

        for technique in missed_techniques:
            if technique in existing_techniques:
                # Rule exists but is producing false negatives — refine severity
                self._refine_existing(technique, sample_logs)
                # Check if we already have a broad catch-all variant for this technique
                broad_variants = [r for r in self.sigma.rules
                                  if r.auto_generated and r.technique == technique
                                  and len(r.conditions) == 1]
                if broad_variants:
                    # Already have a broad variant — skip
                    continue
                # Generate a broad variant (technique-only, no event_id constraint)
                # This catches attack logs where the event_id doesn't match templates
                broad_rule = SigmaRule(
                    rule_id=f"SIG-BROAD-{len(self.sigma.rules)+1:03d}",
                    title=f"Auto-Broad: {technique} any event",
                    description=f"Broad catch-all for {technique} — generated after repeated FNs",
                    severity="medium",
                    technique=technique,
                    conditions=[{"field": "attack_technique", "operator": "eq",
                                 "value": technique}],
                    auto_generated=True,
                )
                self.sigma.add_rule(broad_rule)
                new_rules.append(broad_rule)
                print(f"[Evolution/Rules] ✚ Broad rule: {broad_rule.rule_id} — {broad_rule.title}")
                continue

            rule = (self._llm_generate_rule(technique, sample_logs)
                    if self._client
                    else self._template_generate_rule(technique))

            if rule:
                self.sigma.add_rule(rule)
                self.rules_generated.append(rule)
                new_rules.append(rule)
                print(f"[Evolution/Rules] ✚ New rule: {rule.rule_id} — {rule.title}")

        return new_rules

    def _template_generate_rule(self, technique: str) -> Optional[SigmaRule]:
        tmpl = _TECHNIQUE_TEMPLATES.get(technique)
        if not tmpl:
            # Generic catch-all rule
            tmpl = {
                "title": f"Auto: {technique} Activity",
                "severity": "medium",
                "conditions": [
                    {"field": "attack_technique", "operator": "eq", "value": technique}
                ],
            }
        rule_id = f"SIG-AUTO-{len(self.sigma.rules)+1:03d}"
        return SigmaRule(
            rule_id=rule_id,
            title=tmpl["title"],
            description=f"Auto-generated by Evolution Engine for {technique}",
            severity=tmpl["severity"],
            technique=technique,
            conditions=tmpl["conditions"],
            auto_generated=True,
        )

    def _llm_generate_rule(self, technique: str,
                           sample_logs: list[dict]) -> Optional[SigmaRule]:
        """Ask Claude to generate a SIGMA rule for the missed technique."""
        samples = [l for l in sample_logs
                   if l.get("attack_technique") == technique][:3]
        sample_str = json.dumps(samples, indent=2) if samples else "No samples available"

        prompt = f"""You are a detection engineer writing SIGMA rules for a SOC.

A MITRE ATT&CK technique was MISSED by our current detection: {technique}

Sample log entries that triggered this technique:
{sample_str}

Generate a SIGMA-style detection rule as JSON with this exact schema:
{{
  "title": "short descriptive title",
  "severity": "low|medium|high|critical",
  "conditions": [
    {{"field": "field_name", "operator": "eq|in|contains|gte|regex", "value": "value_or_list"}}
  ]
}}

Available fields: event_id, host, user, department, is_admin, ip_src, ip_dst,
                  attack_technique, label, stealth_level

Respond with ONLY valid JSON. No markdown, no preamble."""

        try:
            from core.gemini_provider import GeminiProvider
            from core.ollama_provider import OllamaProvider
            if isinstance(self._client, (GeminiProvider, OllamaProvider)):
                raw = self._client.call(prompt, max_tokens=400)
            else:
                msg = self._client.messages.create(
                    model=os.getenv("NEXUS_LLM_MODEL", "claude-3-haiku-20240307"),
                    max_tokens=400,
                    messages=[{"role": "user", "content": prompt}],
                )
                raw = msg.content[0].text.strip()
            raw = raw.strip("```json").strip("```").strip()
            data = json.loads(raw)
            rule_id = f"SIG-LLM-{len(self.sigma.rules)+1:03d}"
            return SigmaRule(
                rule_id=rule_id,
                title=data.get("title", f"LLM: {technique}"),
                description=f"LLM-generated by Evolution Engine for {technique}",
                severity=data.get("severity", "medium"),
                technique=technique,
                conditions=data.get("conditions", []),
                auto_generated=True,
            )
        except Exception as e:
            print(f"[Evolution/Rules] LLM rule gen failed ({e}), using template")
            return self._template_generate_rule(technique)

    def _refine_existing(self, technique: str, sample_logs: list[dict]):
        """Bump severity of existing rules for repeatedly-missed techniques."""
        sev_order = ["low", "medium", "high", "critical"]
        for rule in self.sigma.rules:
            if rule.technique == technique and rule.hit_count == 0:
                idx = sev_order.index(rule.severity)
                if idx < len(sev_order) - 1:
                    rule.severity = sev_order[idx + 1]
                    print(f"[Evolution/Rules] ↑ Refined {rule.rule_id} severity → {rule.severity}")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Model Updater
# ─────────────────────────────────────────────────────────────────────────────

class ModelUpdater:
    """
    Feeds newly labelled logs from battles back into the GNN detector.
    Implements incremental learning so detection improves across simulations.
    """

    def __init__(self, gnn: GraphAnomalyDetector):
        self.gnn = gnn
        self.total_updates = 0
        self.logs_fed = 0

    def update(self, battle_logs: list[dict]) -> dict:
        """
        Ingest battle logs, retrain GNN incrementally.
        Returns stats about the update.
        """
        if len(battle_logs) < 10:
            return {"skipped": True, "reason": "not enough logs"}

        # Separate benign logs for incremental fit (anomaly detection trains on normal)
        benign = [l for l in battle_logs if l.get("label") == "benign"]
        malicious = [l for l in battle_logs if l.get("label") == "malicious"]

        self.gnn.partial_fit(benign)
        self.total_updates += 1
        self.logs_fed += len(battle_logs)

        print(f"[Evolution/Model] Update #{self.total_updates} — "
              f"benign={len(benign)}, malicious={len(malicious)}")

        return {
            "update_number": self.total_updates,
            "benign_fed": len(benign),
            "malicious_fed": len(malicious),
            "gnn_stats": self.gnn.graph_stats(),
        }


# ─────────────────────────────────────────────────────────────────────────────
# 3. Psychology Memory Store
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AttackerProfile:
    agent_name: str
    battles_seen: int = 0
    favourite_techniques: dict = field(default_factory=dict)   # technique → count
    preferred_targets: dict = field(default_factory=dict)      # host_role → count
    avg_stealth: float = 0.5
    detection_rate: float = 0.0
    phase_durations: dict = field(default_factory=dict)        # phase → avg_turns
    last_updated: str = ""
    notes: list[str] = field(default_factory=list)


class PsychologyMemory:
    """
    Stores and retrieves behavioural fingerprints for each attacker agent.

    SQLite is the durable source of truth. ChromaDB is an optional semantic
    index layered on top of it; if ChromaDB is missing or fails at runtime,
    all profile operations continue through SQLite.
    """

    def __init__(self, persist_path: Optional[str] = None):
        # Explicit test/custom paths are isolated from application-level env
        # settings. The normal application path can use documented env vars.
        explicit_path = persist_path is not None
        self.persist_path = Path(
            persist_path if explicit_path
            else os.getenv("NEXUS_PSYCHOLOGY_PATH", "data/psychology")
        )
        self.persist_path.mkdir(parents=True, exist_ok=True)
        self.profiles: dict[str, AttackerProfile] = {}
        self._chroma = None
        self._collection = None
        self._storage_backend = "sqlite"
        self._chroma_path = Path(
            os.getenv("NEXUS_CHROMA_PATH", str(self.persist_path / "chroma"))
            if not explicit_path else self.persist_path / "chroma"
        )
        self._sqlite_path = str(
            os.getenv("NEXUS_SQLITE_PATH", str(self.persist_path / "psychology.db"))
            if not explicit_path else self.persist_path / "psychology.db"
        )
        self._init_storage()

    def _init_storage(self):
        # SQLite is the durable source of truth and is always initialised.
        # ChromaDB is an optional semantic-search index layered on top of it.
        self._init_sqlite()

        # Use ChromaDB only after both its client and collection can be opened.
        try:
            import chromadb
            self._chroma_path.mkdir(parents=True, exist_ok=True)
            self._chroma = chromadb.PersistentClient(path=str(self._chroma_path))
            self._collection = self._chroma.get_or_create_collection("attacker_profiles")
            # Opening a collection is not enough to prove that the backend is
            # usable.  count() is a lightweight read that validates the handle.
            self._collection.count()
            self._storage_backend = "chromadb"
            print("[Memory] ChromaDB initialised ✓")
        except Exception as exc:
            self._chroma = None
            self._collection = None
            self._storage_backend = "sqlite"
            print("[Memory] ChromaDB unavailable — using SQLite fallback")
            # Keep the diagnostic available without making normal runs noisy.
            if os.getenv("NEXUS_DEBUG_MEMORY"):
                print(f"[Memory] ChromaDB reason: {exc}")

        self._load_profiles_from_sqlite()

    def _init_sqlite(self):
        Path(self._sqlite_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self._sqlite_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                agent_name TEXT PRIMARY KEY,
                profile_json TEXT,
                updated_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS battle_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT,
                battle_id TEXT,
                log_json TEXT,
                timestamp TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _load_profiles_from_sqlite(self):
        """Restore structured profiles so memory survives process restarts."""
        conn = sqlite3.connect(self._sqlite_path)
        rows = conn.execute("SELECT profile_json FROM profiles").fetchall()
        conn.close()
        for (profile_json,) in rows:
            try:
                data = json.loads(profile_json)
                profile = AttackerProfile(**data)
                self.profiles[profile.agent_name] = profile
            except (TypeError, ValueError, json.JSONDecodeError) as exc:
                if os.getenv("NEXUS_DEBUG_MEMORY"):
                    print(f"[Memory] Ignoring invalid stored profile: {exc}")

    # ── Ingest battle data ────────────────────────────────────────────────────

    def ingest_battle(self, agent_name: str, agent_logs: list[dict],
                      agent_status: dict, battle_id: str):
        """Update the profile for an agent based on their battle logs."""
        profile = self.profiles.get(agent_name, AttackerProfile(agent_name=agent_name))
        profile.battles_seen += 1
        profile.last_updated = datetime.now(timezone.utc).isoformat()

        # Technique frequency
        for log in agent_logs:
            tech = log.get("attack_technique")
            if tech:
                profile.favourite_techniques[tech] = (
                    profile.favourite_techniques.get(tech, 0) + 1
                )
            host = log.get("host", "")
            role = "dc" if "DC" in host else "ws" if "WS" in host else "server"
            profile.preferred_targets[role] = (
                profile.preferred_targets.get(role, 0) + 1
            )

        # Running average stealth
        stealths = {"low": 0.2, "medium": 0.5, "high": 0.9}
        stealth_scores = [stealths.get(l.get("stealth_level", "medium"), 0.5)
                          for l in agent_logs]
        if stealth_scores:
            alpha = 0.3  # EMA weight
            profile.avg_stealth = (alpha * sum(stealth_scores) / len(stealth_scores)
                                   + (1 - alpha) * profile.avg_stealth)

        # Detection rate (from agent status — not tracked per-log yet)
        profile.notes.append(
            f"Battle {battle_id}: phase={agent_status.get('phase')} "
            f"hosts={len(agent_status.get('compromised_hosts', []))}"
        )
        profile.notes = profile.notes[-20:]   # keep last 20 notes

        self.profiles[agent_name] = profile
        self._persist(profile, agent_logs, battle_id)

    def _persist(self, profile: AttackerProfile, logs: list[dict], battle_id: str):
        # Always write the structured record first.  This guarantees that a
        # ChromaDB failure cannot lose memory and gives us a safe fallback.
        self._persist_sqlite(profile, logs, battle_id)

        # ChromaDB is an optional index, not the only copy of the profile.
        if self._storage_backend == "chromadb" and self._collection is not None:
            self._persist_chroma(profile, logs, battle_id)

    def _persist_chroma(self, profile: AttackerProfile, logs: list[dict], battle_id: str):
        """Store profile summary as a ChromaDB document for semantic search."""
        doc = (
            f"Agent: {profile.agent_name}. "
            f"Techniques: {', '.join(profile.favourite_techniques.keys())}. "
            f"Targets: {', '.join(profile.preferred_targets.keys())}. "
            f"Avg stealth: {profile.avg_stealth:.2f}. "
            f"Battles: {profile.battles_seen}."
        )
        meta = {
            "agent": profile.agent_name,
            "battles": profile.battles_seen,
            "avg_stealth": round(profile.avg_stealth, 3),
            "top_technique": max(profile.favourite_techniques,
                                 key=profile.favourite_techniques.get,
                                 default="none"),
        }
        doc_id = f"{profile.agent_name}_{battle_id}"
        try:
            self._collection.upsert(
                ids=[doc_id],
                documents=[doc],
                metadatas=[meta],
            )
        except Exception as e:
            print(f"[Memory] ChromaDB upsert failed: {e}")
            self._disable_chroma()

    def _disable_chroma(self):
        """Switch to SQLite after a ChromaDB runtime failure."""
        self._chroma = None
        self._collection = None
        self._storage_backend = "sqlite"
        print("[Memory] ChromaDB disabled — continuing with SQLite fallback")

    def _persist_sqlite(self, profile: AttackerProfile, logs: list[dict], battle_id: str):
        conn = sqlite3.connect(self._sqlite_path)
        conn.execute(
            "INSERT OR REPLACE INTO profiles VALUES (?, ?, ?)",
            (profile.agent_name, json.dumps(profile.__dict__),
             profile.last_updated)
        )
        for log in logs:
            conn.execute(
                "INSERT INTO battle_logs VALUES (NULL, ?, ?, ?, ?)",
                (profile.agent_name, battle_id,
                 json.dumps(log), datetime.now(timezone.utc).isoformat())
            )
        conn.commit()
        conn.close()

    # ── Query ─────────────────────────────────────────────────────────────────

    def get_profile(self, agent_name: str) -> Optional[AttackerProfile]:
        return self.profiles.get(agent_name)

    def predict_next_technique(self, agent_name: str) -> str:
        """Predict the most likely next technique based on historical frequency."""
        profile = self.profiles.get(agent_name)
        if not profile or not profile.favourite_techniques:
            return "T1078"   # default
        return max(profile.favourite_techniques,
                   key=profile.favourite_techniques.get)

    def get_stealth_estimate(self, agent_name: str) -> float:
        profile = self.profiles.get(agent_name)
        return profile.avg_stealth if profile else 0.5

    def similarity_search(self, query: str, top_k: int = 3) -> list[dict]:
        """Semantic search over agent profiles (ChromaDB only)."""
        if self._storage_backend != "chromadb" or self._collection is None:
            return self._sqlite_profile_results()
        try:
            count = self._collection.count()
            if count == 0:
                # Profiles may predate ChromaDB or have been written while it
                # was unavailable. Do not hide those records from callers.
                return self._sqlite_profile_results()
            results = self._collection.query(
                query_texts=[query], n_results=min(max(top_k, 1), count)
            )
            return [
                {"agent": meta.get("agent", ""), "document": doc, "metadata": meta}
                for doc, meta in zip(
                    results["documents"][0], results["metadatas"][0]
                )
            ]
        except Exception as e:
            print(f"[Memory] Search failed: {e}")
            self._disable_chroma()
            return self._sqlite_profile_results()

    def _sqlite_profile_results(self) -> list[dict]:
        """Return the structured profiles used by the SQLite fallback."""
        return [{"agent": k, "profile": v.__dict__}
                for k, v in self.profiles.items()]

    def summary(self) -> dict:
        return {
            "profiles_stored": len(self.profiles),
            "storage_backend": self._storage_backend,
            "agents": [
                {
                    "name": p.agent_name,
                    "battles": p.battles_seen,
                    "top_technique": max(p.favourite_techniques,
                                         key=p.favourite_techniques.get,
                                         default="none"),
                    "avg_stealth": round(p.avg_stealth, 2),
                }
                for p in self.profiles.values()
            ],
        }


# ─────────────────────────────────────────────────────────────────────────────
# Master Evolution Engine
# ─────────────────────────────────────────────────────────────────────────────

class CognitiveEvolutionEngine:
    """
    Orchestrates all three evolution mechanisms after a battle.
    Call .evolve(battle_report, defender) after each simulation run.
    """

    def __init__(self, defender, provider: str = "anthropic"):
        self.rule_rewriter = RuleRewriter(defender.sigma, provider)
        self.model_updater = ModelUpdater(defender.gnn)
        self.memory = PsychologyMemory()
        self.evolution_count = 0

    def evolve(self, battle_report, defender) -> dict:
        """
        Run all three evolution steps from a completed battle report.
        Returns a summary of changes made.
        """
        self.evolution_count += 1
        print(f"\n[Evolution] ══ Cycle {self.evolution_count} ══")

        all_logs = battle_report.attacker_logs + battle_report.normal_logs

        # 1. Rule rewriting
        missed = battle_report.missed_techniques
        new_rules = []
        if missed:
            print(f"[Evolution] Missed techniques: {missed}")
            new_rules = self.rule_rewriter.rewrite_for_missed(
                missed, battle_report.attacker_logs
            )

        # 2. Model update
        model_stats = self.model_updater.update(all_logs)

        # 3. Psychology memory
        agent_logs_by_name: dict[str, list[dict]] = {}
        for log in battle_report.attacker_logs:
            name = log.get("attacker", "UNKNOWN")
            agent_logs_by_name.setdefault(name, []).append(log)

        for status in battle_report.agent_statuses:
            name = status["agent"]
            self.memory.ingest_battle(
                agent_name=name,
                agent_logs=agent_logs_by_name.get(name, []),
                agent_status=status,
                battle_id=battle_report.battle_id,
            )

        mem_summary = self.memory.summary()
        print(f"[Evolution] Memory: {mem_summary['profiles_stored']} agent profiles stored")

        # Wire memory reference into defender so profile context aids future detections
        if not hasattr(defender, "psychology_memory") or defender.psychology_memory is None:
            defender.psychology_memory = self.memory

        result = {
            "evolution_cycle": self.evolution_count,
            "new_sigma_rules": [r.rule_id for r in new_rules],
            "model_update": model_stats,
            "memory": mem_summary,
            "total_sigma_rules": len(defender.sigma.rules),
        }
        print(f"[Evolution] ✓ Cycle complete — "
              f"rules={result['total_sigma_rules']} "
              f"new={len(new_rules)}")
        return result
