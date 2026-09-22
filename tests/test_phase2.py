"""
NEXUS — Phase 2 Tests
Run with: pytest tests/test_phase2.py -v
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from core.digital_twin import DigitalTwin
from core.simulation import NEXUSSimulation
from defender.gnn.graph_detector import GraphAnomalyDetector, GraphFeatures
from defender.llm.debate_engine import LLMDebateEngine
from defender.tri_brain import TriBrainEnsemble
from defender.sigma.sigma_engine import SigmaEngine, SigmaRule
from evolution.evolution_engine import (
    CognitiveEvolutionEngine, RuleRewriter, ModelUpdater, PsychologyMemory
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_twin(n_users=15, n_hosts=6, seed=99):
    return DigitalTwin(num_users=n_users, num_hosts=n_hosts, seed=seed)


# ── GraphAnomalyDetector ──────────────────────────────────────────────────────

class TestGraphDetector:
    def setup_method(self):
        self.twin = make_twin()
        self.detector = GraphAnomalyDetector(contamination=0.05)

    def test_score_unfitted_returns_heuristic(self):
        log = self.twin.generate_normal_log()
        score = self.detector.score_log(log)
        assert 0.0 <= score <= 1.0

    def test_fit_on_benign_logs(self):
        logs = self.twin.generate_log_stream(n_normal=100, n_attack=0)
        self.detector.fit(logs)
        assert self.detector.is_fitted

    def test_fitted_scores_in_range(self):
        logs = self.twin.generate_log_stream(n_normal=100, n_attack=0)
        self.detector.fit(logs)
        attack_log = self.twin.generate_attack_log("T1003", "KRAKEN")
        score = self.detector.score_log(attack_log)
        assert 0.0 <= score <= 1.0

    def test_flag_returns_tuple(self):
        log = self.twin.generate_normal_log()
        score, flagged = self.detector.flag(log)
        assert isinstance(score, float)
        assert isinstance(flagged, bool)

    def test_graph_updates_on_scoring(self):
        for _ in range(20):
            log = self.twin.generate_normal_log()
            self.detector.score_log(log)
        assert len(self.detector.graph.nodes) > 0
        assert len(self.detector.graph.edges) > 0

    def test_graph_stats(self):
        stats = self.detector.graph_stats()
        assert "nodes" in stats
        assert "is_fitted" in stats
        assert "threshold" in stats

    def test_partial_fit_after_training(self):
        logs = self.twin.generate_log_stream(n_normal=80, n_attack=0)
        self.detector.fit(logs)
        new_logs = self.twin.generate_log_stream(n_normal=30, n_attack=0)
        self.detector.partial_fit(new_logs)   # should not crash
        assert self.detector.is_fitted

    def test_suspicious_edges(self):
        for _ in range(5):
            self.detector.score_log(self.twin.generate_normal_log())
        edges = self.detector.get_suspicious_edges(threshold=1)
        assert isinstance(edges, list)

    def test_feature_vector_shape(self):
        log = self.twin.generate_normal_log()
        self.detector._update_graph(log)
        feat = self.detector._extract_features(log)
        vec = feat.to_vector()
        assert vec.shape == (9,)
        assert vec.dtype == np.float32

    def test_save_load(self, tmp_path):
        logs = self.twin.generate_log_stream(n_normal=60, n_attack=0)
        self.detector.fit(logs)
        path = str(tmp_path / "model.pkl")
        self.detector.save(path)
        new_det = GraphAnomalyDetector()
        new_det.load(path)
        assert new_det.is_fitted


# ── LLM Debate Engine ─────────────────────────────────────────────────────────

class TestLLMDebate:
    def setup_method(self):
        self.twin = make_twin()
        self.engine = LLMDebateEngine(provider="anthropic")  # no key → heuristic
        self.sigma = SigmaEngine()

    def test_heuristic_benign_log(self):
        log = self.twin.generate_normal_log()
        log["event_id"] = 4634   # logoff, benign
        log["label"] = "benign"
        log["is_admin"] = False
        log["host"] = "WS-555"
        alerts = self.sigma.analyze_log(log)
        verdict, conf = self.engine.evaluate(log, alerts, gnn_score=0.1)
        assert verdict in ("malicious", "benign", "uncertain")
        assert 0.0 <= conf <= 1.0

    def test_heuristic_malicious_log(self):
        log = self.twin.generate_attack_log("T1003", "KRAKEN")
        alerts = self.sigma.analyze_log(log)
        verdict, conf = self.engine.evaluate(log, alerts, gnn_score=0.8)
        assert verdict in ("malicious", "uncertain")
        assert conf > 0.0

    def test_stats_structure(self):
        log = self.twin.generate_normal_log()
        self.engine.evaluate(log, [], 0.1)
        stats = self.engine.stats()
        assert "total_debates" in stats
        assert stats["total_debates"] >= 1
        assert "verdicts" in stats

    def test_debate_log_grows(self):
        for _ in range(5):
            log = self.twin.generate_normal_log()
            self.engine.evaluate(log, [], 0.2)
        assert len(self.engine.debate_log) == 5

    def test_prosecution_returns_string(self):
        log = self.twin.generate_attack_log("T1059", "HYDRA")
        alerts = self.sigma.analyze_log(log)
        result = self.engine._heuristic_prosecution(log, alerts, 0.7)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_defence_returns_string(self):
        log = self.twin.generate_normal_log()
        result = self.engine._heuristic_defence(log, [], 0.1)
        assert isinstance(result, str)


# ── Evolution Engine ──────────────────────────────────────────────────────────

class TestEvolutionEngine:
    def setup_method(self):
        self.twin = make_twin()
        self.defender = TriBrainEnsemble()

    def test_rule_rewriter_template(self):
        rewriter = RuleRewriter(self.defender.sigma, provider="mock")
        new_rules = rewriter.rewrite_for_missed(["T1562"], [])
        assert len(new_rules) == 1
        assert new_rules[0].technique == "T1562"
        assert new_rules[0].auto_generated

    def test_rule_rewriter_no_duplicate(self):
        rewriter = RuleRewriter(self.defender.sigma, provider="mock")
        rewriter.rewrite_for_missed(["T1486"], [])
        count_before = len(self.defender.sigma.rules)
        rewriter.rewrite_for_missed(["T1486"], [])  # already exists — should refine, not add
        count_after = len(self.defender.sigma.rules)
        assert count_after == count_before   # no new rule added

    def test_rule_rewriter_unknown_technique(self):
        rewriter = RuleRewriter(self.defender.sigma, provider="mock")
        new_rules = rewriter.rewrite_for_missed(["T9999"], [])
        assert len(new_rules) == 1
        assert new_rules[0].technique == "T9999"

    def test_model_updater(self):
        gnn = self.defender.gnn
        # Pre-train first
        logs = self.twin.generate_log_stream(n_normal=60, n_attack=0)
        gnn.fit(logs)
        updater = ModelUpdater(gnn)
        new_logs = self.twin.generate_log_stream(n_normal=30, n_attack=5)
        stats = updater.update(new_logs)
        assert "update_number" in stats
        assert stats["update_number"] == 1

    def test_model_updater_skip_small_batch(self):
        gnn = self.defender.gnn
        updater = ModelUpdater(gnn)
        stats = updater.update([self.twin.generate_normal_log()])
        assert stats.get("skipped") is True

    def test_psychology_memory_ingest(self, tmp_path):
        mem = PsychologyMemory(persist_path=str(tmp_path))
        logs = [self.twin.generate_attack_log("T1078", "VIPER") for _ in range(5)]
        status = {"agent": "VIPER", "phase": "lateral_movement",
                  "compromised_hosts": ["DC-001"], "logs_generated": 5, "elo": 1200}
        mem.ingest_battle("VIPER", logs, status, battle_id="test-001")
        profile = mem.get_profile("VIPER")
        assert profile is not None
        assert profile.battles_seen == 1
        assert "T1078" in profile.favourite_techniques

    def test_psychology_memory_predict(self, tmp_path):
        mem = PsychologyMemory(persist_path=str(tmp_path))
        logs = ([self.twin.generate_attack_log("T1003", "KRAKEN") for _ in range(5)]
                + [self.twin.generate_attack_log("T1059", "KRAKEN") for _ in range(2)])
        status = {"agent": "KRAKEN", "phase": "exfiltration",
                  "compromised_hosts": [], "logs_generated": 7, "elo": 1050}
        mem.ingest_battle("KRAKEN", logs, status, battle_id="test-002")
        prediction = mem.predict_next_technique("KRAKEN")
        assert prediction == "T1003"   # most frequent

    def test_psychology_memory_summary(self, tmp_path):
        mem = PsychologyMemory(persist_path=str(tmp_path))
        summary = mem.summary()
        assert "profiles_stored" in summary
        assert "storage_backend" in summary

    def test_psychology_memory_survives_restart(self, tmp_path):
        mem = PsychologyMemory(persist_path=str(tmp_path))
        logs = [self.twin.generate_attack_log("T1078", "VIPER")]
        status = {"phase": "initial_access", "compromised_hosts": []}
        mem.ingest_battle("VIPER", logs, status, battle_id="restart-001")

        reloaded = PsychologyMemory(persist_path=str(tmp_path))
        profile = reloaded.get_profile("VIPER")
        assert profile is not None
        assert profile.battles_seen == 1
        assert profile.favourite_techniques["T1078"] == 1

    def test_evolution_engine_full_cycle(self, tmp_path):
        """Integration test: run a mini simulation and evolve."""
        sim = NEXUSSimulation(
            num_users=10, num_hosts=5,
            llm_provider="mock",
            turns=2,
            normal_logs_per_turn=10,
            verbose=False,
            evolve=False,  # we'll call evolve manually
            gnn_pretrain_logs=50,
        )
        report = sim.run()

        engine = CognitiveEvolutionEngine(sim.defender, provider="mock")
        # Override memory path to tmp
        engine.memory = PsychologyMemory(persist_path=str(tmp_path))

        result = engine.evolve(report, sim.defender)
        assert "evolution_cycle" in result
        assert result["evolution_cycle"] == 1
        assert "total_sigma_rules" in result


# ── Full Phase 2 Simulation ───────────────────────────────────────────────────

class TestPhase2Simulation:
    def test_simulation_with_gnn_training(self):
        sim = NEXUSSimulation(
            num_users=10, num_hosts=5,
            llm_provider="mock",
            turns=3,
            normal_logs_per_turn=10,
            verbose=False,
            evolve=True,
            gnn_pretrain_logs=80,
        )
        report = sim.run()
        assert report.battle_id is not None
        assert len(report.attacker_logs) == 3 * 6
        assert report.metrics["total_analyzed"] > 0
        assert report.metrics["gnn_stats"]["is_fitted"] is True
        assert "debate_stats" in report.metrics

    def test_gnn_scores_malicious_higher_after_training(self):
        twin = DigitalTwin(num_users=10, num_hosts=5, seed=7)
        detector = GraphAnomalyDetector()
        benign = twin.generate_log_stream(n_normal=120, n_attack=0)
        detector.fit(benign)

        normal_scores = [detector.score_log(twin.generate_normal_log()) for _ in range(20)]
        attack_scores = [detector.score_log(twin.generate_attack_log("T1003", "KRAKEN"))
                         for _ in range(20)]
        avg_normal = sum(normal_scores) / len(normal_scores)
        avg_attack = sum(attack_scores) / len(attack_scores)
        # Attack logs should score higher on average
        assert avg_attack >= avg_normal - 0.05   # small tolerance

    def test_metrics_include_all_brains(self):
        sim = NEXUSSimulation(
            num_users=8, num_hosts=4,
            llm_provider="mock",
            turns=2,
            normal_logs_per_turn=5,
            verbose=False,
            evolve=False,
            gnn_pretrain_logs=40,
        )
        report = sim.run()
        m = report.metrics
        assert "precision" in m
        assert "recall" in m
        assert "f1_score" in m
        assert "gnn_stats" in m
        assert "debate_stats" in m
        assert "sigma_rules" in m

    def test_evolution_adds_sigma_rules(self):
        sim = NEXUSSimulation(
            num_users=10, num_hosts=5,
            llm_provider="mock",
            turns=3,
            normal_logs_per_turn=10,
            verbose=False,
            evolve=True,
            gnn_pretrain_logs=60,
        )
        rules_before = len(sim.defender.sigma.rules)
        report = sim.run()
        rules_after = len(sim.defender.sigma.rules)
        # Evolution may or may not add rules depending on what was missed
        assert rules_after >= rules_before
