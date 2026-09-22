"""
NEXUS — Phase 3: Multi-Battle Campaign Runner
Runs N sequential battles where the defender evolves between each one.
Tracks ELO, SOAR actions, NOVA evasion progress, and precision improvement.

This is the core loop that proves the research question:
  "Does co-evolution produce emergent TTPs over time?"
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from core.digital_twin import DigitalTwin
from attackers.coalition import (
    process_coalition_messages, broadcast_detection_alert,
    nova_broadcast_threshold, apply_target_override, apply_stealth_override
)
from attackers.personas import build_war_council
from attackers.nova_adversarial import NOVAAdversarialEngine
from defender.tri_brain import TriBrainEnsemble
from evolution.evolution_engine import CognitiveEvolutionEngine
from scoring.elo_scoring import ELOWarScoring
from soar.soar_engine import SOAREngine
from core.simulation import NEXUSSimulation, BattleReport


# ── Campaign Record ───────────────────────────────────────────────────────────

@dataclass
class CampaignRecord:
    campaign_id: str
    start_time: str
    battles_completed: int = 0
    battle_ids: list[str] = field(default_factory=list)

    # Per-battle metrics (for trend analysis)
    f1_history:        list[float] = field(default_factory=list)
    precision_history: list[float] = field(default_factory=list)
    recall_history:    list[float] = field(default_factory=list)
    sigma_rule_history: list[int]  = field(default_factory=list)
    elo_history:       list[dict]  = field(default_factory=list)
    nova_evasion_history: list[float] = field(default_factory=list)
    soar_action_history:  list[int]   = field(default_factory=list)
    winner_history:    list[str]   = field(default_factory=list)

    # Final summary
    final_elo_table:   list[dict] = field(default_factory=list)
    technique_stats:   list[dict] = field(default_factory=list)
    evolution_summary: dict       = field(default_factory=dict)


# ── Campaign Runner ───────────────────────────────────────────────────────────

class CampaignRunner:
    """
    Orchestrates a multi-battle NEXUS campaign.

    The defender persists across battles (ELO, SIGMA rules, GNN model, memory).
    The digital twin is regenerated each battle (fresh environment).
    Attackers persist their ELO and memory but reset campaign state each battle.

    Usage:
        runner = CampaignRunner(n_battles=5, turns_per_battle=8)
        record = runner.run()
        runner.print_campaign_report(record)
    """

    def __init__(
        self,
        n_battles: int = 5,
        turns_per_battle: int = 8,
        num_users: int = 40,
        num_hosts: int = 12,
        llm_provider: str = "mock",
        normal_logs_per_turn: int = 20,
        gnn_pretrain_logs: int = 200,
        seed: int = 42,
        verbose: bool = True,
        save_reports: bool = True,
    ):
        self.n_battles         = n_battles
        self.turns_per_battle  = turns_per_battle
        self.num_users         = num_users
        self.num_hosts         = num_hosts
        self.llm_provider      = llm_provider
        self.normal_per_turn   = normal_logs_per_turn
        self.gnn_pretrain_logs = gnn_pretrain_logs
        self.base_seed         = seed
        self.verbose           = verbose
        self.save_reports      = save_reports

        # Persistent across battles
        self.elo_scoring = ELOWarScoring()
        self.evolution   : Optional[CognitiveEvolutionEngine] = None

        # NOVA adversarial engine (persists across battles)
        self._nova_engine: Optional[NOVAAdversarialEngine] = None

        import uuid
        self._campaign_id = str(uuid.uuid4())[:8]

    def _log(self, msg: str):
        if self.verbose:
            ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
            print(f"[{ts}] {msg}")

    # ── Campaign Run ──────────────────────────────────────────────────────────

    def run(self) -> CampaignRecord:
        record = CampaignRecord(
            campaign_id=self._campaign_id,
            start_time=datetime.now(timezone.utc).isoformat(),
        )

        # Build a persistent defender (SIGMA + GNN + LLM persist across battles)
        persistent_defender = TriBrainEnsemble(llm_provider=self.llm_provider)

        # Build evolution engine (also persists)
        self.evolution = CognitiveEvolutionEngine(
            persistent_defender, self.llm_provider
        )

        self._log(f"\n{'═'*64}")
        self._log(f"  NEXUS CAMPAIGN {self._campaign_id}  |  {self.n_battles} battles")
        self._log(f"{'═'*64}")

        for battle_num in range(1, self.n_battles + 1):
            self._log(f"\n{'─'*64}")
            self._log(f"  ⚔  BATTLE {battle_num}/{self.n_battles}")
            self._log(f"{'─'*64}")

            seed = self.base_seed + battle_num
            report = self._run_single_battle(
                battle_num, seed, persistent_defender
            )

            # ELO scoring
            detection_results = report.detection_results
            elo_result = self.elo_scoring.process_battle(report, detection_results)

            # SOAR stats from simulation (injected into report)
            soar_actions = report.evolution_result.get("soar_actions", 0)

            # NOVA evasion tracking
            nova_evasion = self._get_nova_evasion_rate()

            # Record history
            m = report.metrics
            record.battles_completed  += 1
            record.battle_ids.append(report.battle_id)
            record.f1_history.append(m["f1_score"])
            record.precision_history.append(m["precision"])
            record.recall_history.append(m["recall"])
            record.sigma_rule_history.append(m["sigma_rules"])
            record.elo_history.append(elo_result["current_elos"])
            record.nova_evasion_history.append(nova_evasion)
            record.soar_action_history.append(soar_actions)
            record.winner_history.append(report.winner)

            # Print battle summary
            self._log(f"\n  Battle {battle_num} result: {report.winner.upper()}")
            self._log(f"  F1={m['f1_score']} | P={m['precision']} | R={m['recall']}")
            self._log(f"  SIGMA rules: {m['sigma_rules']} | "
                      f"NOVA evasion rate: {nova_evasion:.1%}")
            self.elo_scoring.print_leaderboard()

        # Campaign summary
        record.final_elo_table = self.elo_scoring.leaderboard()
        record.technique_stats = self.elo_scoring.technique_effectiveness()
        record.evolution_summary = {
            "total_sigma_rules": len(persistent_defender.sigma.rules),
            "auto_generated_rules": sum(
                1 for r in persistent_defender.sigma.rules if r.auto_generated
            ),
            "gnn_updates": self.evolution.model_updater.total_updates,
            "agent_profiles": self.evolution.memory.summary(),
        }

        self._print_campaign_report(record)

        if self.save_reports:
            self._save_campaign(record)
            self._generate_research_outputs(record)

        return record

    def _run_single_battle(self, battle_num: int, seed: int,
                           persistent_defender: TriBrainEnsemble) -> BattleReport:
        """Run one battle, reusing the persistent defender."""
        # Fresh environment each battle
        twin = DigitalTwin(
            num_users=self.num_users,
            num_hosts=self.num_hosts,
            seed=seed,
        )
        agents = build_war_council(twin, self.llm_provider)

        # SOAR engine (fresh per battle but stats accumulate)
        soar = SOAREngine(twin)

        # Initialise / update NOVA adversarial engine
        nova_agent = next(a for a in agents if a.name == "NOVA")
        if self._nova_engine is None:
            self._nova_engine = NOVAAdversarialEngine(twin, persistent_defender.gnn)
        else:
            # Carry threshold knowledge forward into new battle
            prev_threshold = self._nova_engine.threshold_estimate
            prev_confidence = self._nova_engine.threshold_confidence
            prev_history = list(self._nova_engine.battle_threshold_history)

            self._nova_engine.twin     = twin
            self._nova_engine.detector = persistent_defender.gnn
            self._nova_engine.record_battle_threshold()

            # Restore cross-battle knowledge (new twin, same learned threshold)
            if prev_threshold is not None:
                self._nova_engine.threshold_estimate  = prev_threshold
                # Confidence starts higher because we've seen previous battles
                self._nova_engine.threshold_confidence = min(
                    0.95, prev_confidence + 0.15
                )
            self._nova_engine.battle_threshold_history = prev_history

        # Pre-train GNN on benign baseline (uses persistent model — partial_fit)
        if not persistent_defender.gnn.is_fitted:
            self._log(f"[GNN] Initial training on {self.gnn_pretrain_logs} benign logs…")
            baseline = twin.generate_log_stream(n_normal=self.gnn_pretrain_logs, n_attack=0)
            persistent_defender.train_gnn(baseline)
        else:
            # Warm up with fresh env logs (incremental)
            warm = twin.generate_log_stream(n_normal=50, n_attack=0)
            persistent_defender.gnn.partial_fit(warm)

        # Reset defender confusion matrix for this battle
        persistent_defender.true_positives = 0
        persistent_defender.false_positives = 0
        persistent_defender.false_negatives = 0
        persistent_defender.true_negatives = 0
        persistent_defender.total_analyzed = 0

        import uuid
        battle_id = str(uuid.uuid4())[:8]
        self._log(f"[Battle {battle_num}] id={battle_id} seed={seed}")

        report = BattleReport(
            battle_id=battle_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            num_turns=self.turns_per_battle,
        )

        for turn in range(1, self.turns_per_battle + 1):

            # NOVA: probe then decide whether to craft or attack normally
            nova_probe = self._nova_engine.probe(n_probes=6)
            nova_using_evasion = (
                self._nova_engine.threshold_confidence > 0.4
                and battle_num > 1
            )

            turn_attack_logs: list[dict] = []

            # ── Coalition: process inbox messages from last turn ──────────
            coalition_actions = process_coalition_messages(agents, twin)
            for name, acts in coalition_actions.items():
                for act in acts:
                    self._log(f"  [COALITION] {name}: {act}")

            # ── NOVA broadcasts threshold intel to council ─────────────────
            if self._nova_engine and self._nova_engine.threshold_estimate:
                nova_broadcast_threshold(
                    next(a for a in agents if a.name == "NOVA"),
                    agents,
                    self._nova_engine.threshold_estimate,
                )

            for agent in agents:
                # Check coalition target override first
                coalition_action = apply_target_override(agent, twin)

                if agent.name == "NOVA" and nova_using_evasion:
                    technique = "T1071"
                    seq, payload = self._nova_engine.exploit(technique)
                    attack_portion = [l for l in seq if l.get("label") == "malicious"]
                    turn_attack_logs.extend(attack_portion)
                elif coalition_action:
                    # Execute coalition-directed action
                    coalition_action = apply_stealth_override(agent, coalition_action)
                    log = agent.execute_action(coalition_action)
                    turn_attack_logs.append(log)
                else:
                    action = agent.decide_next_action()
                    action = apply_stealth_override(agent, action)
                    log = agent.execute_action(action)
                    turn_attack_logs.append(log)

            # CIPHER broadcasts footholds
            cipher = next((a for a in agents if a.name == "CIPHER"), None)
            if cipher:
                cipher.sell_access(agents)
                # VIPER shares intel on high-value targets
                viper = next((a for a in agents if a.name == "VIPER"), None)
                if viper and viper.state.compromised_hosts:
                    from attackers.base_agent import BaseAttackerAgent
                    viper.broadcast(
                        agents,
                        f"High-value host identified: {viper.state.compromised_hosts[-1]}",
                        msg_type="intel"
                    )

            # Broadcast detection alerts for caught agents this turn
            caught_agents = set()
            for res in []:  # populated after defender analysis below
                if res.get("ensemble_verdict") == "malicious" and res.get("attacker"):
                    caught_agents.add(res["attacker"])

            # Normal background logs
            normal_logs = [twin.generate_normal_log()
                           for _ in range(self.normal_per_turn)]

            # Defender analyses mixed stream
            all_logs = normal_logs + turn_attack_logs
            results = persistent_defender.analyze_stream(all_logs)

            # SOAR responds
            soar_actions = soar.respond(results, agents)

            # Broadcast detection alerts to remaining agents
            caught = {r.log.get("attacker") for r in results
                      if r.ensemble_verdict == "malicious"
                      and r.true_label == "malicious"
                      and r.log.get("attacker")}
            for caught_name in caught:
                caught_agent = next((a for a in agents if a.name == caught_name), None)
                if caught_agent:
                    broadcast_detection_alert(caught_agent, agents)

            report.attacker_logs.extend(turn_attack_logs)
            report.normal_logs.extend(normal_logs)
            report.detection_results.extend(
                [self._serialise_result(r) for r in results]
            )

        # Final metrics
        report.metrics = persistent_defender.metrics()
        report.agent_statuses = [a.status() for a in agents]
        report.missed_techniques = persistent_defender.sigma.get_missed_techniques(
            report.attacker_logs, report.detection_results
        )
        f1 = report.metrics["f1_score"]
        report.winner = "defender" if f1 >= 0.7 else "attacker" if f1 <= 0.3 else "draw"

        # Evolution
        evo_result = self.evolution.evolve(report, persistent_defender)
        evo_result["soar_actions"] = len(soar.actions)
        evo_result["soar_stats"] = soar.stats()
        report.evolution_result = evo_result

        return report

    def _get_nova_evasion_rate(self) -> float:
        if self._nova_engine is None:
            return 0.0
        return self._nova_engine.stats()["evasion_rate"]

    @staticmethod
    def _serialise_result(r) -> dict:
        return {
            "ensemble_verdict":    r.ensemble_verdict,
            "ensemble_confidence": r.ensemble_confidence,
            "true_label":          r.true_label,
            "correct":             r.correct,
            "sigma_fired":         r.sigma_fired,
            "sigma_count":         len(r.sigma_alerts),
            "gnn_score":           r.gnn_score,
            "gnn_flagged":         r.gnn_flagged,
            "llm_verdict":         r.llm_verdict,
            "llm_confidence":      r.llm_confidence,
            "host":      r.log.get("host"),
            "technique": r.log.get("attack_technique"),
            "attacker":  r.log.get("attacker"),
            "stealth_level": r.log.get("stealth_level"),
        }

    # ── Reports ───────────────────────────────────────────────────────────────

    def _print_campaign_report(self, record: CampaignRecord):
        print(f"\n{'═'*64}")
        print(f"  NEXUS CAMPAIGN {record.campaign_id} — FINAL REPORT")
        print(f"{'═'*64}")
        print(f"  Battles: {record.battles_completed}")
        print(f"  Winners: {record.winner_history}")
        print()

        # F1 trend
        print("  Defender F1 trend across battles:")
        for i, (f1, p, r) in enumerate(zip(
                record.f1_history, record.precision_history, record.recall_history), 1):
            bar = "█" * int(f1 * 20)
            trend = ("↑" if i > 1 and f1 > record.f1_history[i-2]
                     else "↓" if i > 1 and f1 < record.f1_history[i-2]
                     else "→")
            print(f"  Battle {i}: {bar:<20} F1={f1:.3f} P={p:.3f} R={r:.3f} {trend}")

        # SIGMA rules grown
        print(f"\n  SIGMA rules: {record.sigma_rule_history[0]} → "
              f"{record.sigma_rule_history[-1]} "
              f"(+{record.sigma_rule_history[-1]-record.sigma_rule_history[0]} auto-generated)")

        # NOVA evasion trend
        print("\n  NOVA evasion rate per battle:")
        for i, er in enumerate(record.nova_evasion_history, 1):
            bar = "█" * int(er * 20)
            print(f"  Battle {i}: {bar:<20} {er:.1%}")

        # Technique effectiveness
        print("\n  Technique effectiveness (attacker evasion rates):")
        for t in record.technique_stats[:5]:
            bar = "█" * int(t["evasion_rate"] * 20)
            print(f"  {t['technique']}: {bar:<20} {t['evasion_rate']:.1%} evasion "
                  f"({t['uses']} uses)")

        # Evolution summary
        es = record.evolution_summary
        print(f"\n  Evolution summary:")
        print(f"    Total SIGMA rules  : {es.get('total_sigma_rules')}")
        print(f"    Auto-generated     : {es.get('auto_generated_rules')}")
        print(f"    GNN update cycles  : {es.get('gnn_updates')}")
        mem = es.get("agent_profiles", {})
        print(f"    Agent profiles     : {mem.get('profiles_stored', 0)} "
              f"({mem.get('storage_backend','?')} backend)")

        print(f"\n{'═'*64}\n")

    def _save_campaign(self, record: CampaignRecord):
        import os as _os
        _root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
        path  = Path(_root) / "data" / "campaigns"
        path.mkdir(parents=True, exist_ok=True)
        fname = path / f"campaign_{record.campaign_id}.json"
        safe = json.loads(json.dumps(record.__dict__, default=str))
        with open(fname, "w") as f:
            json.dump(safe, f, indent=2)
        print(f"[Campaign] Saved → {fname}")

    def _generate_research_outputs(self, record: CampaignRecord):
        """Run all Layer 7 research output generators after a campaign."""
        import sys, os as _os
        from pathlib import Path as _Path
        # Ensure nexus root is always on sys.path regardless of cwd
        _nexus_root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
        if _nexus_root not in sys.path:
            sys.path.insert(0, _nexus_root)
        # All output paths are absolute — work regardless of cwd
        _data = _Path(_nexus_root) / "data"
        (_data / "stix").mkdir(parents=True, exist_ok=True)
        (_data / "research").mkdir(parents=True, exist_ok=True)
        (_data / "datasets").mkdir(parents=True, exist_ok=True)
        cid = record.campaign_id
        _stix_path    = str(_data / f"stix/campaign_{cid}.json")
        _dataset_path = str(_data / f"datasets/{cid}")
        _paper_path   = str(_data / f"research/paper_{cid}.md")
        _nav_path     = str(_data / f"research/navigator_{cid}.json")
        _chains_path  = str(_data / f"research/tactic_chains_{cid}.json")
        _d3_path      = str(_data / f"research/killchain_{cid}.html")
        _res_dir      = str(_data / "research")

        # ── STIX bundle ───────────────────────────────────────────────────────
        try:
            from research.stix_generator import STIXBundleGenerator
            gen = STIXBundleGenerator()
            bundle = gen.from_campaign(record)
            gen.save(bundle, _stix_path)
        except Exception as e:
            print(f"[Research] STIX generation failed: {e}")

        # ── Labeled dataset ───────────────────────────────────────────────────
        try:
            from research.dataset_exporter import DatasetExporter
            exporter = DatasetExporter()
            exporter.ingest_campaign(record)
            exporter.export_all(_dataset_path)
        except Exception as e:
            print(f"[Research] Dataset export failed: {e}")

        # ── Paper draft ───────────────────────────────────────────────────────
        try:
            from research.paper_generator import PaperSectionGenerator
            paper_gen = PaperSectionGenerator()
            paper_gen.generate_paper(record, _paper_path)
        except Exception as e:
            print(f"[Research] Paper generation failed: {e}")

        # ── ATT&CK Navigator layer ─────────────────────────────────────────
        try:
            from research.attck_client import get_client
            attck = get_client(use_live=False)
            # Enrich technique_stats with tactic context
            for stat in record.technique_stats:
                meta = attck.get_technique(stat["technique"])
                stat["tactic"]        = meta.get("tactic_name", "Unknown")
                stat["technique_name"]= meta.get("name", stat["technique"])
                stat["top_attacker"]  = "mixed"
            attck.save_navigator_layer(record.technique_stats, cid, _nav_path)
            # Validate tactic chains per agent from ELO table
            chains = {}
            for row in record.final_elo_table:
                if row["entity"] == "DEFENDER":
                    continue
                tech = row.get("top_technique")
                if tech and tech != "—":
                    chains[row["entity"]] = attck.validate_tactic_chain([tech])
            if chains:
                _Path(_chains_path).write_text(
                    json.dumps(chains, indent=2)
                )
                print(f"[ATT&CK] Tactic chains → {_chains_path}")
        except Exception as e:
            print(f"[Research] ATT&CK outputs failed: {e}")

        # ── D3 kill-chain visualiser ────────────────────────────────────────
        try:
            from research.killchain_viz import generate_killchain_html
            from research.attck_client import get_client as get_attck
            generate_killchain_html(record, get_attck(use_live=False), _d3_path)
        except Exception as e:
            print(f"[Research] D3 visualiser failed: {e}")

        # ── PDF + LaTeX paper output ────────────────────────────────────────
        try:
            from research.pdf_generator import PDFPaperGenerator
            import glob
            paper_files = sorted(glob.glob(_paper_path))
            if paper_files:
                gen = PDFPaperGenerator()
                gen.generate_all(paper_files[0], _res_dir)
        except Exception as e:
            print(f"[Research] PDF/LaTeX generation failed: {e}")
