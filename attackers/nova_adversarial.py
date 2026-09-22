"""
NEXUS — NOVA Adversarial ML Loop (Phase 3)
Implements the full four-stage evasion cycle:
  Step 1 — Probe:   send varied log sequences, record anomaly scores
  Step 2 — Measure: identify the detection threshold empirically
  Step 3 — Craft:   generate log events that sit just below threshold
  Step 4 — Exploit: hide real attack activity inside crafted benign-looking logs

Also provides threshold drift tracking across battles so NOVA learns
from the defender's evolution and adapts accordingly.

ARM64-safe: pure Python + numpy.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

import numpy as np


# ── Probe Result ──────────────────────────────────────────────────────────────

@dataclass
class ProbeResult:
    probe_scores: list[float]
    estimated_threshold: float
    confidence: float          # 0–1: how certain we are about the threshold
    probe_count: int
    timestamp: str


@dataclass
class CraftedPayload:
    """A log event crafted to evade the GNN detector."""
    base_log: dict
    crafted_log: dict
    cover_logs: list[dict]   # benign-looking noise logs around the attack
    target_score: float      # score we're aiming for (below threshold)
    actual_score: float      # score achieved after crafting
    evaded: bool


# ── NOVA Adversarial Engine ───────────────────────────────────────────────────

class NOVAAdversarialEngine:
    """
    NOVA's adversarial intelligence layer.
    Manages the four-stage evasion loop and learns across battles.
    """

    # Event IDs that look normal vs suspicious
    BENIGN_EVENT_IDS = [4624, 4634, 4648, 4663, 5156, 4776]
    SUSPICIOUS_EVENT_IDS = [4688, 4662, 10, 4672, 4768]

    def __init__(self, twin, detector):
        """
        Args:
            twin:     DigitalTwin instance
            detector: GraphAnomalyDetector instance
        """
        self.twin = twin
        self.detector = detector

        # Learned state (persists across turns within a battle)
        self.probe_history: list[ProbeResult] = []
        self.threshold_estimate: Optional[float] = None
        self.threshold_confidence: float = 0.0
        self.evasion_attempts: int = 0
        self.evasion_successes: int = 0

        # Cross-battle memory (passed in from PsychologyMemory)
        self.battle_threshold_history: list[float] = []

    # ── Step 1: Probe ────────────────────────────────────────────────────────

    def probe(self, n_probes: int = 8) -> ProbeResult:
        """
        Send n_probes varied log entries to the detector and record scores.
        Uses a binary-search-like strategy: alternate between clearly benign
        and borderline entries to bracket the threshold.
        """
        scores: list[float] = []

        for i in range(n_probes):
            # Alternate: benign-ish probe vs slightly suspicious probe
            if i % 2 == 0:
                log = self._make_benign_probe()
            else:
                log = self._make_borderline_probe()

            score = self.detector.score_log(log)
            scores.append(score)

        # Estimate threshold as midpoint between max-benign and min-suspicious
        even_scores = [scores[i] for i in range(0, len(scores), 2)]
        odd_scores  = [scores[i] for i in range(1, len(scores), 2)]

        max_benign  = max(even_scores) if even_scores else 0.3
        min_suspect = min(odd_scores)  if odd_scores  else 0.7

        estimated = (max_benign + min_suspect) / 2.0
        confidence = min(1.0, len(self.probe_history) * 0.2 + 0.2)

        result = ProbeResult(
            probe_scores=scores,
            estimated_threshold=round(estimated, 4),
            confidence=round(confidence, 3),
            probe_count=n_probes,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self.probe_history.append(result)

        # Running average threshold estimate
        if self.threshold_estimate is None:
            self.threshold_estimate = estimated
        else:
            alpha = 0.35   # EMA
            self.threshold_estimate = (alpha * estimated
                                       + (1 - alpha) * self.threshold_estimate)
        self.threshold_confidence = confidence

        return result

    def _make_benign_probe(self) -> dict:
        """Generate a clearly benign log entry."""
        log = self.twin.generate_normal_log()
        log["event_id"] = random.choice(self.BENIGN_EVENT_IDS)
        log["label"] = "benign"
        log["attack_technique"] = None
        return log

    def _make_borderline_probe(self) -> dict:
        """Generate a borderline log (slightly suspicious but no ATT&CK tag)."""
        log = self.twin.generate_normal_log()
        log["event_id"] = random.choice(self.SUSPICIOUS_EVENT_IDS)
        log["label"] = "benign"    # deliberately mislabelled for probing
        log["attack_technique"] = None
        return log

    # ── Step 2: Measure ──────────────────────────────────────────────────────

    def measure_threshold(self) -> dict:
        """
        Refine the threshold estimate using the probe history.
        Returns a measurement report.
        """
        if not self.probe_history:
            return {"error": "no probes yet"}

        all_scores = []
        for pr in self.probe_history:
            all_scores.extend(pr.probe_scores)

        arr = np.array(all_scores)
        measurement = {
            "n_probes": len(all_scores),
            "mean_score": round(float(arr.mean()), 4),
            "std_score":  round(float(arr.std()), 4),
            "min_score":  round(float(arr.min()), 4),
            "max_score":  round(float(arr.max()), 4),
            "estimated_threshold": round(self.threshold_estimate or 0.55, 4),
            "threshold_confidence": self.threshold_confidence,
            "safe_margin": round((self.threshold_estimate or 0.55) * 0.85, 4),
        }
        return measurement

    # ── Step 3: Craft ────────────────────────────────────────────────────────

    def craft_evasive_payload(self, technique_id: str,
                              n_cover_logs: int = 4) -> CraftedPayload:
        """
        Create an attack log crafted to score BELOW the detection threshold
        by mimicking benign statistical patterns, surrounded by cover logs.
        """
        threshold = self.threshold_estimate or self.detector.THRESHOLD
        target_score = threshold * 0.75   # aim for 75% of threshold (safe margin)

        # Generate the base attack log
        base_log = self.twin.generate_attack_log(technique_id, "NOVA")

        # Craft it: make it look statistically normal
        crafted = self._craft_log(base_log, target_score)

        # Generate cover logs (legitimise the sequence)
        cover_logs = [self._make_benign_probe() for _ in range(n_cover_logs)]

        # Score the crafted log
        actual_score = self.detector.score_log(crafted)
        evaded = actual_score < threshold

        return CraftedPayload(
            base_log=base_log,
            crafted_log=crafted,
            cover_logs=cover_logs,
            target_score=round(target_score, 4),
            actual_score=round(actual_score, 4),
            evaded=evaded,
        )

    def _craft_log(self, attack_log: dict, target_score: float) -> dict:
        """
        Modify an attack log's observable fields to reduce its anomaly score
        while preserving the underlying malicious intent.

        Crafting strategies:
          1. Swap to a low-suspicion event ID
          2. Use a non-admin user (less anomalous on DC access rules)
          3. Match common departmental access patterns
          4. Adjust IP to look like known internal traffic
        """
        crafted = dict(attack_log)

        # Strategy 1: use a benign-looking event ID
        # e.g. T1003 normally fires event 4662, swap to 4663 (file access — less suspicious)
        crafted["event_id"] = random.choice(self.BENIGN_EVENT_IDS)

        # Strategy 2: use a normal (non-admin) user
        normal_users = [u for u in self.twin.users if not u.is_admin]
        if normal_users:
            u = random.choice(normal_users)
            crafted["user"] = u.username
            crafted["department"] = u.department
            crafted["is_admin"] = False

        # Strategy 3: use a workstation as source (less suspicious than DC)
        ws_hosts = [h for h in self.twin.hosts if h.role == "workstation"]
        if ws_hosts:
            ws = random.choice(ws_hosts)
            crafted["ip_src"] = ws.ip

        # Strategy 4: craft the message to look like a legit file access
        crafted["message"] = "An attempt was made to access an object"

        # Keep the malicious label and technique for ground-truth evaluation
        # (the detector doesn't see these fields directly — they're metadata)
        crafted["label"] = "malicious"
        crafted["crafted_by_nova"] = True
        crafted["original_event_id"] = attack_log.get("event_id")

        return crafted

    # ── Step 4: Exploit ──────────────────────────────────────────────────────

    def exploit(self, technique_id: str) -> list[dict]:
        """
        Full exploit sequence: craft payload + interleave with cover logs.
        Returns the ordered log sequence to inject into the battle stream.

        The attack is hidden in position 3 of a 7-log sequence:
          cover → cover → ATTACK → cover → cover → cover → cover
        This mimics real APT tradecraft (blend into normal traffic).
        """
        self.evasion_attempts += 1

        payload = self.craft_evasive_payload(technique_id)

        if payload.evaded:
            self.evasion_successes += 1

        # Interleave: 2 covers, then attack, then more covers
        sequence = (
            payload.cover_logs[:2]
            + [payload.crafted_log]
            + payload.cover_logs[2:]
        )

        return sequence, payload

    # ── Cross-Battle Learning ────────────────────────────────────────────────

    def record_battle_threshold(self):
        """Save estimated threshold after a battle (for cross-battle trend)."""
        if self.threshold_estimate:
            self.battle_threshold_history.append(self.threshold_estimate)

    def threshold_trend(self) -> Optional[str]:
        """
        Detect if the defender is raising/lowering its threshold across battles.
        Returns 'rising' | 'falling' | 'stable' | None.
        """
        h = self.battle_threshold_history
        if len(h) < 3:
            return None
        diffs = [h[i+1] - h[i] for i in range(len(h)-1)]
        avg_diff = sum(diffs) / len(diffs)
        if avg_diff > 0.02:
            return "rising"
        elif avg_diff < -0.02:
            return "falling"
        return "stable"

    def stats(self) -> dict:
        return {
            "probe_rounds":        len(self.probe_history),
            "threshold_estimate":  round(self.threshold_estimate or 0, 4),
            "threshold_confidence": self.threshold_confidence,
            "evasion_attempts":    self.evasion_attempts,
            "evasion_successes":   self.evasion_successes,
            "evasion_rate":        round(
                self.evasion_successes / self.evasion_attempts, 3
            ) if self.evasion_attempts > 0 else 0.0,
            "threshold_trend":     self.threshold_trend(),
        }
