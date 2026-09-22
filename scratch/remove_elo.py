import codecs

with codecs.open('research/paper_generator.py', 'r', 'utf-8') as f:
    text = f.read()

import re

# 1. Remove ELO Table from results()
old_results = r"""        # ELO table (from current campaign record which already pulls from DB)
        elo_rows = [[r["rank"], r["entity"], int(r["elo"]), int(r["peak_elo"]),
                     r["battles"], f"{r['win_rate']:.1%}", f"{r['evasion_rate']:.1%}"]
                    for r in cr.final_elo_table]
        elo_table = _fmt_table(
            ["Rank", "Entity", "ELO", "Peak ELO", "Total History", "Win Rate", "Evasion Rate"],
            elo_rows
        )

        # Technique table
        tech_rows = [[t["technique"], t["uses"], t["evaded"],
                      f"{t['evasion_rate']:.1%}", f"{t['detection_rate']:.1%}"]
                     for t in cr.technique_stats]
        tech_table = _fmt_table(
            ["Technique", "Uses", "Evaded", "Evasion Rate", "Detection Rate"],
            tech_rows
        )

        lines = [
            "## 3. Recent Agent Performance (TELEMETRY EXTRACTS)\n",
            "This table details detection performance for the most recent operations with full JSON telemetry exports.\n",
            f1_table + "\n",
            "\n## 4. Global Threat Intelligence Leaderboard\n",
            elo_table + "\n",
            "\n## 5. MITRE ATT&CK Tactic Effectiveness\n",
            tech_table + "\n"
        ]"""

new_results = r"""        # Technique table
        tech_rows = [[t["technique"], t["uses"], t["evaded"],
                      f"{t['evasion_rate']:.1%}", f"{t['detection_rate']:.1%}"]
                     for t in cr.technique_stats]
        tech_table = _fmt_table(
            ["Technique", "Uses", "Evaded", "Evasion Rate", "Detection Rate"],
            tech_rows
        )

        lines = [
            "## 3. Recent Agent Performance (TELEMETRY EXTRACTS)\n",
            "This table details detection performance for the most recent operations with full JSON telemetry exports.\n",
            f1_table + "\n",
            "\n## 4. MITRE ATT&CK Tactic Effectiveness\n",
            tech_table + "\n"
        ]"""

text = text.replace(old_results, new_results)

# 2. Remove Personas from generate_paper
old_gen = r"""            "\n" + self.results(campaign_record),
            "\n" + self.appendix_personas(campaign_record).replace("Appendix A:", "6. Attacker Persona Profiles"),
            "\n" + self.appendix_sigma_log(campaign_record).replace("Appendix B:", "7.")"""

new_gen = r"""            "\n" + self.results(campaign_record),
            "\n" + self.appendix_sigma_log(campaign_record).replace("## 7.", "## 5.")"""

text = text.replace(old_gen, new_gen)

# 3. Change "## 7. SIGMA" inside appendix_sigma_log to "## 5. SIGMA"
text = text.replace('## 7. SIGMA Rule Evolution Log', '## 5. SIGMA Rule Evolution Log')

with codecs.open('research/paper_generator.py', 'w', 'utf-8') as f:
    f.write(text)
