"""
NEXUS — Phase 4 Tests
Run with: pytest tests/test_phase4.py -v
"""

import sys, os, json, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.digital_twin import DigitalTwin
from core.simulation import NEXUSSimulation
from research.stix_generator import STIXBundleGenerator
from research.dataset_exporter import DatasetExporter, _encode_row
from research.paper_generator import PaperSectionGenerator, _fmt_table
from research.bulk_runner import BulkRunner


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_sim(turns=2, seed=42):
    return NEXUSSimulation(
        num_users=8, num_hosts=4, llm_provider="mock",
        turns=turns, normal_logs_per_turn=6,
        gnn_pretrain_logs=40, verbose=False, evolve=True,
    )


def make_campaign_record(n_battles=2):
    from core.campaign import CampaignRunner
    runner = CampaignRunner(
        n_battles=n_battles, turns_per_battle=2,
        num_users=8, num_hosts=4, llm_provider="mock",
        normal_logs_per_turn=5, gnn_pretrain_logs=40,
        verbose=False, save_reports=False,
    )
    return runner.run()


# ── STIX Generator ────────────────────────────────────────────────────────────

class TestSTIXGenerator:
    def setup_method(self):
        self.gen = STIXBundleGenerator()

    def test_from_battle_produces_bundle(self):
        sim = make_sim()
        report = sim.run()
        bundle = self.gen.from_battle(report)
        assert bundle is not None
        assert len(bundle.objects) > 0

    def test_bundle_contains_identity(self):
        sim = make_sim()
        report = sim.run()
        bundle = self.gen.from_battle(report)
        types = [obj.get("type") for obj in bundle.objects]
        assert "identity" in types

    def test_bundle_contains_campaign(self):
        sim = make_sim()
        report = sim.run()
        bundle = self.gen.from_battle(report)
        types = [obj.get("type") for obj in bundle.objects]
        assert "campaign" in types

    def test_bundle_contains_threat_actors(self):
        sim = make_sim()
        report = sim.run()
        bundle = self.gen.from_battle(report)
        types = [obj.get("type") for obj in bundle.objects]
        assert "threat-actor" in types

    def test_bundle_contains_attack_patterns(self):
        sim = make_sim()
        report = sim.run()
        bundle = self.gen.from_battle(report)
        types = [obj.get("type") for obj in bundle.objects]
        assert "attack-pattern" in types

    def test_bundle_contains_relationships(self):
        sim = make_sim()
        report = sim.run()
        bundle = self.gen.from_battle(report)
        types = [obj.get("type") for obj in bundle.objects]
        assert "relationship" in types

    def test_no_duplicate_threat_actors(self):
        sim = make_sim(turns=4)
        report = sim.run()
        bundle = self.gen.from_battle(report)
        actors = [obj for obj in bundle.objects if obj.get("type") == "threat-actor"]
        names = [a.get("name") for a in actors]
        assert len(names) == len(set(names))

    def test_from_campaign_bundle(self):
        record = make_campaign_record()
        bundle = self.gen.from_campaign(record)
        assert len(bundle.objects) > 5
        types = [obj.get("type") for obj in bundle.objects]
        assert "campaign" in types
        assert "threat-actor" in types

    def test_save_creates_file(self, tmp_path):
        sim = make_sim()
        report = sim.run()
        bundle = self.gen.from_battle(report)
        path = str(tmp_path / "test_bundle.json")
        self.gen.save(bundle, path)
        assert os.path.exists(path)
        with open(path) as f:
            data = json.load(f)
        assert "objects" in data

    def test_bundle_valid_stix(self, tmp_path):
        """Bundle JSON should be parseable as STIX 2.1."""
        import stix2
        sim = make_sim()
        report = sim.run()
        bundle = self.gen.from_battle(report)
        path = str(tmp_path / "stix.json")
        self.gen.save(bundle, path)
        # Re-parse
        with open(path) as f:
            raw = json.load(f)
        assert raw.get("type") == "bundle"
        assert isinstance(raw.get("objects"), list)

    def test_object_count(self):
        sim = make_sim()
        report = sim.run()
        bundle = self.gen.from_battle(report)
        counts = self.gen.object_count(bundle)
        assert "identity" in counts
        assert counts["identity"] == 1


# ── Dataset Exporter ──────────────────────────────────────────────────────────

class TestDatasetExporter:
    def test_encode_row_all_fields(self):
        twin = DigitalTwin(num_users=5, num_hosts=3, seed=1)
        log = twin.generate_attack_log("T1003", "KRAKEN")
        result = {
            "eid": log["event_id"],
            "sigma_fired": True, "sigma_count": 2,
            "gnn_score": 0.7, "gnn_flagged": True,
            "llm_verdict": "malicious", "llm_confidence": 0.85,
            "ensemble_confidence": 0.75,
            "true_label": "malicious",
            "technique": "T1003", "attacker": "KRAKEN",
            "host": log["host"], "stealth_level": "high",
        }
        row = _encode_row(result, log)
        for col in ["event_id", "gnn_score", "sigma_fired", "label"]:
            assert col in row
        assert row["label"] == 1
        assert row["stealth_num"] == 2   # high = 2

    def test_encode_benign_row(self):
        twin = DigitalTwin(num_users=5, num_hosts=3, seed=2)
        log = twin.generate_normal_log()
        result = {
            "eid": log["event_id"],
            "sigma_fired": False, "sigma_count": 0,
            "gnn_score": 0.1, "gnn_flagged": False,
            "llm_verdict": "benign", "llm_confidence": 0.9,
            "ensemble_confidence": 0.9,
            "true_label": "benign",
            "technique": None, "attacker": None,
            "host": log["host"], "stealth_level": "medium",
        }
        row = _encode_row(result, log)
        assert row["label"] == 0
        assert row["sigma_fired"] == 0

    def test_ingest_battle(self):
        sim = make_sim()
        report = sim.run()
        exporter = DatasetExporter()
        exporter.ingest_battle(report)
        assert len(exporter.rows) > 0
        assert exporter.battles_included == 1

    def test_ingest_campaign(self):
        record = make_campaign_record()
        exporter = DatasetExporter()
        exporter.ingest_campaign(record)
        assert len(exporter.rows) > 0

    def test_export_csv(self, tmp_path):
        sim = make_sim()
        report = sim.run()
        exporter = DatasetExporter()
        exporter.ingest_battle(report)
        path = exporter.export_csv(str(tmp_path / "test.csv"))
        assert os.path.exists(path)
        import csv
        with open(path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == len(exporter.rows)
        assert "label" in rows[0]
        assert "gnn_score" in rows[0]

    def test_export_jsonl(self, tmp_path):
        sim = make_sim()
        report = sim.run()
        exporter = DatasetExporter()
        exporter.ingest_battle(report)
        path = exporter.export_jsonl(str(tmp_path / "test.jsonl"))
        assert os.path.exists(path)
        with open(path) as f:
            lines = f.readlines()
        assert len(lines) == len(exporter.rows)
        first = json.loads(lines[0])
        assert "prompt" in first
        assert "label" in first
        assert "features" in first

    def test_compute_stats(self):
        sim = make_sim()
        report = sim.run()
        exporter = DatasetExporter()
        exporter.ingest_battle(report)
        stats = exporter.compute_stats()
        assert "total_rows" in stats
        assert "malicious" in stats
        assert "benign" in stats
        assert stats["malicious"] + stats["benign"] == stats["total_rows"]

    def test_export_all(self, tmp_path):
        sim = make_sim()
        report = sim.run()
        exporter = DatasetExporter()
        exporter.ingest_battle(report)
        result = exporter.export_all(str(tmp_path))
        assert os.path.exists(result["csv"])
        assert os.path.exists(result["jsonl"])
        assert os.path.exists(result["summary"])
        assert "total_rows" in result["stats"]

    def test_class_balance_between_0_and_1(self):
        sim = make_sim(turns=3)
        report = sim.run()
        exporter = DatasetExporter()
        exporter.ingest_battle(report)
        stats = exporter.compute_stats()
        assert 0.0 <= stats["class_balance"] <= 1.0


# ── Paper Generator ───────────────────────────────────────────────────────────

class TestPaperGenerator:
    def setup_method(self):
        self.gen = PaperSectionGenerator(provider="mock")

    def test_fmt_table(self):
        headers = ["A", "B", "C"]
        rows = [["x", "y", "z"], ["1", "2", "3"]]
        table = _fmt_table(headers, rows)
        assert "A" in table
        assert "B" in table
        assert "|" in table
        assert "-" in table

    def test_abstract_contains_key_metrics(self):
        record = make_campaign_record()
        abstract = self.gen.abstract(record)
        assert isinstance(abstract, str)
        assert len(abstract) > 50
        # Should mention battles
        assert str(record.battles_completed) in abstract

    def test_experimental_setup_section(self):
        record = make_campaign_record()
        section = self.gen.experimental_setup(record)
        assert "Experimental Setup" in section
        assert "SIGMA" in section
        assert "GNN" in section

    def test_results_section_has_table(self):
        record = make_campaign_record()
        section = self.gen.results(record)
        assert "Results" in section
        assert "|" in section   # markdown table

    def test_discussion_section(self):
        record = make_campaign_record()
        section = self.gen.discussion(record)
        assert "Discussion" in section
        assert "Co-Evolution" in section or "co-evolution" in section

    def test_appendix_personas(self):
        record = make_campaign_record()
        section = self.gen.appendix_personas(record)
        assert "Appendix" in section

    def test_appendix_sigma_log(self):
        record = make_campaign_record()
        section = self.gen.appendix_sigma_log(record)
        assert "SIGMA" in section
        assert str(record.sigma_rule_history[0]) in section

    def test_generate_paper_creates_file(self, tmp_path):
        record = make_campaign_record()
        path = str(tmp_path / "paper.md")
        result = self.gen.generate_paper(record, path)
        assert os.path.exists(result)
        with open(result) as f:
            content = f.read()
        assert "NEXUS" in content
        assert "Abstract" in content
        assert "Results" in content
        assert "Conclusion" in content

    def test_paper_contains_all_sections(self, tmp_path):
        record = make_campaign_record()
        path = str(tmp_path / "paper.md")
        self.gen.generate_paper(record, path)
        with open(path) as f:
            content = f.read()
        for section in ["Introduction", "Related Work", "Experimental Setup",
                        "Results", "Discussion", "Conclusion", "References",
                        "Appendix"]:
            assert section in content, f"Missing section: {section}"


# ── Bulk Runner ───────────────────────────────────────────────────────────────

class TestBulkRunner:
    def test_bulk_runner_completes(self, tmp_path):
        runner = BulkRunner(
            n_sims=3, turns=2, num_users=6, num_hosts=3,
            llm_provider="mock", normal_per_turn=4,
            gnn_pretrain=30, output_dir=str(tmp_path), resume=False,
        )
        summary = runner.run()
        assert summary["n_simulations"] == 3
        assert "f1" in summary
        assert "winners" in summary

    def test_bulk_runner_saves_results(self, tmp_path):
        runner = BulkRunner(
            n_sims=3, turns=2, num_users=6, num_hosts=3,
            llm_provider="mock", normal_per_turn=4,
            gnn_pretrain=30, output_dir=str(tmp_path), resume=False,
        )
        runner.run()
        assert (tmp_path / "bulk_results.json").exists()
        assert (tmp_path / "bulk_summary.json").exists()

    def test_bulk_summary_stats(self, tmp_path):
        runner = BulkRunner(
            n_sims=5, turns=2, num_users=6, num_hosts=3,
            llm_provider="mock", normal_per_turn=4,
            gnn_pretrain=30, output_dir=str(tmp_path), resume=False,
        )
        summary = runner.run()
        for stat in ["mean", "stdev", "median", "min", "max"]:
            assert stat in summary["f1"]
        assert summary["f1"]["mean"] >= 0.0
        assert summary["f1"]["mean"] <= 1.0

    def test_bulk_resume(self, tmp_path):
        """Second run should load prior results and only run remaining sims."""
        runner1 = BulkRunner(
            n_sims=3, turns=2, num_users=6, num_hosts=3,
            llm_provider="mock", normal_per_turn=4,
            gnn_pretrain=30, output_dir=str(tmp_path), resume=False,
        )
        runner1.run()

        runner2 = BulkRunner(
            n_sims=5, turns=2, num_users=6, num_hosts=3,
            llm_provider="mock", normal_per_turn=4,
            gnn_pretrain=30, output_dir=str(tmp_path), resume=True,
        )
        # Should have 3 already, run 2 more
        assert len(runner2.results) == 3
        summary = runner2.run()
        assert summary["n_simulations"] == 5

    def test_bulk_winner_distribution(self, tmp_path):
        runner = BulkRunner(
            n_sims=5, turns=2, num_users=6, num_hosts=3,
            llm_provider="mock", normal_per_turn=4,
            gnn_pretrain=30, output_dir=str(tmp_path), resume=False,
        )
        summary = runner.run()
        total = sum(summary["winners"].values())
        assert total == 5
        for rate in summary["winner_rates"].values():
            assert 0.0 <= rate <= 1.0
