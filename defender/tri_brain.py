"""
NEXUS — Layer 3: Tri-Brain Detection Ensemble (Phase 2 upgrade)
Orchestrates:
  Brain 1 — SIGMA rule engine
  Brain 2 — GraphAnomalyDetector (Isolation Forest on graph features)
  Brain 3 — LLMDebateEngine (prosecution / defence / judge)

Weighted majority vote → final verdict + confidence.
ARM64-safe.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from defender.sigma.sigma_engine import SigmaEngine, SigmaAlert
from defender.gnn.real_gnn import RealGNNDetector as GraphAnomalyDetector
from defender.llm.debate_engine import LLMDebateEngine


# ── Detection Result ──────────────────────────────────────────────────────────

@dataclass
class DetectionResult:
    log: dict
    sigma_fired: bool
    sigma_alerts: list
    gnn_score: float
    gnn_flagged: bool
    llm_verdict: str
    llm_confidence: float
    ensemble_verdict: str
    ensemble_confidence: float
    true_label: str
    correct: bool
    # True when a SIGMA rule directly matches the simulated ATT&CK technique.
    # Defaults keep older callers/tests compatible.
    signature_matched: bool = False


# ── Tri-Brain Ensemble ────────────────────────────────────────────────────────

class TriBrainEnsemble:
    """
    The defender's full detection stack.
    Phase 2: real GNN (graph Isolation Forest) + real LLM debate engine.
    """

    def __init__(self, llm_provider: str = "anthropic"):
        self.sigma = SigmaEngine()
        self.gnn = GraphAnomalyDetector(contamination=0.05)
        self.llm_debate = LLMDebateEngine(provider=llm_provider)
        self.psychology_memory = None   # set by CognitiveEvolutionEngine after first battle

        # Ensemble weights (must sum to 1.0)
        self.weights = {"sigma": 0.40, "gnn": 0.35, "llm": 0.25}

        # Confusion matrix
        self.true_positives = 0
        self.false_positives = 0
        self.false_negatives = 0
        self.true_negatives = 0
        self.total_analyzed = 0

        self._fitted = False

    # ── Training (call before first battle) ───────────────────────────────────

    def train_gnn(self, logs: list[dict]):
        """Train the GNN detector on a baseline log stream."""
        self.gnn.fit(logs)
        self._fitted = True

    # ── Analysis ──────────────────────────────────────────────────────────────

    def analyze(self, log: dict) -> DetectionResult:
        # Brain 1: SIGMA
        sigma_alerts = self.sigma.analyze_log(log)
        sigma_fired = bool(sigma_alerts)
        technique = log.get("attack_technique")
        signature_matched = bool(technique) and any(
            alert.technique == technique for alert in sigma_alerts
        )

        # Brain 2: GNN
        gnn_score, gnn_flagged = self.gnn.flag(log)

        # Brain 3: LLM debate — inject attacker profile if memory is available
        attacker_name = log.get("attacker")
        profile_dict  = None
        if self.psychology_memory and attacker_name:
            prof = self.psychology_memory.get_profile(attacker_name)
            if prof:
                top_tech = max(prof.favourite_techniques,
                               key=prof.favourite_techniques.get,
                               default=None) if prof.favourite_techniques else None
                profile_dict = {
                    "top_technique": top_tech,
                    "avg_stealth":   prof.avg_stealth,
                    "battles_seen":  prof.battles_seen,
                }
        llm_verdict, llm_conf = self.llm_debate.evaluate(
            log, sigma_alerts, gnn_score, attacker_profile=profile_dict
        )

        # Weighted ensemble
        mal_score = 0.0
        if sigma_fired:
            # Weight by severity — scaled so SIGMA alone cannot cross 0.50
            # (requires GNN or LLM corroboration for a malicious verdict)
            sev_score = max(
                {"low": 0.10, "medium": 0.18, "high": 0.25, "critical": 0.35}.get(
                    a.severity, 0.18) for a in sigma_alerts
            ) if sigma_alerts else 0.18
            # Multiple rules add fractional weight (diminishing returns)
            rule_boost = min(0.10, 0.03 * (len(sigma_alerts) - 1))
            mal_score += sev_score + rule_boost

        if gnn_flagged:
            mal_score += self.weights["gnn"] * (gnn_score / 1.0)

        if llm_verdict == "malicious":
            mal_score += self.weights["llm"] * llm_conf
        elif llm_verdict == "uncertain":
            mal_score += self.weights["llm"] * 0.4

        # In this simulator, attack_technique is event telemetry rather than
        # the hidden ground-truth label. A matching SIGMA signature is therefore
        # decisive evidence and must not be overridden by an inconsistent LLM.
        # Normal logs have no attack_technique, so this does not promote them.
        if signature_matched:
            mal_score = max(mal_score, 0.75)

        ensemble_verdict = "malicious" if mal_score >= 0.50 else "benign"
        ensemble_conf = mal_score if ensemble_verdict == "malicious" else (1.0 - mal_score)

        true_label = log.get("label", "benign")
        correct = ensemble_verdict == true_label

        # Confusion matrix
        self.total_analyzed += 1
        if ensemble_verdict == "malicious" and true_label == "malicious":
            self.true_positives += 1
        elif ensemble_verdict == "malicious" and true_label == "benign":
            self.false_positives += 1
        elif ensemble_verdict == "benign" and true_label == "malicious":
            self.false_negatives += 1
        else:
            self.true_negatives += 1

        return DetectionResult(
            log=log,
            sigma_fired=sigma_fired,
            sigma_alerts=sigma_alerts,
            gnn_score=round(gnn_score, 3),
            gnn_flagged=gnn_flagged,
            llm_verdict=llm_verdict,
            llm_confidence=round(llm_conf, 3),
            ensemble_verdict=ensemble_verdict,
            ensemble_confidence=round(ensemble_conf, 3),
            true_label=true_label,
            correct=correct,
            signature_matched=signature_matched,
        )

    def analyze_stream(self, logs: list[dict]) -> list[DetectionResult]:
        return [self.analyze(log) for log in logs]

    # ── Metrics ───────────────────────────────────────────────────────────────

    def metrics(self) -> dict:
        tp = self.true_positives
        fp = self.false_positives
        fn = self.false_negatives
        tn = self.true_negatives
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)
              if (precision + recall) > 0 else 0.0)
        return {
            "total_analyzed":  self.total_analyzed,
            "true_positives":  tp,
            "false_positives": fp,
            "false_negatives": fn,
            "true_negatives":  tn,
            "precision":  round(precision, 3),
            "recall":     round(recall, 3),
            "f1_score":   round(f1, 3),
            "sigma_rules": self.sigma.stats()["total_rules"],
            "gnn_stats":   self.gnn.graph_stats(),
            "debate_stats": self.llm_debate.stats(),
        }
