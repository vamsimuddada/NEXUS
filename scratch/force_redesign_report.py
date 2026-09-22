import codecs

with codecs.open('research/paper_generator.py', 'r', 'utf-8') as f:
    text = f.read()

start_idx = text.find('    def generate_paper(')
end_idx = text.find('    def abstract(')

new_generate_paper = """    def generate_paper(self, campaign_record,
                       output_path: str = "data/research/nexus_paper.md") -> str:
        from pathlib import Path
        from datetime import datetime, timezone
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        sections = [
            f"# NEXUS EXECUTIVE INCIDENT REPORT\\n",
            f"**Report ID:** {campaign_record.campaign_id}\\n",
            f"**Generated:** {timestamp} UTC\\n",
            f"**Classification:** STRICTLY CONFIDENTIAL\\n\\n---\\n",
            "\\n## 1. Executive Summary\\n\\n",
            "This document serves as an automated post-action report following a simulated cyber warfare campaign. ",
            "The following data details the adversarial threat exposure, Blue Team SIEM detection rates, and active mitigation performance.\\n",
            "\\n" + self.results(campaign_record),
            "\\n" + self.discussion(campaign_record)
        ]
        
        md = "\\n".join(sections)
        Path(output_path).write_text(md, encoding="utf-8")
        return output_path

"""

text = text[:start_idx] + new_generate_paper + text[end_idx:]

with codecs.open('research/paper_generator.py', 'w', 'utf-8') as f:
    f.write(text)
