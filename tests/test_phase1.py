"""
NEXUS — Phase 1 Tests
Run with: pytest tests/test_phase1.py -v
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.digital_twin import DigitalTwin, ADUser, Host
from attackers.personas import build_war_council, VIPER, NOVA
from defender.sigma.sigma_engine import SigmaEngine, SigmaRule
from defender.tri_brain import TriBrainEnsemble


# ── Digital Twin ──────────────────────────────────────────────────────────────

class TestDigitalTwin:
    def setup_method(self):
        self.twin = DigitalTwin(num_users=10, num_hosts=5, seed=1)

    def test_has_users(self):
        assert len(self.twin.users) == 10

    def test_has_hosts(self):
        assert len(self.twin.hosts) == 5

    def test_has_domain_controller(self):
        dcs = [h for h in self.twin.hosts if h.is_domain_controller]
        assert len(dcs) >= 1

    def test_has_admin_user(self):
        admins = [u for u in self.twin.users if u.is_admin]
        assert len(admins) >= 1

    def test_normal_log_structure(self):
        log = self.twin.generate_normal_log()
        assert "timestamp" in log
        assert "event_id" in log
        assert "user" in log
        assert "host" in log
        assert log["label"] == "benign"
        assert log["attack_technique"] is None

    def test_attack_log_structure(self):
        log = self.twin.generate_attack_log("T1078", "VIPER")
        assert log["label"] == "malicious"
        assert log["attack_technique"] == "T1078"
        assert log["attacker"] == "VIPER"

    def test_log_stream(self):
        logs = self.twin.generate_log_stream(n_normal=50, n_attack=10)
        assert len(logs) == 60
        malicious = [l for l in logs if l["label"] == "malicious"]
        assert len(malicious) == 10

    def test_summary(self):
        s = self.twin.summary()
        assert "corp.local" in s
        assert "users=10" in s


# ── Attacker Personas ─────────────────────────────────────────────────────────

class TestAttackers:
    def setup_method(self):
        self.twin = DigitalTwin(num_users=10, num_hosts=5, seed=2)
        self.agents = build_war_council(self.twin, llm_provider="mock")

    def test_six_agents_created(self):
        assert len(self.agents) == 6

    def test_all_agents_have_names(self):
        names = {a.name for a in self.agents}
        assert names == {"VIPER", "KRAKEN", "GHOST", "HYDRA", "NOVA", "CIPHER"}

    def test_agent_run_turn_produces_log(self):
        viper = next(a for a in self.agents if a.name == "VIPER")
        log = viper.run_turn()
        assert log["label"] == "malicious"
        assert log["attacker"] == "VIPER"
        assert log["attack_technique"] is not None

    def test_llm_action_is_constrained_to_persona_techniques(self):
        viper = next(a for a in self.agents if a.name == "VIPER")
        action = viper._parse_action("""{
            "action": "unsupported move",
            "technique_id": "T0120",
            "target_host_role": "dc",
            "rationale": "test",
            "stealth_level": "high"
        }""")
        assert action["technique_id"] in viper.preferred_techniques

    def test_inter_agent_messaging(self):
        viper = next(a for a in self.agents if a.name == "VIPER")
        nova = next(a for a in self.agents if a.name == "NOVA")
        viper.send_message(nova, "DC admin credentials found", msg_type="intel")
        assert len(nova.message_inbox) == 1
        assert nova.message_inbox[0]["from"] == "VIPER"

    def test_campaign_state_advances(self):
        agent = self.agents[0]
        for _ in range(6):
            agent.run_turn()
        assert agent.state.turn == 6
        assert len(agent.state.compromised_hosts) > 0

    def test_agent_status(self):
        agent = self.agents[0]
        status = agent.status()
        assert "agent" in status
        assert "elo" in status
        assert "phase" in status


# ── SIGMA Engine ──────────────────────────────────────────────────────────────

class TestSigmaEngine:
    def setup_method(self):
        self.engine = SigmaEngine()
        self.twin = DigitalTwin(num_users=5, num_hosts=3, seed=3)

    def test_baseline_rules_loaded(self):
        assert len(self.engine.rules) == 10

    def test_rule_matches_attack_log(self):
        log = self.twin.generate_attack_log("T1003", "KRAKEN")
        alerts = self.engine.analyze_log(log)
        assert any(a.technique == "T1003" for a in alerts)

    def test_no_alert_on_normal_log(self):
        # Normal logs shouldn't trigger most rules
        # (some may fire on event_id 4624 which is normal login)
        log = self.twin.generate_normal_log()
        log["event_id"] = 4634   # logoff — should not trigger any rule
        log["label"] = "benign"
        log["attack_technique"] = None
        log["is_admin"] = False
        log["host"] = "WS-123"
        alerts = self.engine.analyze_log(log)
        assert len(alerts) == 0

    def test_add_custom_rule(self):
        rule = SigmaRule(
            rule_id="SIG-TEST-001",
            title="Test Rule",
            description="Test",
            severity="low",
            technique="T1099",
            conditions=[{"field": "event_id", "operator": "eq", "value": 9999}],
        )
        self.engine.add_rule(rule)
        assert len(self.engine.rules) == 11

    def test_missed_techniques_detection(self):
        logs = [self.twin.generate_attack_log("T1486", "KRAKEN") for _ in range(5)]
        # T1486 requires specific conditions, may be in missed
        missed = self.engine.get_missed_techniques(logs)
        assert isinstance(missed, list)

    def test_stats(self):
        stats = self.engine.stats()
        assert "total_rules" in stats
        assert stats["total_rules"] == 10


# ── Tri-Brain Ensemble ────────────────────────────────────────────────────────

class TestTriBrain:
    def setup_method(self):
        self.twin = DigitalTwin(num_users=10, num_hosts=5, seed=4)
        self.defender = TriBrainEnsemble()

    def test_analyze_malicious_log(self):
        log = self.twin.generate_attack_log("T1003", "KRAKEN")
        result = self.defender.analyze(log)
        assert result.true_label == "malicious"
        assert result.ensemble_verdict in {"malicious", "benign"}

    def test_supported_attack_signatures_are_not_missed(self):
        techniques = {
            "T1078", "T1021", "T1083", "T1071", "T1059", "T1486",
            "T1003", "T1055",
        }
        for technique in techniques:
            log = self.twin.generate_attack_log(technique, "TEST")
            result = self.defender.analyze(log)
            assert result.signature_matched is True
            assert result.ensemble_verdict == "malicious"

    def test_analyze_benign_log(self):
        log = self.twin.generate_normal_log()
        result = self.defender.analyze(log)
        assert result.true_label == "benign"

    def test_metrics_populated(self):
        logs = (
            [self.twin.generate_attack_log("T1003", "VIPER") for _ in range(10)]
            + [self.twin.generate_normal_log() for _ in range(10)]
        )
        self.defender.analyze_stream(logs)
        m = self.defender.metrics()
        assert m["total_analyzed"] == 20
        assert 0.0 <= m["f1_score"] <= 1.0


# ── Full Simulation ───────────────────────────────────────────────────────────

class TestSimulation:
    def test_full_run(self):
        from core.simulation import NEXUSSimulation
        sim = NEXUSSimulation(
            num_users=10, num_hosts=5, llm_provider="mock",
            turns=3, normal_logs_per_turn=5, verbose=False
        )
        report = sim.run()
        assert report.battle_id is not None
        assert len(report.attacker_logs) == 3 * 6  # 3 turns × 6 agents
        assert report.winner in {"attacker", "defender", "draw"}
        assert "f1_score" in report.metrics
