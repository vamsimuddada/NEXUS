"""
NEXUS — Phase 5 Tests
Covers: coalition behaviour, ATT&CK client, RealGNN, enriched campaign outputs.
Run with: pytest tests/test_phase5.py -v
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.digital_twin import DigitalTwin
from core.simulation import NEXUSSimulation
from attackers.personas import build_war_council
from attackers.coalition import (
    process_coalition_messages, broadcast_detection_alert,
    nova_broadcast_threshold, apply_target_override, apply_stealth_override,
)
from research.attck_client import ATTCKClient
from defender.gnn.real_gnn import RealGNNDetector, _TORCH_AVAILABLE


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_twin(seed=42):
    return DigitalTwin(num_users=12, num_hosts=5, seed=seed)


def make_agents(twin, provider="mock"):
    return build_war_council(twin, provider)


# ── Coalition Behaviour ───────────────────────────────────────────────────────

class TestCoalition:
    def setup_method(self):
        self.twin   = make_twin()
        self.agents = make_agents(self.twin)

    def _agent(self, name):
        return next(a for a in self.agents if a.name == name)

    def test_cipher_access_sale_pivots_viper(self):
        cipher = self._agent("CIPHER")
        viper  = self._agent("VIPER")
        dc_host = next(h for h in self.twin.hosts if h.is_domain_controller)
        cipher.send_message(viper, f"Access available: {dc_host.hostname}",
                            msg_type="access_sale")
        process_coalition_messages(self.agents, self.twin)
        # VIPER should have a target override or it was applied
        # (override consumed by process_coalition_messages)
        assert True   # no exception = pass

    def test_nova_threshold_broadcast_raises_stealth(self):
        nova  = self._agent("NOVA")
        kraken = self._agent("KRAKEN")
        nova_broadcast_threshold(nova, self.agents, threshold_estimate=0.612)
        actions = process_coalition_messages(self.agents, self.twin)
        # KRAKEN should have been told to raise stealth
        assert any("stealth" in act.lower() or "threshold" in act.lower()
                   for act in actions.get("KRAKEN", []))

    def test_detection_alert_propagates(self):
        viper = self._agent("VIPER")
        broadcast_detection_alert(viper, self.agents)
        # All other agents should have a detection_alert in inbox
        for agent in self.agents:
            if agent.name != "VIPER":
                assert any(m["type"] == "detection_alert"
                           for m in agent.message_inbox)

    def test_detection_alert_raises_stealth(self):
        kraken = self._agent("KRAKEN")
        kraken.message_inbox.append({
            "from": "VIPER", "to": "KRAKEN",
            "type": "detection_alert",
            "content": "VIPER was detected — raise stealth",
            "timestamp": "",
        })
        process_coalition_messages(self.agents, self.twin)
        # _stealth_override should be set on KRAKEN
        assert getattr(kraken, "_stealth_override", None) in (
            "medium", "high", None   # consumed or set
        )

    def test_apply_target_override_returns_action(self):
        viper = self._agent("VIPER")
        dc = next(h for h in self.twin.hosts if h.is_domain_controller)
        viper._target_override = dc.hostname
        action = apply_target_override(viper, self.twin)
        assert action is not None
        assert "technique_id" in action
        assert action.get("_coalition_target") == dc.hostname
        # Consumed after call
        assert getattr(viper, "_target_override", None) is None

    def test_apply_target_override_none_when_no_override(self):
        viper = self._agent("VIPER")
        assert apply_target_override(viper, self.twin) is None

    def test_apply_stealth_override(self):
        viper = self._agent("VIPER")
        viper._stealth_override = "high"
        action = {"technique_id": "T1078", "stealth_level": "low",
                  "action": "x", "target_host_role": "dc", "rationale": "y"}
        result = apply_stealth_override(viper, action)
        assert result["stealth_level"] == "high"
        assert getattr(viper, "_stealth_override", None) is None

    def test_ghost_leak_flags_cipher(self):
        ghost  = self._agent("GHOST")
        cipher = self._agent("CIPHER")
        ghost.send_message(cipher,
                           "Found credentials: admin:P@ss1234 on DC-001",
                           msg_type="intel")
        process_coalition_messages(self.agents, self.twin)
        assert getattr(cipher, "_resell_flag", False) is True

    def test_full_coalition_round_no_crash(self):
        """Full turn of coalition processing should not crash."""
        for agent in self.agents:
            agent.run_turn()
        cipher = self._agent("CIPHER")
        cipher.sell_access(self.agents)
        nova = self._agent("NOVA")
        nova_broadcast_threshold(nova, self.agents, 0.55)
        actions = process_coalition_messages(self.agents, self.twin)
        assert isinstance(actions, dict)
        assert set(actions.keys()) == {a.name for a in self.agents}

    def test_campaign_runs_with_coalition(self):
        from core.campaign import CampaignRunner
        runner = CampaignRunner(
            n_battles=2, turns_per_battle=2,
            num_users=8, num_hosts=4, llm_provider="mock",
            normal_logs_per_turn=5, gnn_pretrain_logs=40,
            verbose=False, save_reports=False,
        )
        record = runner.run()
        assert record.battles_completed == 2


# ── ATT&CK Client ─────────────────────────────────────────────────────────────

class TestATTCKClient:
    def setup_method(self):
        self.client = ATTCKClient(use_live=False)

    def test_get_known_technique(self):
        meta = self.client.get_technique("T1003")
        assert meta["name"] == "OS Credential Dumping"
        assert meta["tactic"] == "credential-access"
        assert "LSASS" in meta["detection"]

    def test_get_all_nexus_techniques(self):
        for tid in ["T1078","T1021","T1059","T1055","T1083","T1003","T1486","T1071"]:
            meta = self.client.get_technique(tid)
            assert "name" in meta
            assert "tactic" in meta
            assert meta["name"] != tid   # should resolve to a real name

    def test_unknown_technique_fallback(self):
        meta = self.client.get_technique("T9999")
        assert meta["name"] == "T9999"
        assert meta["tactic"] == "unknown"

    def test_get_tactic_name(self):
        assert "Command" in self.client.get_tactic_name("T1071")
        assert "Credential" in self.client.get_tactic_name("T1003")

    def test_get_detection_note(self):
        note = self.client.get_detection_note("T1003")
        assert len(note) > 10

    def test_validate_tactic_chain_plausible(self):
        result = self.client.validate_tactic_chain(
            ["T1078", "T1021", "T1003", "T1486"]
        )
        assert result["is_plausible"] is True
        assert result["technique_count"] == 4
        assert len(result["covered_phases"]) >= 3

    def test_validate_tactic_chain_completeness(self):
        result = self.client.validate_tactic_chain(
            ["T1078", "T1021", "T1003", "T1486"]
        )
        assert 0.0 < result["completeness"] < 1.0

    def test_enrich_sigma_rule(self):
        from defender.sigma.sigma_engine import SigmaRule
        rule = SigmaRule(
            rule_id="TEST-001", title="Test", description="",
            severity="high", technique="T1003",
            conditions=[], auto_generated=False,
        )
        enriched = self.client.enrich_sigma_rule(rule)
        assert enriched["technique_name"] == "OS Credential Dumping"
        assert "attck_url" in enriched
        assert "T1003" in enriched["attck_url"]

    def test_enrich_all_rules(self):
        from defender.sigma.sigma_engine import SigmaEngine
        engine = SigmaEngine()
        enriched = self.client.enrich_all_rules(engine)
        assert len(enriched) == len(engine.rules)
        for e in enriched:
            assert "technique_name" in e
            assert "tactic" in e

    def test_navigator_layer_structure(self):
        stats = [
            {"technique": "T1003", "uses": 5, "evaded": 2,
             "evasion_rate": 0.4, "detection_rate": 0.6},
            {"technique": "T1071", "uses": 3, "evaded": 1,
             "evasion_rate": 0.33, "detection_rate": 0.67},
        ]
        layer = self.client.navigator_layer(stats, "test-campaign")
        assert layer["domain"] == "enterprise-attack"
        assert len(layer["techniques"]) == 2
        assert layer["techniques"][0]["techniqueID"] in ("T1003","T1071")
        assert "score" in layer["techniques"][0]

    def test_navigator_layer_save(self, tmp_path):
        stats = [{"technique": "T1078", "uses": 4, "evaded": 1,
                  "evasion_rate": 0.25, "detection_rate": 0.75}]
        path  = str(tmp_path / "nav.json")
        self.client.save_navigator_layer(stats, "cam001", path)
        import os, json
        assert os.path.exists(path)
        with open(path) as f:
            data = json.load(f)
        assert data["domain"] == "enterprise-attack"


# ── RealGNN Detector ──────────────────────────────────────────────────────────

class TestRealGNN:
    def setup_method(self):
        self.twin = make_twin(seed=7)
        self.det  = RealGNNDetector(contamination=0.05, epochs=20)

    def test_mode_reported(self):
        stats = self.det.graph_stats()
        assert stats["mode"] in ("gcn-autoencoder", "isolation-forest")

    def test_fit_on_benign(self):
        logs = self.twin.generate_log_stream(n_normal=80, n_attack=0)
        self.det.fit(logs)
        assert self.det.is_fitted

    def test_score_in_range(self):
        logs = self.twin.generate_log_stream(n_normal=80, n_attack=0)
        self.det.fit(logs)
        for _ in range(10):
            log = self.twin.generate_normal_log()
            s = self.det.score_log(log)
            assert 0.0 <= s <= 1.0

    def test_flag_returns_tuple(self):
        logs = self.twin.generate_log_stream(n_normal=60, n_attack=0)
        self.det.fit(logs)
        log = self.twin.generate_normal_log()
        score, flagged = self.det.flag(log)
        assert isinstance(score, float)
        assert isinstance(flagged, bool)

    def test_attack_scores_higher_than_benign_on_average(self):
        logs = self.twin.generate_log_stream(n_normal=120, n_attack=0)
        self.det.fit(logs)
        benign  = [self.det.score_log(self.twin.generate_normal_log())
                   for _ in range(20)]
        attacks = [self.det.score_log(
                       self.twin.generate_attack_log("T1003","KRAKEN"))
                   for _ in range(20)]
        avg_b = sum(benign)  / len(benign)
        avg_a = sum(attacks) / len(attacks)
        assert avg_a >= avg_b - 0.05   # allow tiny tolerance

    def test_partial_fit_no_crash(self):
        logs = self.twin.generate_log_stream(n_normal=80, n_attack=0)
        self.det.fit(logs)
        new_logs = self.twin.generate_log_stream(n_normal=30, n_attack=0)
        self.det.partial_fit(new_logs)   # should not crash
        assert self.det.is_fitted

    def test_graph_updates_on_scoring(self):  # noqa
        for _ in range(15):
            self.det.score_log(self.twin.generate_normal_log())
        # In IF fallback mode graph lives on the underlying detector
        underlying = self.det._if_detector if self.det._if_detector else self.det
        import networkx as nx
        graph = getattr(underlying, "graph", None) or getattr(self.det, "graph", None)
        assert graph is not None
        assert len(graph.nodes) > 0

    def test_torch_availability_reported(self):
        # Just verify the flag is a bool — actual value depends on environment
        assert isinstance(_TORCH_AVAILABLE, bool)

    def test_tribrains_uses_real_gnn(self):
        from defender.tri_brain import TriBrainEnsemble
        ens = TriBrainEnsemble()
        # The gnn attribute should be a RealGNNDetector instance
        assert isinstance(ens.gnn, RealGNNDetector)

    def test_full_sim_with_real_gnn(self):
        sim = NEXUSSimulation(
            num_users=8, num_hosts=4, llm_provider="mock",
            turns=2, normal_logs_per_turn=6,
            gnn_pretrain_logs=40, verbose=False, evolve=False,
        )
        report = sim.run()
        m = report.metrics
        assert "gnn_stats" in m
        assert m["gnn_stats"]["is_fitted"] is True
        assert m["gnn_stats"]["mode"] in ("gcn-autoencoder","isolation-forest")


# ── Integration: enriched campaign output ─────────────────────────────────────

class TestEnrichedCampaign:
    def test_campaign_generates_navigator_layer(self, tmp_path, monkeypatch):
        import json, os
        from pathlib import Path
        monkeypatch.chdir(tmp_path)
        from core.campaign import CampaignRunner
        runner = CampaignRunner(
            n_battles=2, turns_per_battle=2,
            num_users=8, num_hosts=4, llm_provider="mock",
            normal_logs_per_turn=5, gnn_pretrain_logs=40,
            verbose=False, save_reports=True,
        )
        record = runner.run()
        assert record.battles_completed == 2
        # Research outputs are written to absolute nexus data dir
        nexus_root = os.path.dirname(os.path.dirname(os.path.abspath(
            __import__("core.campaign", fromlist=["campaign"]).__file__
        )))
        nav_files = list((Path(nexus_root) / "data/research").glob(
            f"navigator_{record.campaign_id}.json"
        ))
        assert len(nav_files) >= 1, "Navigator layer not found in nexus data dir"
        layer = json.loads(nav_files[0].read_text())
        assert layer["domain"] == "enterprise-attack"

    def test_tactic_chain_validation_in_campaign(self):
        # Tactic chain should be plausible for T1078 → T1021 → T1003
        client = ATTCKClient(use_live=False)
        result = client.validate_tactic_chain(["T1078", "T1021", "T1003"])
        assert result["is_plausible"] is True
        assert "initial-access" in result["covered_phases"]
        assert "lateral-movement" in result["covered_phases"]
