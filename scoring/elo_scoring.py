"""
NEXUS — Layer 6: ELO War Scoring System
Tracks per-agent and defender ELO ratings across battles.
Also computes per-technique effectiveness and generates leaderboards.

Standard ELO with K-factor tuned for cybersecurity simulation:
  - Attacker wins (technique evades detection)   → attacker ELO ↑, defender ↓
  - Defender wins (technique detected)           → defender ELO ↑, attacker ↓
  - Partial credit for stealth / detection speed

ARM64-safe: pure Python.
"""

from __future__ import annotations

import json
import math
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


# ── ELO Constants ─────────────────────────────────────────────────────────────

K_AGENT    = 32    # K-factor for agent ELO updates
K_DEFENDER = 24    # defender updates more slowly (ensemble system)
INITIAL_ELO = 1000


# ── Data Models ───────────────────────────────────────────────────────────────

@dataclass
class ELORecord:
    entity: str          # agent name or "DEFENDER"
    elo: float
    battles: int
    wins: int
    losses: int
    draws: int
    techniques_used: dict = field(default_factory=dict)   # technique → uses
    techniques_evaded: dict = field(default_factory=dict) # technique → evasions
    peak_elo: float = INITIAL_ELO
    last_battle: str = ""


@dataclass
class BattleOutcome:
    battle_id: str
    timestamp: str
    agent_name: str
    technique: str
    detected: bool         # True = defender won this exchange
    stealth_level: str     # low | medium | high
    gnn_score: float
    sigma_fired: bool
    turns_to_detect: int   # 0 if not detected


# ── ELO Engine ────────────────────────────────────────────────────────────────

class ELOWarScoring:
    """
    Manages ELO ratings for all six agents and the defender.

    After each battle, call .process_battle(report, detection_results).
    Use .leaderboard() to get the ranked table.
    Use .technique_effectiveness() for per-technique win rates.
    """

    AGENTS = ["VIPER", "KRAKEN", "GHOST", "HYDRA", "NOVA", "CIPHER", "DEFENDER"]

    def __init__(self, db_path: str = "data/elo.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.records: dict[str, ELORecord] = {}
        self._init_db()
        self._load_records()

    # ── Storage ───────────────────────────────────────────────────────────────

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS elo_records (
                entity      TEXT PRIMARY KEY,
                elo         REAL,
                battles     INTEGER,
                wins        INTEGER,
                losses      INTEGER,
                draws       INTEGER,
                techniques_used    TEXT,
                techniques_evaded  TEXT,
                peak_elo    REAL,
                last_battle TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS battle_outcomes (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                battle_id       TEXT,
                timestamp       TEXT,
                agent_name      TEXT,
                technique       TEXT,
                detected        INTEGER,
                stealth_level   TEXT,
                gnn_score       REAL,
                sigma_fired     INTEGER,
                turns_to_detect INTEGER
            )
        """)
        conn.commit()
        conn.close()

    def _load_records(self):
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute("SELECT * FROM elo_records").fetchall()
        conn.close()
        for row in rows:
            (entity, elo, battles, wins, losses, draws,
             tech_used, tech_evaded, peak, last) = row
            self.records[entity] = ELORecord(
                entity=entity, elo=elo, battles=battles,
                wins=wins, losses=losses, draws=draws,
                techniques_used=json.loads(tech_used or "{}"),
                techniques_evaded=json.loads(tech_evaded or "{}"),
                peak_elo=peak, last_battle=last,
            )
        # Initialise any missing entities
        for name in self.AGENTS:
            if name not in self.records:
                initial_elos = {
                    "VIPER": 1200, "NOVA": 1300, "CIPHER": 1100,
                    "KRAKEN": 1050, "GHOST": 980, "HYDRA": 900,
                    "DEFENDER": 1000,
                }
                self.records[name] = ELORecord(
                    entity=name,
                    elo=initial_elos.get(name, INITIAL_ELO),
                    battles=0, wins=0, losses=0, draws=0,
                    peak_elo=initial_elos.get(name, INITIAL_ELO),
                )

    def _save_records(self):
        conn = sqlite3.connect(self.db_path)
        for rec in self.records.values():
            conn.execute("""
                INSERT OR REPLACE INTO elo_records VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (
                rec.entity, rec.elo, rec.battles, rec.wins, rec.losses, rec.draws,
                json.dumps(rec.techniques_used),
                json.dumps(rec.techniques_evaded),
                rec.peak_elo, rec.last_battle,
            ))
        conn.commit()
        conn.close()

    def _save_outcomes(self, outcomes: list[BattleOutcome]):
        conn = sqlite3.connect(self.db_path)
        for o in outcomes:
            conn.execute("""
                INSERT INTO battle_outcomes VALUES (NULL,?,?,?,?,?,?,?,?,?)
            """, (
                o.battle_id, o.timestamp, o.agent_name, o.technique,
                int(o.detected), o.stealth_level, o.gnn_score,
                int(o.sigma_fired), o.turns_to_detect,
            ))
        conn.commit()
        conn.close()

    # ── ELO Calculation ───────────────────────────────────────────────────────

    @staticmethod
    def _expected(rating_a: float, rating_b: float) -> float:
        """Expected score for player A against player B."""
        return 1.0 / (1.0 + math.pow(10, (rating_b - rating_a) / 400))

    @staticmethod
    def _update(rating: float, expected: float, actual: float, k: float) -> float:
        return rating + k * (actual - expected)

    def _score_exchange(self, detected: bool, stealth: str,
                        gnn_score: float) -> tuple[float, float]:
        """
        Map one attacker↔defender exchange to win scores [0,1].
        Returns (attacker_score, defender_score).
        Partial credit: high-stealth near-miss = attacker 0.6, defender 0.4.
        """
        stealth_mult = {"high": 1.2, "medium": 1.0, "low": 0.8}.get(stealth, 1.0)

        if not detected:
            # Attacker evaded — full win
            att = min(1.0, 0.8 * stealth_mult)
            dfn = 1.0 - att
        else:
            # Defender detected
            if gnn_score >= 0.7:          # caught early by GNN
                att, dfn = 0.1, 0.9
            elif gnn_score >= 0.4:        # marginal detection
                att, dfn = 0.3, 0.7
            else:                         # only SIGMA caught it
                att, dfn = 0.4, 0.6
        return att, dfn

    # ── Main API ──────────────────────────────────────────────────────────────

    def process_battle(self, battle_report, detection_results: list[dict]) -> dict:
        """
        Process a completed battle report and update all ELO ratings.
        Returns the ELO delta summary.

        Defender ELO accounts for precision, not just recall:
          - Detecting an attack       → defender wins the exchange
          - Missing an attack         → attacker wins the exchange
          - False positive (FP rate)  → defender ELO penalty applied once per battle
        """
        bid = battle_report.battle_id
        ts  = battle_report.timestamp
        deltas: dict[str, float] = {}
        outcomes: list[BattleOutcome] = []

        attack_results = [r for r in detection_results
                          if r.get("technique") is not None]

        defender_rec = self.records["DEFENDER"]

        # Compute battle-level FP penalty for defender
        metrics = getattr(battle_report, "metrics", {})
        fp_rate = 0.0
        if metrics:
            fp = metrics.get("false_positives", 0)
            tn = metrics.get("true_negatives", 0)
            fp_rate = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        # Reduce defender ELO by FP rate × K (poor precision = ELO drain)
        fp_penalty = fp_rate * K_DEFENDER * 0.5
        defender_rec.elo = max(800.0, defender_rec.elo - fp_penalty)

        for result in attack_results:
            agent_name = result.get("attacker", "UNKNOWN")
            if agent_name not in self.records:
                continue

            agent_rec = self.records[agent_name]
            technique = result.get("technique", "T1078")
            detected  = result.get("ensemble_verdict") == "malicious" \
                        and result.get("true_label") == "malicious"
            stealth   = result.get("stealth_level") or "medium"
            gnn_score = float(result.get("gnn_score", 0.5))
            sigma_fired = bool(result.get("sigma_fired", False))

            att_score, dfn_score = self._score_exchange(detected, stealth, gnn_score)

            # ELO update — attacker vs defender
            exp_att = self._expected(agent_rec.elo, defender_rec.elo)
            exp_dfn = self._expected(defender_rec.elo, agent_rec.elo)

            new_att_elo = self._update(agent_rec.elo, exp_att, att_score, K_AGENT)
            new_dfn_elo = self._update(defender_rec.elo, exp_dfn, dfn_score, K_DEFENDER)

            delta_att = new_att_elo - agent_rec.elo
            delta_dfn = new_dfn_elo - defender_rec.elo

            agent_rec.elo    = round(new_att_elo, 1)
            defender_rec.elo = round(new_dfn_elo, 1)
            agent_rec.peak_elo    = max(agent_rec.peak_elo, agent_rec.elo)
            defender_rec.peak_elo = max(defender_rec.peak_elo, defender_rec.elo)

            # Win/loss bookkeeping
            if att_score > 0.5:
                agent_rec.wins += 1
                defender_rec.losses += 1
            elif dfn_score > 0.5:
                agent_rec.losses += 1
                defender_rec.wins += 1
            else:
                agent_rec.draws += 1
                defender_rec.draws += 1

            # Technique tracking
            agent_rec.techniques_used[technique] = \
                agent_rec.techniques_used.get(technique, 0) + 1
            if not detected:
                agent_rec.techniques_evaded[technique] = \
                    agent_rec.techniques_evaded.get(technique, 0) + 1

            deltas[agent_name] = deltas.get(agent_name, 0.0) + delta_att
            deltas["DEFENDER"] = deltas.get("DEFENDER", 0.0) + delta_dfn

            outcomes.append(BattleOutcome(
                battle_id=bid, timestamp=ts,
                agent_name=agent_name, technique=technique,
                detected=detected, stealth_level=stealth,
                gnn_score=gnn_score, sigma_fired=sigma_fired,
                turns_to_detect=0,
            ))

        # Update battle counts
        for name in self.AGENTS:
            rec = self.records[name]
            rec.battles += 1
            rec.last_battle = ts

        self._save_records()
        self._save_outcomes(outcomes)

        return {
            "battle_id": bid,
            "elo_deltas": {k: round(v, 1) for k, v in deltas.items()},
            "current_elos": self.current_elos(),
        }

    # ── Reports ───────────────────────────────────────────────────────────────

    def current_elos(self) -> dict[str, float]:
        return {name: round(rec.elo, 1)
                for name, rec in self.records.items()}

    def leaderboard(self) -> list[dict]:
        """Return agents ranked by ELO descending."""
        rows = []
        for rec in self.records.values():
            total = rec.wins + rec.losses + rec.draws
            wr = rec.wins / total if total > 0 else 0.0
            top_tech = (max(rec.techniques_used,
                            key=rec.techniques_used.get)
                        if rec.techniques_used else "—")
            evasion_rate = 0.0
            if rec.techniques_used:
                total_uses = sum(rec.techniques_used.values())
                total_evaded = sum(rec.techniques_evaded.values())
                evasion_rate = total_evaded / total_uses if total_uses > 0 else 0.0

            rows.append({
                "rank": 0,
                "entity":     rec.entity,
                "elo":        round(rec.elo, 0),
                "peak_elo":   round(rec.peak_elo, 0),
                "battles":    rec.battles,
                "wins":       rec.wins,
                "losses":     rec.losses,
                "win_rate":   round(wr, 3),
                "evasion_rate": round(evasion_rate, 3),
                "top_technique": top_tech,
            })
        rows.sort(key=lambda x: x["elo"], reverse=True)
        for i, row in enumerate(rows, 1):
            row["rank"] = i
        return rows

    def technique_effectiveness(self) -> list[dict]:
        """Per-technique win rate across all agents."""
        tech_stats: dict[str, dict] = {}
        for rec in self.records.values():
            if rec.entity == "DEFENDER":
                continue
            for tech, uses in rec.techniques_used.items():
                s = tech_stats.setdefault(tech, {"uses": 0, "evaded": 0})
                s["uses"] += uses
                s["evaded"] += rec.techniques_evaded.get(tech, 0)
        result = []
        for tech, s in tech_stats.items():
            evasion = s["evaded"] / s["uses"] if s["uses"] > 0 else 0.0
            result.append({
                "technique": tech,
                "uses": s["uses"],
                "evaded": s["evaded"],
                "detected": s["uses"] - s["evaded"],
                "evasion_rate": round(evasion, 3),
                "detection_rate": round(1.0 - evasion, 3),
            })
        result.sort(key=lambda x: x["evasion_rate"], reverse=True)
        return result

    def print_leaderboard(self):
        lb = self.leaderboard()
        print("\n" + "=" * 72)
        print(f"  {'NEXUS WAR LEADERBOARD':^68}")
        print("=" * 72)
        print(f"  {'#':<4} {'Entity':<12} {'ELO':>6} {'Peak':>6} "
              f"{'W':>4} {'L':>4} {'WR%':>6} {'Evasion%':>9} {'Top TTP':<12}")
        print("  " + "─" * 68)
        for r in lb:
            marker = "★" if r["entity"] == "DEFENDER" else " "
            print(
                f"  {r['rank']:<4} {marker}{r['entity']:<11} {r['elo']:>6.0f} "
                f"{r['peak_elo']:>6.0f} {r['wins']:>4} {r['losses']:>4} "
                f"{r['win_rate']*100:>5.1f}% {r['evasion_rate']*100:>8.1f}% "
                f"  {r['top_technique']:<12}"
            )
        print("=" * 72)
