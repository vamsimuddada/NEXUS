"""
NEXUS — 100-Simulation Bulk Runner
Runs N simulations (default 100) with varied seeds and parameters,
collecting aggregated statistics for research publication.

Outputs:
  - data/bulk/bulk_results.json    : per-sim metrics
  - data/bulk/bulk_summary.json    : aggregated statistics
  - data/datasets/                 : combined labeled dataset

Designed to be resumable (skips completed seeds) and shows a progress bar.
ARM64-safe: pure Python.
"""

from __future__ import annotations

import json
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class SimResult:
    seed: int
    battle_id: str
    f1: float
    precision: float
    recall: float
    sigma_rules: int
    auto_rules: int
    nova_evasion: float
    winner: str
    duration_s: float
    tp: int
    fp: int
    fn: int
    tn: int


class BulkRunner:
    """
    Runs N independent single-battle simulations with varied seeds.
    Each battle uses the same configuration but a different random seed,
    enabling statistical analysis of detection performance distributions.
    """

    def __init__(
        self,
        n_sims: int = 100,
        turns: int = 6,
        num_users: int = 30,
        num_hosts: int = 10,
        llm_provider: str = "mock",
        normal_per_turn: int = 15,
        gnn_pretrain: int = 150,
        output_dir: str = "data/bulk",
        resume: bool = True,
    ):
        self.n_sims        = n_sims
        self.turns         = turns
        self.num_users     = num_users
        self.num_hosts     = num_hosts
        self.llm_provider  = llm_provider
        self.normal_per_turn = normal_per_turn
        self.gnn_pretrain  = gnn_pretrain
        self.output_dir    = Path(output_dir)
        self.resume        = resume
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.results: list[SimResult] = []
        self._results_path = self.output_dir / "bulk_results.json"

        if resume and self._results_path.exists():
            self._load_existing()

    def _load_existing(self):
        with open(self._results_path) as f:
            data = json.load(f)
        for d in data:
            self.results.append(SimResult(**d))
        print(f"[Bulk] Resumed: {len(self.results)} prior results loaded")

    def _completed_seeds(self) -> set[int]:
        return {r.seed for r in self.results}

    def run(self) -> dict:
        from core.simulation import NEXUSSimulation
        from evolution.evolution_engine import CognitiveEvolutionEngine

        completed = self._completed_seeds()
        seeds_todo = [s for s in range(self.n_sims) if s not in completed]

        print(f"[Bulk] Running {len(seeds_todo)} simulations "
              f"({len(completed)} already done) …")

        for i, seed in enumerate(seeds_todo, 1):
            t0 = time.time()

            try:
                sim = NEXUSSimulation(
                    num_users=self.num_users,
                    num_hosts=self.num_hosts,
                    llm_provider=self.llm_provider,
                    turns=self.turns,
                    normal_logs_per_turn=self.normal_per_turn,
                    gnn_pretrain_logs=self.gnn_pretrain,
                    seed=seed,
                    verbose=False,
                    evolve=True,
                )
                report = sim.run()
                m = report.metrics
                ev = report.evolution_result

                nova_agent = next(
                    (a for a in sim.agents if a.name == "NOVA"), None
                )

                result = SimResult(
                    seed=seed,
                    battle_id=report.battle_id,
                    f1=m["f1_score"],
                    precision=m["precision"],
                    recall=m["recall"],
                    sigma_rules=m["sigma_rules"],
                    auto_rules=len(ev.get("new_sigma_rules", [])),
                    nova_evasion=0.0,   # evasion only meaningful across battles
                    winner=report.winner,
                    duration_s=round(time.time() - t0, 2),
                    tp=m["true_positives"],
                    fp=m["false_positives"],
                    fn=m["false_negatives"],
                    tn=m["true_negatives"],
                )
                self.results.append(result)

                # Progress
                pct = (len(completed) + i) / self.n_sims * 100
                bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
                print(f"\r  [{bar}] {pct:5.1f}%  sim {seed:03d} "
                      f"F1={result.f1:.3f} P={result.precision:.3f} "
                      f"winner={result.winner}", end="", flush=True)

                # Save incrementally every 10 sims
                if i % 10 == 0:
                    self._save_results()

            except Exception as e:
                print(f"\n[Bulk] Sim {seed} failed: {e}")

        print()  # newline after progress bar
        self._save_results()
        summary = self._compute_summary()
        self._save_summary(summary)
        self._print_summary(summary)
        return summary

    def _save_results(self):
        with open(self._results_path, "w") as f:
            json.dump([r.__dict__ for r in self.results], f, indent=2)

    def _compute_summary(self) -> dict:
        if not self.results:
            return {}

        f1s   = [r.f1        for r in self.results]
        precs = [r.precision for r in self.results]
        recs  = [r.recall    for r in self.results]
        durs  = [r.duration_s for r in self.results]

        winners = {
            "attacker": sum(1 for r in self.results if r.winner == "attacker"),
            "defender": sum(1 for r in self.results if r.winner == "defender"),
            "draw":     sum(1 for r in self.results if r.winner == "draw"),
        }

        def stats(vals: list[float]) -> dict:
            if len(vals) < 2:
                return {"mean": vals[0] if vals else 0, "stdev": 0,
                        "min": vals[0] if vals else 0, "max": vals[0] if vals else 0,
                        "p25": vals[0] if vals else 0, "p75": vals[0] if vals else 0,
                        "median": vals[0] if vals else 0}
            s = sorted(vals)
            n = len(s)
            return {
                "mean":   round(statistics.mean(vals), 4),
                "stdev":  round(statistics.stdev(vals), 4),
                "median": round(statistics.median(vals), 4),
                "min":    round(min(vals), 4),
                "max":    round(max(vals), 4),
                "p25":    round(s[n // 4], 4),
                "p75":    round(s[3 * n // 4], 4),
            }

        # Auto-rule generation rate
        sims_with_new_rules = sum(1 for r in self.results if r.auto_rules > 0)

        return {
            "n_simulations": len(self.results),
            "generated_at":  datetime.now(timezone.utc).isoformat(),
            "f1":            stats(f1s),
            "precision":     stats(precs),
            "recall":        stats(recs),
            "duration_s":    stats(durs),
            "winners":       winners,
            "winner_rates": {
                k: round(v / len(self.results), 3)
                for k, v in winners.items()
            },
            "rule_generation_rate": round(sims_with_new_rules / len(self.results), 3),
            "avg_auto_rules_per_sim": round(
                statistics.mean([r.auto_rules for r in self.results]), 3
            ),
        }

    def _save_summary(self, summary: dict):
        path = self.output_dir / "bulk_summary.json"
        with open(path, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"[Bulk] Summary → {path}")

    def _print_summary(self, s: dict):
        print(f"\n{'═'*56}")
        print(f"  NEXUS BULK RUN — {s['n_simulations']} SIMULATIONS")
        print(f"{'═'*56}")
        print(f"  F1   : mean={s['f1']['mean']:.3f}  "
              f"σ={s['f1']['stdev']:.3f}  "
              f"[{s['f1']['min']:.3f}, {s['f1']['max']:.3f}]")
        print(f"  P    : mean={s['precision']['mean']:.3f}  "
              f"σ={s['precision']['stdev']:.3f}")
        print(f"  R    : mean={s['recall']['mean']:.3f}  "
              f"σ={s['recall']['stdev']:.3f}")
        print(f"  Time : mean={s['duration_s']['mean']:.1f}s / sim")
        print(f"  Winners: attacker={s['winners']['attacker']}  "
              f"defender={s['winners']['defender']}  "
              f"draw={s['winners']['draw']}")
        print(f"  Rule gen rate : {s['rule_generation_rate']:.1%}")
        print(f"  Avg auto rules: {s['avg_auto_rules_per_sim']:.2f} / sim")
        print(f"{'═'*56}\n")
