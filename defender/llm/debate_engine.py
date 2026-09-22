"""
NEXUS — Layer 3 / Brain 3: LLM Debate Protocol
Two LLM "jurors" argue Prosecution (malicious) vs Defence (benign).
A Judge weighs the arguments and delivers a final verdict with confidence.

Falls back to a structured heuristic debate if no API key is present.
ARM64-safe: pure Python + Anthropic SDK.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Optional


# ── Debate Record ─────────────────────────────────────────────────────────────

@dataclass
class DebateRecord:
    log_summary: str
    prosecution_argument: str
    defence_argument: str
    judge_verdict: str          # "malicious" | "benign" | "uncertain"
    judge_confidence: float
    judge_reasoning: str
    used_llm: bool = True


# ── LLM Debate Engine ─────────────────────────────────────────────────────────

class LLMDebateEngine:
    """
    Three-role LLM debate:
      - Prosecution juror: argues the log is malicious
      - Defence juror:     argues the log is benign
      - Judge:             weighs both and delivers a structured verdict

    With an API key → uses Claude.
    Without          → structured heuristic debate (no API needed).
    """

    def __init__(self, provider: str = "anthropic"):
        self.provider = provider
        self._client = None
        self._init_client()
        self.debate_log: list[DebateRecord] = []

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

    def _call(self, prompt: str, max_tokens: int = 300) -> str:
        if self._client is None:
            return ""
        try:
            if self.provider in ("gemini", "ollama"):
                result = self._client.call(prompt, max_tokens=max_tokens)
                return result.strip() if result else ""

            msg = self._client.messages.create(
                model=os.getenv("NEXUS_LLM_MODEL", "claude-3-haiku-20240307"),
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text.strip()
        except Exception as e:
            print(f"[LLMDebate] API error: {e}")
            return ""

    # ── Main Debate ───────────────────────────────────────────────────────────

    def evaluate(self, log: dict,
                 sigma_alerts: list,
                 gnn_score: float,
                 attacker_profile: dict | None = None) -> tuple[str, float]:
        """
        Run the full debate. Returns (verdict, confidence).
        attacker_profile: optional dict from PsychologyMemory.get_profile()
                          — boosts confidence when attacker's known patterns match
        """
        verdict, conf = (
            self._llm_debate(log, sigma_alerts, gnn_score)
            if self._client
            else self._heuristic_debate(log, sigma_alerts, gnn_score)
        )
        # Profile boost: if this technique matches the attacker's known top technique,
        # raise confidence by up to 0.10
        if attacker_profile and verdict == "malicious":
            technique = log.get("attack_technique", "")
            top_tech  = attacker_profile.get("top_technique", "")
            if technique and technique == top_tech:
                conf = min(0.95, conf + 0.08)
        return verdict, conf

    def _llm_debate(self, log: dict, sigma_alerts: list,
                    gnn_score: float) -> tuple[str, float]:
        """Full 3-way LLM debate."""
        sigma_summary = (f"{len(sigma_alerts)} SIGMA rules fired: "
                         + ", ".join(a.title for a in sigma_alerts[:3])
                         if sigma_alerts else "No SIGMA alerts")

        log_summary = (
            f"EventID={log.get('event_id')} | Host={log.get('host')} | "
            f"User={log.get('user')} | Admin={log.get('is_admin')} | "
            f"Technique={log.get('attack_technique', 'None')} | "
            f"SIGMA: {sigma_summary} | GNN score: {gnn_score:.2f}"
        )

        # ── Prosecution ───────────────────────────────────────────────────────
        prosecution_prompt = f"""You are the PROSECUTION analyst in a SOC investigation.
Your job: argue convincingly that this log entry IS MALICIOUS.
Cite the specific evidence. Be concise (2-3 sentences max).

Log: {log_summary}

Respond with ONLY your argument. No preamble."""

        prosecution = self._call(prosecution_prompt, max_tokens=150)
        if not prosecution:
            prosecution = self._heuristic_prosecution(log, sigma_alerts, gnn_score)

        # ── Defence ───────────────────────────────────────────────────────────
        defence_prompt = f"""You are the DEFENCE analyst in a SOC investigation.
Your job: argue convincingly that this log entry IS BENIGN (false positive).
Cite innocent explanations. Be concise (2-3 sentences max).

Log: {log_summary}
Prosecution argued: {prosecution}

Respond with ONLY your counter-argument. No preamble."""

        defence = self._call(defence_prompt, max_tokens=150)
        if not defence:
            defence = self._heuristic_defence(log, sigma_alerts, gnn_score)

        # ── Judge ─────────────────────────────────────────────────────────────
        judge_prompt = f"""You are the JUDGE in a SOC triage review.
Weigh both arguments and deliver a final verdict.

Log: {log_summary}
Prosecution: {prosecution}
Defence: {defence}

Respond with ONLY valid JSON (no markdown):
{{"verdict": "malicious"|"benign"|"uncertain", "confidence": 0.0-1.0, "reasoning": "one sentence"}}"""

        judge_raw = self._call(judge_prompt, max_tokens=120)
        verdict, confidence, reasoning = self._parse_judge(judge_raw)

        record = DebateRecord(
            log_summary=log_summary,
            prosecution_argument=prosecution,
            defence_argument=defence,
            judge_verdict=verdict,
            judge_confidence=confidence,
            judge_reasoning=reasoning,
            used_llm=True,
        )
        self.debate_log.append(record)
        return verdict, confidence

    def _parse_judge(self, raw: str) -> tuple[str, float, str]:
        try:
            clean = raw.strip().strip("```json").strip("```").strip()
            data = json.loads(clean)
            verdict = data.get("verdict", "uncertain")
            conf = float(data.get("confidence", 0.5))
            reasoning = data.get("reasoning", "")
            if verdict not in ("malicious", "benign", "uncertain"):
                verdict = "uncertain"
            return verdict, conf, reasoning
        except Exception:
            return "uncertain", 0.5, "JSON parse failed"

    # ── Heuristic Debate (no API key) ─────────────────────────────────────────

    def _heuristic_debate(self, log: dict, sigma_alerts: list,
                          gnn_score: float) -> tuple[str, float]:
        """
        Structured rule-based debate that mimics the LLM debate pattern.
        Produces the same output shape without any API call.
        """
        prosecution = self._heuristic_prosecution(log, sigma_alerts, gnn_score)
        defence = self._heuristic_defence(log, sigma_alerts, gnn_score)

        # Judge scoring
        mal_score = 0.0
        if sigma_alerts:
            # Use same severity tiers as tri_brain
            sev_score = max(
                {"low": 0.10, "medium": 0.18, "high": 0.25, "critical": 0.35}.get(
                    a.severity, 0.18) for a in sigma_alerts
            )
            mal_score += sev_score + min(0.10, 0.03 * (len(sigma_alerts) - 1))
        if gnn_score >= 0.65:
            mal_score += 0.35
        elif gnn_score >= 0.45:
            mal_score += 0.20
        elif gnn_score >= 0.30:
            mal_score += 0.10
        if log.get("is_admin") and "DC" in log.get("host", ""):
            mal_score += 0.08
        if log.get("attack_technique"):
            mal_score += 0.08

        if mal_score >= 0.45:
            verdict, conf = "malicious", min(0.5 + mal_score, 0.95)
            reasoning = f"Strong evidence: SIGMA={len(sigma_alerts)}, GNN={gnn_score:.2f}"
        elif mal_score >= 0.2:
            verdict, conf = "uncertain", 0.5
            reasoning = f"Mixed signals: SIGMA={len(sigma_alerts)}, GNN={gnn_score:.2f}"
        else:
            verdict, conf = "benign", 0.85
            reasoning = "No significant indicators"

        record = DebateRecord(
            log_summary=f"EventID={log.get('event_id')} host={log.get('host')}",
            prosecution_argument=prosecution,
            defence_argument=defence,
            judge_verdict=verdict,
            judge_confidence=conf,
            judge_reasoning=reasoning,
            used_llm=False,
        )
        self.debate_log.append(record)
        return verdict, conf

    def _heuristic_prosecution(self, log: dict, sigma_alerts: list,
                                gnn_score: float) -> str:
        parts = []
        if sigma_alerts:
            rules = ", ".join(a.title for a in sigma_alerts[:2])
            parts.append(f"SIGMA rules fired: {rules}")
        if gnn_score >= 0.5:
            parts.append(f"GNN anomaly score {gnn_score:.2f} exceeds baseline")
        if log.get("attack_technique"):
            parts.append(f"Log tagged with ATT&CK technique {log['attack_technique']}")
        if log.get("is_admin") and "DC" in log.get("host", ""):
            parts.append("Admin account accessed Domain Controller — high-value target")
        return (" | ".join(parts) if parts
                else "No direct SIGMA or GNN signal, but behaviour deviates from norm.")

    def _heuristic_defence(self, log: dict, sigma_alerts: list,
                            gnn_score: float) -> str:
        parts = []
        if not sigma_alerts:
            parts.append("No SIGMA rules triggered — no known malicious pattern matched")
        if gnn_score < 0.4:
            parts.append(f"GNN score {gnn_score:.2f} is within normal range")
        dept = log.get("department", "")
        if dept in ("IT", "Engineering"):
            parts.append(f"{dept} users legitimately perform admin operations")
        eid = log.get("event_id", 0)
        if eid in (4624, 4634, 4648):
            parts.append("Event ID is a standard authentication event, common in normal ops")
        return (" | ".join(parts) if parts
                else "Activity could be explained by legitimate administrative work.")

    def stats(self) -> dict:
        total = len(self.debate_log)
        llm_used = sum(1 for d in self.debate_log if d.used_llm)
        verdicts = {"malicious": 0, "benign": 0, "uncertain": 0}
        for d in self.debate_log:
            verdicts[d.judge_verdict] = verdicts.get(d.judge_verdict, 0) + 1
        return {
            "total_debates": total,
            "llm_powered": llm_used,
            "heuristic": total - llm_used,
            "verdicts": verdicts,
        }
