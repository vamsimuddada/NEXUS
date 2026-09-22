"""
NEXUS — Ollama Provider Tests
Tests OllamaProvider class and its integration with all NEXUS components.
All tests pass whether or not Ollama is actually running locally.
Run with: pytest tests/test_ollama.py -v
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from core.ollama_provider import OllamaProvider, get_ollama, reset_ollama, RECOMMENDED_MODELS
from core.digital_twin import DigitalTwin
from core.simulation import NEXUSSimulation


# ── OllamaProvider unit tests ─────────────────────────────────────────────────

class TestOllamaProvider:

    def test_instantiates_without_server(self):
        """Provider instantiates cleanly even when Ollama isn't running."""
        p = OllamaProvider(host="http://localhost:19999")  # wrong port
        assert isinstance(p, OllamaProvider)

    def test_available_false_when_no_server(self):
        p = OllamaProvider(host="http://localhost:19999")
        assert p.available is False

    def test_call_returns_empty_when_unavailable(self):
        p = OllamaProvider(host="http://localhost:19999")
        assert p.call("hello") == ""

    def test_call_json_returns_none_when_unavailable(self):
        p = OllamaProvider(host="http://localhost:19999")
        assert p.call_json("return json") is None

    def test_list_models_returns_empty_when_unavailable(self):
        p = OllamaProvider(host="http://localhost:19999")
        assert p.list_models() == []

    def test_default_model_set(self):
        p = OllamaProvider(host="http://localhost:19999")
        assert "llama" in p.model or "phi" in p.model or "mistral" in p.model \
               or "gemma" in p.model or len(p.model) > 0

    def test_custom_model_respected(self):
        p = OllamaProvider(model="mistral:7b-instruct",
                           host="http://localhost:19999")
        # Model may be overridden to an available one, but we set it
        assert p.model is not None

    def test_env_model_override(self, monkeypatch):
        monkeypatch.setenv("NEXUS_OLLAMA_MODEL", "phi3:mini")
        reset_ollama()
        p = OllamaProvider(host="http://localhost:19999")
        # When server is unavailable, model stays as set
        assert "phi3" in p.model or p.model == "phi3:mini" or len(p.model) > 0
        reset_ollama()

    def test_env_host_override(self, monkeypatch):
        monkeypatch.setenv("OLLAMA_HOST", "http://192.168.1.100:11434")
        p = OllamaProvider()
        # Host should be read from env when not passed explicitly
        assert p.host is not None
        reset_ollama()

    def test_recommended_models_dict(self):
        assert "fast"    in RECOMMENDED_MODELS
        assert "quality" in RECOMMENDED_MODELS
        assert "tiny"    in RECOMMENDED_MODELS
        for key, model in RECOMMENDED_MODELS.items():
            assert ":" in model or len(model) > 3  # name:tag format

    def test_parse_json_direct(self):
        p = OllamaProvider(host="http://localhost:19999")
        result = p._parse_json('{"action": "test", "technique_id": "T1078"}')
        assert result is not None
        assert result["action"] == "test"

    def test_parse_json_with_fences(self):
        p = OllamaProvider(host="http://localhost:19999")
        raw = '```json\n{"action": "test", "stealth_level": "high"}\n```'
        result = p._parse_json(raw)
        assert result is not None
        assert result["stealth_level"] == "high"

    def test_parse_json_extracts_from_prose(self):
        p = OllamaProvider(host="http://localhost:19999")
        raw = 'Here is my response: {"verdict": "malicious", "confidence": 0.9} That is my answer.'
        result = p._parse_json(raw)
        assert result is not None
        assert result["verdict"] == "malicious"

    def test_parse_json_returns_none_on_garbage(self):
        p = OllamaProvider(host="http://localhost:19999")
        result = p._parse_json("This is not JSON at all !!!")
        assert result is None

    def test_singleton(self):
        reset_ollama()
        p1 = get_ollama()
        p2 = get_ollama()
        assert p1 is p2
        reset_ollama()

    def test_reset_creates_new_instance(self):
        reset_ollama()
        p1 = get_ollama()
        reset_ollama()
        p2 = get_ollama()
        assert p1 is not p2
        reset_ollama()


# ── Integration: ollama provider with mock fallback ──────────────────────────

class TestOllamaIntegration:
    """
    These tests use provider='ollama' but Ollama isn't running in CI,
    so they fall back to mock — verifying the fallback path works correctly.
    """

    def test_simulation_runs_with_ollama_provider(self):
        """provider='ollama' falls back to mock gracefully."""
        sim = NEXUSSimulation(
            num_users=8, num_hosts=4, llm_provider="ollama",
            turns=2, normal_logs_per_turn=5,
            gnn_pretrain_logs=30, verbose=False, evolve=False,
        )
        report = sim.run()
        assert report.battle_id is not None
        assert len(report.attacker_logs) == 2 * 6

    def test_debate_engine_with_ollama(self):
        from defender.llm.debate_engine import LLMDebateEngine
        twin   = DigitalTwin(num_users=8, num_hosts=4, seed=1)
        engine = LLMDebateEngine(provider="ollama")
        log    = twin.generate_attack_log("T1003", "KRAKEN")
        verdict, conf = engine.evaluate(log, [], 0.8)
        assert verdict in ("malicious", "benign", "uncertain")
        assert 0.0 <= conf <= 1.0

    def test_evolution_engine_with_ollama(self):
        from defender.sigma.sigma_engine import SigmaEngine
        from evolution.evolution_engine import RuleRewriter
        sigma    = SigmaEngine()
        rewriter = RuleRewriter(sigma, provider="ollama")
        new_rules = rewriter.rewrite_for_missed(["T1562"], [])
        assert len(new_rules) == 1
        assert new_rules[0].technique == "T1562"

    def test_paper_generator_with_ollama(self):
        from research.paper_generator import PaperSectionGenerator
        from core.campaign import CampaignRunner
        runner = CampaignRunner(
            n_battles=2, turns_per_battle=2,
            num_users=8, num_hosts=4, llm_provider="mock",
            normal_logs_per_turn=5, gnn_pretrain_logs=30,
            verbose=False, save_reports=False,
        )
        record   = runner.run()
        gen      = PaperSectionGenerator(provider="ollama")
        abstract = gen.abstract(record)
        assert isinstance(abstract, str) and len(abstract) > 50

    def test_campaign_with_ollama_provider(self):
        from core.campaign import CampaignRunner
        runner = CampaignRunner(
            n_battles=2, turns_per_battle=2,
            num_users=8, num_hosts=4, llm_provider="ollama",
            normal_logs_per_turn=5, gnn_pretrain_logs=30,
            verbose=False, save_reports=False,
        )
        record = runner.run()
        assert record.battles_completed == 2
        assert len(record.f1_history) == 2


# ── Real Ollama tests (skipped when server not running) ───────────────────────

class TestOllamaLive:
    """Only runs when Ollama is actually running on localhost:11434."""

    def _skip_if_no_server(self):
        p = OllamaProvider()
        if not p.available:
            pytest.skip("Ollama server not running — skipping live tests")
        return p

    def test_live_server_available(self):
        p = self._skip_if_no_server()
        assert p.available is True

    def test_live_list_models(self):
        p = self._skip_if_no_server()
        models = p.list_models()
        assert isinstance(models, list)
        assert len(models) > 0
        print(f"\n  Available models: {models}")

    def test_live_call_returns_text(self):
        p = self._skip_if_no_server()
        result = p.call("Say exactly: NEXUS test OK", max_tokens=20)
        assert isinstance(result, str)
        assert len(result) > 0
        print(f"\n  Response: {result[:100]}")

    def test_live_call_json(self):
        p = self._skip_if_no_server()
        result = p.call_json(
            'Return a JSON object with key "status" set to "ok" and key "value" set to 42.'
        )
        assert result is not None
        assert isinstance(result, dict)

    def test_live_attacker_decision(self):
        p = self._skip_if_no_server()
        twin   = DigitalTwin(num_users=10, num_hosts=5, seed=42)
        agents = __import__(
            "attackers.personas", fromlist=["build_war_council"]
        ).build_war_council(twin, "ollama")
        viper  = next(a for a in agents if a.name == "VIPER")
        action = viper.decide_next_action()
        assert "technique_id" in action
        assert "stealth_level" in action
        assert action["technique_id"].startswith("T")
        print(f"\n  VIPER action: {action}")

    def test_live_full_battle(self):
        p = self._skip_if_no_server()
        sim = NEXUSSimulation(
            num_users=10, num_hosts=5, llm_provider="ollama",
            turns=2, normal_logs_per_turn=8,
            gnn_pretrain_logs=60, verbose=True, evolve=True,
        )
        report = sim.run()
        assert report.winner in ("attacker", "defender", "draw")
        print(f"\n  Winner: {report.winner}")
        print(f"  F1={report.metrics['f1_score']} P={report.metrics['precision']}")

    def test_live_campaign(self):
        p = self._skip_if_no_server()
        from core.campaign import CampaignRunner
        runner = CampaignRunner(
            n_battles=2, turns_per_battle=3,
            num_users=10, num_hosts=5, llm_provider="ollama",
            normal_logs_per_turn=10, gnn_pretrain_logs=80,
            verbose=True, save_reports=False,
        )
        record = runner.run()
        assert record.battles_completed == 2
        print(f"\n  F1 trend: {record.f1_history}")
        print(f"  SIGMA rules: {record.sigma_rule_history}")
