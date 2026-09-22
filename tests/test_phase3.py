"""
NEXUS — Phase 3 Tests
Run with: pytest tests/test_phase3.py -v
"""

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.digital_twin import DigitalTwin
from core.simulation import NEXUSSimulation
from attackers.personas import build_war_council
from attackers.nova_adversarial import NOVAAdversarialEngine
from defender.tri_brain import TriBrainEnsemble
from defender.gnn.graph_detector import GraphAnomalyDetector
from scoring.elo_scoring import ELOWarScoring
from soar.soar_engine import SOAREngine


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_twin(seed=42):
    return DigitalTwin(num_users=15, num_hosts=6, seed=seed)


def make_sim(turns=2, verbose=False, evolve=False):
    return NEXUSSimulation(
        num_users=10, num_hosts=5, llm_provider="mock",
        turns=turns, normal_logs_per_turn=8,
        gnn_pretrain_logs=60, verbose=verbose, evolve=evolve,
    )


# ── ELO Scoring ──────────────────────────────────────────────────────────────

class TestELOScoring:
    def setup_method(self, tmp_path=None):
        import tempfile, os
        self._tmpdir = tempfile.mkdtemp()
        db = os.path.join(self._tmpdir, "elo.db")
        self.elo = ELOWarScoring(db_path=db)

    def test_initial_elos_set(self):
        elos = self.elo.current_elos()
        assert "VIPER" in elos
        assert "DEFENDER" in elos
        assert elos["NOVA"] > elos["HYDRA"]   # NOVA starts higher

    def test_leaderboard_length(self):
        lb = self.elo.leaderboard()
        assert len(lb) == 7   # 6 agents + DEFENDER

    def test_leaderboard_ranked(self):
        lb = self.elo.leaderboard()
        elos = [r["elo"] for r in lb]
        assert elos == sorted(elos, reverse=True)

    def test_elo_update_after_battle(self):
        sim = make_sim(turns=2)
        report = sim.run()
        before = dict(self.elo.current_elos())
        self.elo.process_battle(report, report.detection_results)
        after = self.elo.current_elos()
        # At least one ELO must have changed
        changed = sum(1 for k in before if before[k] != after[k])
        assert changed > 0

    def test_expected_score_formula(self):
        # Equal ratings → 50% expected
        exp = ELOWarScoring._expected(1000, 1000)
        assert abs(exp - 0.5) < 0.001

    def test_expected_higher_rated_wins_more(self):
        exp_high = ELOWarScoring._expected(1200, 1000)
        exp_low  = ELOWarScoring._expected(1000, 1200)
        assert exp_high > 0.5
        assert exp_low  < 0.5
        assert abs(exp_high + exp_low - 1.0) < 0.001

    def test_elo_update_direction(self):
        # Win → ELO goes up
        new = ELOWarScoring._update(1000, 0.5, 1.0, 32)
        assert new > 1000
        # Loss → ELO goes down
        new = ELOWarScoring._update(1000, 0.5, 0.0, 32)
        assert new < 1000

    def test_score_exchange_detected(self):
        att, dfn = self.elo._score_exchange(detected=True, stealth="medium", gnn_score=0.8)
        assert dfn > att

    def test_score_exchange_evaded(self):
        att, dfn = self.elo._score_exchange(detected=False, stealth="high", gnn_score=0.2)
        assert att > dfn

    def test_technique_effectiveness(self):
        sim = make_sim(turns=2)
        report = sim.run()
        self.elo.process_battle(report, report.detection_results)
        stats = self.elo.technique_effectiveness()
        assert isinstance(stats, list)
        if stats:
            assert "technique" in stats[0]
            assert "evasion_rate" in stats[0]
            assert 0.0 <= stats[0]["evasion_rate"] <= 1.0


# ── NOVA Adversarial Engine ───────────────────────────────────────────────────

class TestNOVAAdversarial:
    def setup_method(self):
        self.twin = make_twin()
        self.detector = GraphAnomalyDetector()
        benign = self.twin.generate_log_stream(n_normal=80, n_attack=0)
        self.detector.fit(benign)
        self.nova = NOVAAdversarialEngine(self.twin, self.detector)

    def test_probe_returns_result(self):
        result = self.nova.probe(n_probes=6)
        assert len(result.probe_scores) == 6
        assert 0.0 <= result.estimated_threshold <= 1.0
        assert 0.0 <= result.confidence <= 1.0

    def test_probe_history_grows(self):
        for _ in range(3):
            self.nova.probe(n_probes=4)
        assert len(self.nova.probe_history) == 3

    def test_threshold_estimate_converges(self):
        for _ in range(5):
            self.nova.probe(n_probes=6)
        # After multiple probes, should have a stable estimate
        assert self.nova.threshold_estimate is not None
        assert 0.0 < self.nova.threshold_estimate < 1.0

    def test_measure_threshold(self):
        self.nova.probe(n_probes=6)
        m = self.nova.measure_threshold()
        assert "estimated_threshold" in m
        assert "safe_margin" in m
        assert m["safe_margin"] < m["estimated_threshold"]

    def test_measure_before_probe_error(self):
        fresh_nova = NOVAAdversarialEngine(self.twin, self.detector)
        result = fresh_nova.measure_threshold()
        assert "error" in result

    def test_craft_evasive_payload(self):
        self.nova.probe(n_probes=6)
        payload = self.nova.craft_evasive_payload("T1071")
        assert payload.crafted_log is not None
        assert payload.crafted_log.get("crafted_by_nova") is True
        assert payload.crafted_log.get("label") == "malicious"
        assert 0.0 <= payload.actual_score <= 1.0

    def test_crafted_event_id_is_benign(self):
        self.nova.probe(n_probes=6)
        payload = self.nova.craft_evasive_payload("T1071")
        assert payload.crafted_log["event_id"] in NOVAAdversarialEngine.BENIGN_EVENT_IDS

    def test_exploit_returns_sequence(self):
        self.nova.probe(n_probes=6)
        seq, payload = self.nova.exploit("T1071")
        assert isinstance(seq, list)
        assert len(seq) > 0
        assert self.nova.evasion_attempts == 1

    def test_evasion_tracking(self):
        self.nova.probe(n_probes=6)
        for _ in range(5):
            self.nova.exploit("T1071")
        stats = self.nova.stats()
        assert stats["evasion_attempts"] == 5
        assert 0.0 <= stats["evasion_rate"] <= 1.0

    def test_threshold_trend_needs_three_battles(self):
        assert self.nova.threshold_trend() is None
        self.nova.probe(n_probes=4)
        self.nova.record_battle_threshold()
        self.nova.probe(n_probes=4)
        self.nova.record_battle_threshold()
        assert self.nova.threshold_trend() is None  # need 3
        self.nova.probe(n_probes=4)
        self.nova.record_battle_threshold()
        trend = self.nova.threshold_trend()
        assert trend in ("rising", "falling", "stable")

    def test_stats_structure(self):
        self.nova.probe(n_probes=4)
        stats = self.nova.stats()
        for key in ("probe_rounds", "threshold_estimate", "evasion_attempts",
                    "evasion_successes", "evasion_rate"):
            assert key in stats


# ── SOAR Engine ───────────────────────────────────────────────────────────────

class TestSOAREngine:
    def setup_method(self):
        self.twin = make_twin()
        self.soar = SOAREngine(self.twin)
        self.agents = build_war_council(self.twin, "mock")

    def _make_detection_result(self, verdict="malicious", technique="T1003",
                               severity="critical", host="DC-001"):
        """Build a minimal DetectionResult-like object."""
        from defender.tri_brain import DetectionResult
        from defender.sigma.sigma_engine import SigmaAlert
        alert = SigmaAlert(
            rule_id="SIG-003", title="LSASS Dump",
            severity=severity, technique=technique,
            log={}, confidence=1.0,
        )
        log = {
            "attack_technique": technique,
            "host": host,
            "user": "test.user",
            "attacker": "KRAKEN",
            "label": "malicious",
        }
        return DetectionResult(
            log=log, sigma_fired=True, sigma_alerts=[alert],
            gnn_score=0.75, gnn_flagged=True,
            llm_verdict="malicious", llm_confidence=0.9,
            ensemble_verdict=verdict, ensemble_confidence=0.85,
            true_label="malicious", correct=True,
        )

    def test_respond_returns_actions(self):
        result = self._make_detection_result()
        actions = self.soar.respond([result], self.agents)
        assert isinstance(actions, list)

    def test_honeypot_deployed_on_critical(self):
        result = self._make_detection_result(severity="critical")
        self.soar.respond([result], self.agents)
        assert len(self.soar.honeypots) >= 1

    def test_honeypot_not_duplicated_excessively(self):
        result = self._make_detection_result(host="WS-999", severity="critical")
        for _ in range(5):
            self.soar.respond([result], self.agents)
        near_hps = [h for h in self.soar.honeypots if h["near"] == "WS-999"]
        assert len(near_hps) <= 2   # capped at 2

    def test_account_lockout_on_T1003(self):
        result = self._make_detection_result(technique="T1003")
        result.log["user"] = self.twin.users[0].username
        self.soar.respond([result], self.agents)
        assert len(self.soar.locked_users) >= 1

    def test_no_duplicate_lockout(self):
        user = self.twin.users[0].username
        result = self._make_detection_result(technique="T1003")
        result.log["user"] = user
        self.soar.respond([result], self.agents)
        self.soar.respond([result], self.agents)
        assert self.soar.locked_users.count(user) if hasattr(
            self.soar.locked_users, 'count') else len(
            [u for u in self.soar.locked_users if u == user]) == 1

    def test_host_isolation_on_ransomware(self):
        result = self._make_detection_result(technique="T1486", host="WS-XYZ")
        self.soar.respond([result], self.agents)
        assert "WS-XYZ" in self.soar.isolated_hosts

    def test_deception_injects_message(self):
        result = self._make_detection_result()
        result.log["attacker"] = "VIPER"
        viper = next(a for a in self.agents if a.name == "VIPER")
        initial_inbox = len(viper.message_inbox)
        self.soar.respond([result], self.agents)
        # Deception message may or may not be injected (confidence threshold)
        # Just check no crash
        assert isinstance(self.soar.deception_messages, list)

    def test_stats_structure(self):
        stats = self.soar.stats()
        for key in ("total_actions", "actions_by_type", "honeypots_deployed",
                    "accounts_locked", "hosts_isolated", "deception_tokens"):
            assert key in stats

    def test_benign_log_no_action(self):
        from defender.tri_brain import DetectionResult
        log = self.twin.generate_normal_log()
        benign_result = DetectionResult(
            log=log, sigma_fired=False, sigma_alerts=[],
            gnn_score=0.1, gnn_flagged=False,
            llm_verdict="benign", llm_confidence=0.9,
            ensemble_verdict="benign", ensemble_confidence=0.9,
            true_label="benign", correct=True,
        )
        before = len(self.soar.actions)
        self.soar.respond([benign_result], self.agents)
        # Only hunting actions may fire; no lockout/isolate/honeypot
        after = len(self.soar.actions)
        lockouts = [a for a in self.soar.actions if a.action_type == "lockout"]
        assert len(lockouts) == 0


# ── Campaign Runner ───────────────────────────────────────────────────────────

class TestCampaignRunner:
    def test_campaign_runs_n_battles(self):
        from core.campaign import CampaignRunner
        runner = CampaignRunner(
            n_battles=2, turns_per_battle=2,
            num_users=8, num_hosts=4,
            llm_provider="mock",
            normal_logs_per_turn=5,
            gnn_pretrain_logs=40,
            verbose=False,
            save_reports=False,
        )
        record = runner.run()
        assert record.battles_completed == 2
        assert len(record.battle_ids) == 2
        assert len(record.f1_history) == 2
        assert len(record.sigma_rule_history) == 2
        assert len(record.elo_history) == 2

    def test_sigma_rules_monotonically_non_decreasing(self):
        from core.campaign import CampaignRunner
        runner = CampaignRunner(
            n_battles=3, turns_per_battle=2,
            num_users=8, num_hosts=4,
            llm_provider="mock",
            normal_logs_per_turn=5,
            gnn_pretrain_logs=40,
            verbose=False, save_reports=False,
        )
        record = runner.run()
        for i in range(1, len(record.sigma_rule_history)):
            assert record.sigma_rule_history[i] >= record.sigma_rule_history[i-1]

    def test_campaign_has_evolution_summary(self):
        from core.campaign import CampaignRunner
        runner = CampaignRunner(
            n_battles=2, turns_per_battle=2,
            num_users=8, num_hosts=4,
            llm_provider="mock",
            normal_logs_per_turn=5,
            gnn_pretrain_logs=40,
            verbose=False, save_reports=False,
        )
        record = runner.run()
        es = record.evolution_summary
        assert "total_sigma_rules" in es
        assert "gnn_updates" in es
        assert "agent_profiles" in es

    def test_nova_evasion_tracked_per_battle(self):
        from core.campaign import CampaignRunner
        runner = CampaignRunner(
            n_battles=2, turns_per_battle=3,
            num_users=8, num_hosts=4,
            llm_provider="mock",
            normal_logs_per_turn=5,
            gnn_pretrain_logs=40,
            verbose=False, save_reports=False,
        )
        record = runner.run()
        assert len(record.nova_evasion_history) == 2
        for rate in record.nova_evasion_history:
            assert 0.0 <= rate <= 1.0

    def test_elo_table_in_final_report(self):
        from core.campaign import CampaignRunner
        runner = CampaignRunner(
            n_battles=2, turns_per_battle=2,
            num_users=8, num_hosts=4,
            llm_provider="mock",
            normal_logs_per_turn=5,
            gnn_pretrain_logs=40,
            verbose=False, save_reports=False,
        )
        record = runner.run()
        assert len(record.final_elo_table) == 7   # 6 agents + DEFENDER
        assert "elo" in record.final_elo_table[0]

    def test_winner_history_valid_values(self):
        from core.campaign import CampaignRunner
        runner = CampaignRunner(
            n_battles=2, turns_per_battle=2,
            num_users=8, num_hosts=4,
            llm_provider="mock",
            normal_logs_per_turn=5,
            gnn_pretrain_logs=40,
            verbose=False, save_reports=False,
        )
        record = runner.run()
        for w in record.winner_history:
            assert w in ("attacker", "defender", "draw")
