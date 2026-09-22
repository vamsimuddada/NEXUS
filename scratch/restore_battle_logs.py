import codecs

with codecs.open('research/paper_generator.py', 'r', 'utf-8') as f:
    text = f.read()

import re

# Restore the battle-by-battle logs to the SIGMA section
old_method = r"""    def appendix_sigma_log(self, campaign_record) -> str:
        es = campaign_record.evolution_summary
        auto = es.get("auto_generated_rules", 0)
        total = es.get("total_sigma_rules", 0)
        start = campaign_record.sigma_rule_history[0] if campaign_record.sigma_rule_history else 0
        
        return (
            "## 7. SIGMA Rule Evolution Log\n"
            f"The Evolution Engine actively synthesizes new SIGMA detection rules in response to zero-day adversarial behaviors. The campaign started with {start} baseline rules and concluded with {total} active rules, representing the autonomous generation of {auto} new behavioral heuristic(s) over the course of the live operations.\n"
        )"""

new_method = r"""    def appendix_sigma_log(self, campaign_record) -> str:
        es = campaign_record.evolution_summary
        auto = es.get("auto_generated_rules", 0)
        total = es.get("total_sigma_rules", 0)
        start = campaign_record.sigma_rule_history[0] if campaign_record.sigma_rule_history else 0
        
        lines = [
            "## 7. SIGMA Rule Evolution Log\n",
            f"The Evolution Engine actively synthesizes new SIGMA detection rules in response to zero-day adversarial behaviors. The campaign started with {start} baseline rules and concluded with {total} active rules, representing the autonomous generation of {auto} new behavioral heuristic(s) over the course of the live operations.\n",
            "**Rule count per battle:**"
        ]
        
        for i, count in enumerate(campaign_record.sigma_rule_history, 1):
            lines.append(f"- Battle {i}: {count} rules")
            
        return "\n".join(lines) + "\n" """

text = re.sub(r'    def appendix_sigma_log\(self, campaign_record\) -> str:.*?        \)', new_method, text, flags=re.DOTALL)

with codecs.open('research/paper_generator.py', 'w', 'utf-8') as f:
    f.write(text)
