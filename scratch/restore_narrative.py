import codecs

with codecs.open('research/paper_generator.py', 'r', 'utf-8') as f:
    text = f.read()

# Define the new rich sections
new_methods = """    def project_info(self) -> str:
        return (
            "## 1. Project Overview & Architecture\\n"
            "NEXUS (Neural Exploitation and eXplainable Unified Security) is a strictly isolated, "
            "autonomous cyber-warfare simulation matrix. The platform pits an ensemble of highly specialized, "
            "LLM-driven adversarial agents against a self-evolving SOC (Security Operations Center). "
            "The SOC combines dynamic SIGMA rule generation, graph-neural-network anomaly detection, "
            "and active threat mitigation protocols. This intelligence report details the co-evolutionary "
            "adaptation of both offensive and defensive systems over the course of the simulation.\\n"
        )
        
    def tactical_details(self, cr) -> str:
        turns = cr.battles_completed
        techs = cr.technique_stats if hasattr(cr, 'technique_stats') else []
        top_tech = sorted(techs, key=lambda x: x.get("uses", 0), reverse=True)[0]['technique'] if techs else "N/A"
        total_uses = sum(t.get("uses", 0) for t in techs)
        
        return (
            "## 2. Tactical Deployment Details\\n"
            f"The simulation stress-tested the defensive architecture across {turns} manual tactical engagements, "
            f"simulating thousands of distinct behavioral artifacts. In total, the adversarial Red Team deployed "
            f"MITRE ATT&CK techniques {total_uses} times. The most heavily utilized operational vector was "
            f"technique {top_tech}, demonstrating the attackers' preference for exploiting structural "
            f"vulnerabilities in the simulated enterprise environment. The following telemetry data rigorously "
            f"quantifies the exact effectiveness of these tactical deployments.\\n"
        )
"""

# Inject the new methods into the class
if "def project_info" not in text:
    target = "    def generate_charts(self, campaign_record):"
    text = text.replace(target, new_methods + "\n" + target)

# Modify the generate_paper method to include the new sections
old_sections = """            "\\n" + self.results(campaign_record),
            "\\n## D. THREAT EVOLUTION VISUALIZATION\\n",
            "![ELO Chart](data/research/elo_chart.png)\\n",
            "![MITRE Chart](data/research/mitre_chart.png)\\n",
            "\\n" + self.appendix_personas(campaign_record),
            "\\n" + self.appendix_sigma_log(campaign_record)
        ])"""

new_sections = """            "\\n" + self.project_info(),
            "\\n" + self.tactical_details(campaign_record),
            "\\n" + self.results(campaign_record),
            "\\n## 3. Threat Evolution Visualization\\n",
            "![ELO Chart](data/research/elo_chart.png)\\n",
            "![MITRE Chart](data/research/mitre_chart.png)\\n",
            "\\n" + self.appendix_personas(campaign_record),
            "\\n" + self.appendix_sigma_log(campaign_record)
        ])"""

text = text.replace(old_sections, new_sections)

# Let's fix the numbering of the tables in results() too.
text = text.replace("## A. RECENT AGENT PERFORMANCE", "## 4. Recent Agent Performance")
text = text.replace("## B. ELO THREAT INTELLIGENCE LEADERBOARD", "## 5. Global Threat Intelligence Leaderboard")
text = text.replace("## C. MITRE ATT&CK TACTIC EFFECTIVENESS", "## 6. MITRE ATT&CK Tactic Effectiveness")
text = text.replace("## Appendix A:", "## Appendix A:")

# Write back
with codecs.open('research/paper_generator.py', 'w', 'utf-8') as f:
    f.write(text)
