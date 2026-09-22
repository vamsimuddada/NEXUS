"""
NEXUS — Gemini Provider Tests
Tests the GeminiProvider class and its integration with all NEXUS components.
These pass whether or not a real GEMINI_API_KEY is set.
Run with: pytest tests/test_gemini.py -v
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.gemini_provider import GeminiProvider, get_gemini
from core.digital_twin import DigitalTwin
from core.simulation import NEXUSSimulation


# ── GeminiProvider unit tests ─────────────────────────────────────────────────

class TestGeminiProvider:
    def test_instantiates_without_key(self):
        p = GeminiProvider(api_key="")
        assert isinstance(p, GeminiProvider)

    def test_available_false_without_key(self):
        p = GeminiProvider(api_key="")
        assert p.available is False

    def test_call_returns_empty_without_key(self):
        p = GeminiProvider(api_key="")
        result = p.call("Hello")
        assert result == ""

    def test_call_json_returns_none_without_key(self):
        p = GeminiProvider(api_key="")
        result = p.call_json("Return JSON")
        assert result is None

    def test_get_gemini_singleton(self):
        """get_gemini() returns the same instance each call."""
        import importlib
        import core.gemini_provider as gm
        gm._provider = None   # reset singleton
        p1 = get_gemini(api_key="")
        p2 = get_gemini(api_key="")
        assert p1 is p2
        gm._provider = None   # clean up

    def test_default_model_set(self):
        p = GeminiProvider(api_key="")
        assert "gemini" in p.model.lower()

    def test_custom_model_respected(self):
        p = GeminiProvider(api_key="", model="gemini-1.5-flash")
        assert p.model == "gemini-1.5-flash"

    def test_env_model_override(self, monkeypatch):
        monkeypatch.setenv("NEXUS_GEMINI_MODEL", "gemini-1.5-flash-8b")
        p = GeminiProvider(api_key="")
        assert p.model == "gemini-1.5-flash-8b"

    def test_env_key_read(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "test-key-123")
        p = GeminiProvider()
        assert p.api_key == "test-key-123"


# ── Integration: gemini provider with mock fallback ──────────────────────────

class TestGeminiIntegration:
    """
    These tests use provider="gemini" but without a real key,
    so they fall back to mock — verifying the fallback path works correctly.
    """

    def test_simulation_runs_with_gemini_provider(self):
        """Simulation with provider='gemini' falls back gracefully to mock."""
        sim = NEXUSSimulation(
            num_users=8, num_hosts=4, llm_provider="gemini",
            turns=2, normal_logs_per_turn=5,
            gnn_pretrain_logs=30, verbose=False, evolve=False,
        )
        report = sim.run()
        # Should complete without error — mock fallback activates
        assert report.battle_id is not None
        assert len(report.attacker_logs) == 2 * 6

    def test_debate_engine_with_gemini_provider(self):
        """Debate engine with gemini falls back to heuristic without key."""
        from defender.llm.debate_engine import LLMDebateEngine
        twin   = DigitalTwin(num_users=8, num_hosts=4, seed=1)
        engine = LLMDebateEngine(provider="gemini")
        # Should use heuristic fallback (no API key)
        log    = twin.generate_attack_log("T1003", "KRAKEN")
        verdict, conf = engine.evaluate(log, [], 0.8)
        assert verdict in ("malicious", "benign", "uncertain")
        assert 0.0 <= conf <= 1.0

    def test_evolution_engine_with_gemini_provider(self):
        """Rule rewriter with gemini falls back to template without key."""
        from defender.sigma.sigma_engine import SigmaEngine
        from evolution.evolution_engine import RuleRewriter
        sigma   = SigmaEngine()
        rewriter = RuleRewriter(sigma, provider="gemini")
        new_rules = rewriter.rewrite_for_missed(["T1562"], [])
        # Template fallback should produce a rule
        assert len(new_rules) == 1
        assert new_rules[0].technique == "T1562"

    def test_paper_generator_with_gemini_provider(self):
        """Paper generator with gemini falls back to template without key."""
        from research.paper_generator import PaperSectionGenerator
        from core.campaign import CampaignRunner
        runner = CampaignRunner(
            n_battles=2, turns_per_battle=2,
            num_users=8, num_hosts=4, llm_provider="mock",
            normal_logs_per_turn=5, gnn_pretrain_logs=30,
            verbose=False, save_reports=False,
        )
        record = runner.run()
        gen    = PaperSectionGenerator(provider="gemini")
        # Abstract should use template fallback
        abstract = gen.abstract(record)
        assert isinstance(abstract, str)
        assert len(abstract) > 50

    def test_campaign_with_gemini_provider(self):
        """Full campaign with gemini provider uses mock fallback throughout."""
        from core.campaign import CampaignRunner
        runner = CampaignRunner(
            n_battles=2, turns_per_battle=2,
            num_users=8, num_hosts=4, llm_provider="gemini",
            normal_logs_per_turn=5, gnn_pretrain_logs=30,
            verbose=False, save_reports=False,
        )
        record = runner.run()
        assert record.battles_completed == 2
        assert len(record.f1_history) == 2


# ── Real API test (skipped without key) ──────────────────────────────────────

class TestGeminiRealAPI:
    """
    Only runs when GEMINI_API_KEY is set in the environment.
    Skip these in CI or when testing without a key.
    """

    def _skip_if_no_key(self):
        import pytest
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set — skipping live API test")

    def test_real_api_returns_text(self):
        self._skip_if_no_key()
        p      = GeminiProvider()
        result = p.call("Say 'NEXUS test OK' and nothing else.")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_real_api_returns_json(self):
        self._skip_if_no_key()
        p      = GeminiProvider()
        result = p.call_json(
            'Return a JSON object with key "status" set to "ok".'
        )
        assert result is not None
        assert isinstance(result, dict)

    def test_real_attacker_decision(self):
        self._skip_if_no_key()
        twin   = DigitalTwin(num_users=10, num_hosts=5, seed=42)
        agents = __import__(
            "attackers.personas", fromlist=["build_war_council"]
        ).build_war_council(twin, "gemini")
        viper  = next(a for a in agents if a.name == "VIPER")
        action = viper.decide_next_action()
        assert "technique_id" in action
        assert "stealth_level" in action

    def test_real_gemini_in_simulation(self):
        self._skip_if_no_key()
        sim = NEXUSSimulation(
            num_users=10, num_hosts=5, llm_provider="gemini",
            turns=2, normal_logs_per_turn=8,
            gnn_pretrain_logs=60, verbose=True, evolve=True,
        )
        report = sim.run()
        assert report.winner in ("attacker", "defender", "draw")
        m = report.metrics
        assert m["total_analyzed"] > 0
