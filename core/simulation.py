"""
NEXUS — Simulation Orchestrator (Phase 2 upgrade)
Runs battles: attackers act, defender detects, evolution engine learns.
"""

from __future__ import annotations

import json
import uuid
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from core.digital_twin import DigitalTwin
from attackers.personas import build_war_council
from attackers.base_agent import BaseAttackerAgent
from defender.tri_brain import TriBrainEnsemble, DetectionResult


@dataclass
class BattleReport:
    battle_id: str
    timestamp: str
    num_turns: int
    attacker_logs: list[dict] = field(default_factory=list)
    normal_logs: list[dict] = field(default_factory=list)
    detection_results: list[dict] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    agent_statuses: list[dict] = field(default_factory=list)
    missed_techniques: list[str] = field(default_factory=list)
    evolution_result: dict = field(default_factory=dict)
    winner: str = "draw"


class NEXUSSimulation:
    """
    Runs a NEXUS battle simulation with optional evolution.

    Each turn:
      1. All six attackers produce attack logs (LLM or mock decisions).
      2. Digital twin adds background normal logs.
      3. TriBrainEnsemble (SIGMA + GNN + LLM Debate) analyses the mixed stream.
      4. After the battle: CognitiveEvolutionEngine improves the defender.
    """

    def __init__(
        self,
        num_users: int = 50,
        num_hosts: int = 20,
        llm_provider: str = "mock",
        turns: int = 10,
        normal_logs_per_turn: int = 20,
        seed: int = 42,
        verbose: bool = True,
        evolve: bool = True,
        gnn_pretrain_logs: int = 200,
    ):
        self.turns = turns
        self.normal_per_turn = normal_logs_per_turn
        self.verbose = verbose
        self.evolve = evolve
        self.gnn_pretrain_logs = gnn_pretrain_logs

        self.twin = DigitalTwin(num_users=num_users, num_hosts=num_hosts, seed=seed)
        self.agents: list[BaseAttackerAgent] = build_war_council(self.twin, llm_provider)
        self.defender = TriBrainEnsemble(llm_provider=llm_provider)

        # Evolution engine (optional import — only fails if files missing)
        self._evolution = None
        if evolve:
            try:
                from evolution.evolution_engine import CognitiveEvolutionEngine
                self._evolution = CognitiveEvolutionEngine(self.defender, llm_provider)
            except Exception as e:
                self._log(f"[Warning] Evolution engine unavailable: {e}")

        self.report: Optional[BattleReport] = None

    def _log(self, msg: str):
        if self.verbose:
            import sys
            from datetime import datetime, timezone
            ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
            print(f"[{ts}] {msg}")
            sys.stdout.flush()

    def _pretrain_gnn(self):
        """Generate benign baseline logs and train the GNN before battle starts."""
        self._log(f"[GNN] Pre-training on {self.gnn_pretrain_logs} benign logs …")
        baseline = self.twin.generate_log_stream(
            n_normal=self.gnn_pretrain_logs, n_attack=0
        )
        self.defender.train_gnn(baseline)
        self._log("[GNN] Pre-training complete ✓")

    def run(self) -> BattleReport:
        battle_id = str(uuid.uuid4())[:8]
        self._log(f"=== NEXUS Battle {battle_id} START ===")
        self._log(self.twin.summary())

        # Pre-train GNN on normal behaviour
        self._pretrain_gnn()

        report = BattleReport(
            battle_id=battle_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            num_turns=self.turns,
        )

        for turn in range(1, self.turns + 1):
            self._log(f"\n─── Turn {turn}/{self.turns} ───")

            # Attackers act
            turn_attack_logs = []
            for agent in self.agents:
                self._log(f"  [{agent.name:8s}] Synthesizing attack vectors...")
                log = agent.run_turn()
                turn_attack_logs.append(log)


            # CIPHER broadcasts footholds
            cipher = next((a for a in self.agents if a.name == "CIPHER"), None)
            if cipher:
                cipher.sell_access(self.agents)

            # NOVA probes the GNN
            nova = next((a for a in self.agents if a.name == "NOVA"), None)
            if nova:
                probe = nova.probe_detector(self.defender.gnn)
                if probe.get("evasion_ready"):
                    self._log(f"  [NOVA    ] Probe complete — "
                              f"estimated threshold ≈ {probe['estimated_threshold']:.3f}")

            # Generate normal background logs
            normal_logs = [self.twin.generate_normal_log()
                           for _ in range(self.normal_per_turn)]

            # Defender analyses mixed stream
            all_logs = normal_logs + turn_attack_logs
            results = self.defender.analyze_stream(all_logs)

            try:
                from integrations.siem_forwarder import get_forwarder
                fwd = get_forwarder()
                attack_results = results[-len(turn_attack_logs):]
                for log, r in zip(turn_attack_logs, attack_results):
                    agent_name = log.get("attacker", "UNKNOWN")
                    tech = log.get("attack_technique", "Unknown")
                    host = log.get("host", "Unknown")
                    stealth = log.get("stealth_level", "?")
                    
                    # Log to terminal perfectly in sync with the graph update
                    self._log(f"  [{agent_name:8s}] {tech} -> {host:12s} stealth={stealth}")
                    
                    log["detected"] = (r.ensemble_verdict == "malicious")
                    fwd.forward(log)
                    time.sleep(0.85)  # Pace the attacks out so the graph animates sequentially!
            except Exception:
                pass

            tp_turn = sum(
                1 for r in results
                if r.ensemble_verdict == "malicious" and r.true_label == "malicious"
            )
            self._log(
                f"  [Defender] Detected {tp_turn}/{len(turn_attack_logs)} attacks "
                f"| SIGMA alerts: {sum(1 for r in results if r.sigma_fired)}"
            )

            report.attacker_logs.extend(turn_attack_logs)
            report.normal_logs.extend(normal_logs)
            report.detection_results.extend(
                [self._serialise_result(r) for r in results]
            )
            


        # Final metrics
        report.metrics = self.defender.metrics()
        report.agent_statuses = [a.status() for a in self.agents]
        report.missed_techniques = self.defender.sigma.get_missed_techniques(
            report.attacker_logs, report.detection_results
        )

        # Determine winner
        f1 = report.metrics.get("f1_score", 0)
        report.winner = "defender" if f1 >= 0.7 else "attacker" if f1 <= 0.3 else "draw"

        # Evolution — defender learns from the battle
        if self._evolution:
            self._log("\n[Evolution] Running post-battle learning …")
            report.evolution_result = self._evolution.evolve(report, self.defender)

        self._log(f"\n=== Battle {battle_id} END | Winner: {report.winner.upper()} ===")
        self._log(f"F1={report.metrics['f1_score']} "
                  f"P={report.metrics['precision']} "
                  f"R={report.metrics['recall']}")

        self.report = report

        # Flush SIEM buffer
        try:
            from integrations.siem_forwarder import get_forwarder
            get_forwarder().flush()
        except Exception:
            pass

        
        try:
            from integrations.siem_forwarder import get_forwarder
            get_forwarder().flush()
        except Exception:
            pass
        return report

    @staticmethod
    def _serialise_result(r: DetectionResult) -> dict:
        """Convert DetectionResult to JSON-safe dict."""
        return {
            "ensemble_verdict":    r.ensemble_verdict,
            "ensemble_confidence": r.ensemble_confidence,
            "signature_matched":   r.signature_matched,
            "true_label":          r.true_label,
            "correct":             r.correct,
            "sigma_fired":         r.sigma_fired,
            "sigma_count":         len(r.sigma_alerts),
            "gnn_score":           r.gnn_score,
            "gnn_flagged":         r.gnn_flagged,
            "llm_verdict":         r.llm_verdict,
            "llm_confidence":      r.llm_confidence,
            "host":  r.log.get("host"),
            "user":  r.log.get("user"),
            "eid":   r.log.get("event_id"),
            "technique": r.log.get("attack_technique"),
            "attacker":  r.log.get("attacker"),
        }

    def save_report(self, path: str = "data/reports") -> str:
        if self.report is None:
            return ""
        Path(path).mkdir(parents=True, exist_ok=True)
        fname = f"{path}/battle_{self.report.battle_id}.json"
        safe = json.loads(json.dumps(self.report.__dict__, default=str))
        with open(fname, "w") as f:
            json.dump(safe, f, indent=2)
        print(f"[NEXUS] Report saved → {fname}")
        return fname
