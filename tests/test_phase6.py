"""
NEXUS — Phase 6 Tests
Covers: D3 kill-chain visualiser, PDF/LaTeX paper generator, full pipeline.
Run with: pytest tests/test_phase6.py -v
"""
import sys, os, json, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pathlib import Path
from research.killchain_viz import generate_killchain_html, _build_graph_data, _build_timeline_data
from research.pdf_generator import PDFPaperGenerator, _md_to_html_body, _md_to_latex, _latex_escape
from research.attck_client  import ATTCKClient


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_campaign_record(n_battles=2):
    from core.campaign import CampaignRunner
    runner = CampaignRunner(
        n_battles=n_battles, turns_per_battle=2,
        num_users=8, num_hosts=4, llm_provider="mock",
        normal_logs_per_turn=5, gnn_pretrain_logs=40,
        verbose=False, save_reports=False,
    )
    return runner.run()


def make_attck():
    return ATTCKClient(use_live=False)


SAMPLE_MD = """# NEXUS Paper Title

**Authors:** Test Team
**Venue:** arXiv

---

## Abstract

This is the abstract paragraph. It summarises the key findings.

## 1. Introduction

NEXUS is an autonomous cybersecurity simulation platform. It combines
**six attacker agents** with a self-modifying defender.

### 1.1 Contributions

We make the following contributions:

1. A six-agent LLM attacker council.
2. A tri-brain detection ensemble.

## 2. Results

| Battle | F1    | SIGMA |
|--------|-------|-------|
| 1      | 0.750 | 10    |
| 2      | 0.800 | 17    |

## 3. Conclusion

NEXUS demonstrates emergent co-evolution.

## References

[1] MITRE ATT&CK. https://attack.mitre.org/
"""


# ── D3 Kill-Chain Visualiser ──────────────────────────────────────────────────

class TestKillChainViz:
    def test_build_graph_data_structure(self):
        record = make_campaign_record()
        attck  = make_attck()
        data   = _build_graph_data(record, attck)
        assert "nodes" in data
        assert "links" in data
        assert len(data["nodes"]) > 0
        assert len(data["links"]) > 0

    def test_graph_has_agent_nodes(self):
        record = make_campaign_record()
        attck  = make_attck()
        data   = _build_graph_data(record, attck)
        agent_nodes = [n for n in data["nodes"] if n["type"] == "agent"]
        assert len(agent_nodes) >= 1

    def test_graph_has_technique_nodes(self):
        record = make_campaign_record()
        attck  = make_attck()
        data   = _build_graph_data(record, attck)
        tech_nodes = [n for n in data["nodes"] if n["type"] == "technique"]
        assert len(tech_nodes) >= 1

    def test_graph_has_defender_node(self):
        record = make_campaign_record()
        attck  = make_attck()
        data   = _build_graph_data(record, attck)
        defender = [n for n in data["nodes"] if n["id"] == "DEFENDER"]
        assert len(defender) == 1

    def test_graph_links_have_required_fields(self):
        record = make_campaign_record()
        attck  = make_attck()
        data   = _build_graph_data(record, attck)
        for link in data["links"]:
            assert "source" in link
            assert "target" in link
            assert "type"   in link

    def test_build_timeline_data(self):
        record = make_campaign_record(n_battles=2)
        attck  = make_attck()
        data   = _build_timeline_data(record, attck)
        assert isinstance(data, list)
        if data:
            row = data[0]
            assert "battle"    in row
            assert "technique" in row
            assert "evasion"   in row
            assert "detection" in row

    def test_generate_html_creates_file(self, tmp_path):
        record = make_campaign_record()
        attck  = make_attck()
        path   = str(tmp_path / "killchain.html")
        result = generate_killchain_html(record, attck, path)
        assert os.path.exists(result)
        content = Path(result).read_text(encoding="utf-8")
        assert len(content) > 5000

    def test_html_contains_d3_script(self, tmp_path):
        record = make_campaign_record()
        attck  = make_attck()
        path   = str(tmp_path / "killchain.html")
        generate_killchain_html(record, attck, path)
        content = Path(path).read_text(encoding="utf-8")
        assert "d3.min.js" in content

    def test_html_contains_force_simulation(self, tmp_path):
        record = make_campaign_record()
        attck  = make_attck()
        path   = str(tmp_path / "killchain.html")
        generate_killchain_html(record, attck, path)
        content = Path(path).read_text(encoding="utf-8")
        assert "forceSimulation" in content

    def test_html_contains_campaign_id(self, tmp_path):
        record = make_campaign_record()
        attck  = make_attck()
        path   = str(tmp_path / "killchain.html")
        generate_killchain_html(record, attck, path)
        content = Path(path).read_text(encoding="utf-8")
        assert record.campaign_id in content

    def test_html_contains_timeline(self, tmp_path):
        record = make_campaign_record(n_battles=2)
        attck  = make_attck()
        path   = str(tmp_path / "killchain.html")
        generate_killchain_html(record, attck, path)
        content = Path(path).read_text(encoding="utf-8")
        assert "timeline" in content.lower()

    def test_html_contains_metrics_tab(self, tmp_path):
        record = make_campaign_record()
        attck  = make_attck()
        path   = str(tmp_path / "killchain.html")
        generate_killchain_html(record, attck, path)
        content = Path(path).read_text(encoding="utf-8")
        assert "metrics" in content.lower()

    def test_graph_data_serialisable(self):
        record = make_campaign_record()
        attck  = make_attck()
        data   = _build_graph_data(record, attck)
        # Must be JSON-serialisable (D3 requires this)
        json_str = json.dumps(data)
        assert len(json_str) > 100

    def test_node_colours_present(self):
        record = make_campaign_record()
        attck  = make_attck()
        data   = _build_graph_data(record, attck)
        for node in data["nodes"]:
            assert "color" in node
            assert node["color"]   # non-empty


# ── PDF/LaTeX Generator ───────────────────────────────────────────────────────

class TestPDFGenerator:
    def test_md_to_html_headings(self):
        html = _md_to_html_body("## Section\n\nParagraph text.")
        assert "<h2>Section</h2>" in html
        assert "Paragraph text" in html

    def test_md_to_html_table(self):
        md   = "| A | B |\n|---|---|\n| x | y |"
        html = _md_to_html_body(md)
        assert "<table>" in html
        assert "<td>" in html or "<th>" in html

    def test_md_to_html_code_block(self):
        md   = "```python\nprint('hello')\n```"
        html = _md_to_html_body(md)
        assert "<pre>" in html
        assert "print" in html

    def test_md_to_html_bold(self):
        html = _md_to_html_body("**bold text** here")
        assert "<strong>bold text</strong>" in html

    def test_md_to_html_italic(self):
        html = _md_to_html_body("*italic text* here")
        assert "<em>italic text</em>" in html

    def test_md_to_html_inline_code(self):
        html = _md_to_html_body("Use `myfunction()` here")
        assert "<code>myfunction()</code>" in html

    def test_md_to_html_horizontal_rule(self):
        html = _md_to_html_body("---")
        assert "<hr>" in html

    def test_latex_escape_ampersand(self):
        assert r"\&" in _latex_escape("A & B")

    def test_latex_escape_percent(self):
        assert r"\%" in _latex_escape("50%")

    def test_latex_escape_underscore(self):
        assert r"\_" in _latex_escape("var_name")

    def test_md_to_latex_section(self):
        latex = _md_to_latex("## Introduction\n\nText.", "Title", "Author")
        assert r"\section{Introduction}" in latex

    def test_md_to_latex_subsection(self):
        latex = _md_to_latex("### Sub\n\nText.", "T", "A")
        assert r"\subsection{Sub}" in latex

    def test_md_to_latex_has_document_tags(self):
        latex = _md_to_latex(SAMPLE_MD, "Title", "Author")
        assert r"\begin{document}" in latex
        assert r"\end{document}"   in latex

    def test_md_to_latex_has_maketitle(self):
        latex = _md_to_latex(SAMPLE_MD, "Title", "Author")
        assert r"\maketitle" in latex

    def test_md_to_latex_abstract(self):
        latex = _md_to_latex(SAMPLE_MD, "T", "A")
        assert r"\begin{abstract}" in latex

    def test_generate_latex_file(self, tmp_path):
        md_path  = str(tmp_path / "paper.md")
        tex_path = str(tmp_path / "paper.tex")
        Path(md_path).write_text(SAMPLE_MD)
        gen    = PDFPaperGenerator()
        result = gen.generate_latex(md_path, tex_path)
        assert os.path.exists(result)
        content = Path(result).read_text(encoding="utf-8")
        assert r"\documentclass" in content
        assert r"\end{document}" in content

    def test_generate_pdf_produces_file(self, tmp_path):
        md_path  = str(tmp_path / "paper.md")
        pdf_path = str(tmp_path / "paper.pdf")
        Path(md_path).write_text(SAMPLE_MD)
        gen    = PDFPaperGenerator()
        result = gen.generate_pdf(md_path, pdf_path)
        # Should produce either a PDF or HTML fallback — either way a file
        assert result is not None
        assert os.path.exists(result)

    def test_generate_all_returns_dict(self, tmp_path):
        md_path = str(tmp_path / "paper.md")
        Path(md_path).write_text(SAMPLE_MD)
        gen    = PDFPaperGenerator()
        result = gen.generate_all(md_path, str(tmp_path))
        assert isinstance(result, dict)
        # At minimum LaTeX should succeed
        assert "latex" in result
        assert result["latex"] is not None
        assert os.path.exists(result["latex"])


# ── Full pipeline integration ─────────────────────────────────────────────────

class TestFullPipeline:
    """Integration tests that verify research outputs land in nexus/data/ (absolute paths)."""

    @staticmethod
    def _nexus_data():
        import os
        nexus_root = os.path.dirname(os.path.dirname(os.path.abspath(
            __import__("core.campaign", fromlist=["campaign"]).__file__
        )))
        from pathlib import Path
        return Path(nexus_root) / "data"

    def _run_campaign(self, monkeypatch, tmp_path):
        monkeypatch.chdir(tmp_path)
        from core.campaign import CampaignRunner
        runner = CampaignRunner(
            n_battles=2, turns_per_battle=2,
            num_users=8, num_hosts=4, llm_provider="mock",
            normal_logs_per_turn=5, gnn_pretrain_logs=40,
            verbose=False, save_reports=True,
        )
        return runner.run()

    def test_campaign_generates_d3_html(self, tmp_path, monkeypatch):
        record = self._run_campaign(monkeypatch, tmp_path)
        data   = self._nexus_data()
        html_files = list(data.glob(f"research/killchain_{record.campaign_id}.html"))
        assert len(html_files) >= 1
        content = html_files[0].read_text(encoding="utf-8")
        assert "forceSimulation" in content
        assert record.campaign_id in content

    def test_campaign_generates_latex(self, tmp_path, monkeypatch):
        record = self._run_campaign(monkeypatch, tmp_path)
        data   = self._nexus_data()
        tex_files = list(data.glob(f"research/paper_{record.campaign_id}.tex"))
        assert len(tex_files) >= 1
        content = tex_files[0].read_text(encoding="utf-8")
        assert "documentclass" in content

    def test_campaign_generates_pdf_or_html_fallback(self, tmp_path, monkeypatch):
        record = self._run_campaign(monkeypatch, tmp_path)
        data   = self._nexus_data()
        cid    = record.campaign_id
        pdf_files  = list(data.glob(f"research/paper_{cid}.pdf"))
        html_files = list(data.glob(f"research/paper_{cid}.html"))
        assert len(pdf_files) >= 1 or len(html_files) >= 1

    def test_all_seven_research_outputs(self, tmp_path, monkeypatch):
        """Verify all 7 expected output types are produced by a campaign."""
        record = self._run_campaign(monkeypatch, tmp_path)
        data   = self._nexus_data()
        cid    = record.campaign_id
        ds_dir = data / f"datasets/{cid}"

        checks = {
            "STIX bundle":    list(data.glob(f"stix/campaign_{cid}.json")),
            "Paper Markdown": list(data.glob(f"research/paper_{cid}.md")),
            "LaTeX source":   list(data.glob(f"research/paper_{cid}.tex")),
            "PDF or HTML":    list(data.glob(f"research/paper_{cid}.pdf")) +
                              list(data.glob(f"research/paper_{cid}.html")),
            "D3 visualiser":  list(data.glob(f"research/killchain_{cid}.html")),
            "Navigator layer":list(data.glob(f"research/navigator_{cid}.json")),
            "Dataset files":  (list(ds_dir.glob("*.csv")) +
                               list(ds_dir.glob("*.jsonl"))) if ds_dir.exists() else [],
        }
        for name, files in checks.items():
            assert len(files) >= 1, f"Missing output: {name}"
