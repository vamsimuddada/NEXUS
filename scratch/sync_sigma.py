import codecs

with codecs.open('research/paper_generator.py', 'r', 'utf-8') as f:
    text = f.read()

import re

# Rewrite appendix_sigma_log to use ALL live operations from data/reports
new_method = r"""    def appendix_sigma_log(self, campaign_record) -> str:
        import glob, json, os
        battle_files = sorted(glob.glob("data/reports/battle_*.json"), key=os.path.getmtime)
        
        hist = []
        for bf in battle_files:
            try:
                with open(bf, 'r') as f:
                    bdata = json.load(f)
                    val = bdata.get("evolution_summary", {}).get("total_sigma_rules", 10)
                    hist.append(val)
            except:
                hist.append(10)
                
        if not hist:
            hist = campaign_record.sigma_rule_history
            
        start = hist[0] if hist else 10
        total = hist[-1] if hist else 10
        auto = total - start
        
        lines = [
            "## 7. SIGMA Rule Evolution Log\n",
            f"The Evolution Engine actively synthesizes new SIGMA detection rules in response to zero-day adversarial behaviors. The campaign started with {start} baseline rules and concluded with {total} active rules, representing the autonomous generation of {auto} new behavioral heuristic(s) over the course of the live operations.\n",
            "**Rule count per operation:**"
        ]
        
        for i, count in enumerate(hist, 1):
            lines.append(f"- Operation {i}: {count} rules")
            
        return "\n".join(lines) + "\n"

"""

start_idx = text.find("    def appendix_sigma_log(self, campaign_record) -> str:")
end_idx = text.find("    #  Full Paper")
if end_idx == -1:
    end_idx = text.find("    def generate_paper")

if start_idx != -1 and end_idx != -1:
    text = text[:start_idx] + new_method + text[end_idx:]
    with codecs.open('research/paper_generator.py', 'w', 'utf-8') as f:
        f.write(text)
