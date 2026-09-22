import codecs

with codecs.open('research/paper_generator.py', 'r', 'utf-8') as f:
    text = f.read()

# Replace the generation logic to strip out academic sections and focus purely on professional SOC reporting
old_sections = """        sections = [
            f"# {self.TITLE}\\n",
            f"**Authors:** {self.AUTHORS}  \\n",
            f"**Venue:** {self.VENUE}  \\n",
            f"**Generated:** {timestamp}  \\n\\n---\n",
            "## Abstract\\n\\n" + self.abstract(campaign_record) + "\\n",
            "\\n---\\n\\n## 1. Introduction\\n\\n"
            "Modern SOC detection systems are evaluated against static attack datasets. "
            "NEXUS challenges this by coupling attacker and defender in a closed "
            "co-evolutionary loop: each side learns from the other across sequential battles. "
            "We make the following contributions:\\n\\n"
            "1. A six-agent LLM attacker council with distinct psychological profiles.\\n"
            "2. A tri-brain detection ensemble (SIGMA + GNN + LLM debate).\\n"
            "3. A cognitive evolution engine that rewrites detection rules and "
            "retrains models autonomously.\\n"
            "4. NOVA: an adversarial ML attacker that learns the detection threshold "
            "empirically across battles.\\n"
            "5. A full research output pipeline producing STIX 2.1 bundles, "
            "labeled datasets, and paper sections.\\n",
            "\\n## 2. Related Work\\n\\n"
            "Prior work on cyber simulation includes CALDERA [MITRE], "
            "CybORG [CAGE], and AttackIQ. These platforms focus on known playbooks "
            "rather than emergent co-evolution. LLM-based agents for red-teaming "
            "have been explored by PentestGPT and HackingBuddyGPT but without "
            "a self-modifying defender. NEXUS contributes the closed-loop "
            "co-evolution architecture and the adversarial ML evasion layer.\\n",
            "\\n" + self.experimental_setup(campaign_record),
            "\\n" + self.results(campaign_record),
            "\\n" + self.discussion(campaign_record),
            "\\n## 6. Conclusion\\n\\n"
            "NEXUS demonstrates that autonomous adversarial co-evolution is feasible "
            "on commodity hardware. The defender's SIGMA rule base grows without human "
            "authorship, NOVA's evasion rate climbs across battles through purely "
            "empirical threshold probing, and the ELO system successfully tracks "
            "model capability.\\n",
            "\\n" + self.appendix_a(campaign_record)
        ]"""

new_sections = """        sections = [
            f"# NEXUS EXECUTIVE INCIDENT REPORT\\n",
            f"**Report ID:** {campaign_record.campaign_id}\\n",
            f"**Generated:** {timestamp} UTC\\n",
            f"**Classification:** STRICTLY CONFIDENTIAL\\n\\n---\\n",
            "\\n## 1. Executive Summary\\n\\n",
            "This document serves as an automated post-action report following a simulated cyber warfare campaign. ",
            "The following data details the adversarial threat exposure, Blue Team SIEM detection rates, and active mitigation performance.\\n",
            "\\n" + self.results(campaign_record),
            "\\n" + self.discussion(campaign_record),
        ]"""

text = text.replace(old_sections, new_sections)

with codecs.open('research/paper_generator.py', 'w', 'utf-8') as f:
    f.write(text)
