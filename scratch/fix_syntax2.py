import codecs

with codecs.open('research/paper_generator.py', 'r', 'utf-8') as f:
    text = f.read()

start_idx = text.find("    def appendix_sigma_log(self, campaign_record) -> str:")
end_idx = text.find("    #  Full Paper")
if end_idx == -1:
    end_idx = text.find("    def generate_paper")

new_method = r"""    def appendix_sigma_log(self, campaign_record) -> str:
        es = campaign_record.evolution_summary
        auto = es.get("auto_generated_rules", 0)
        total = es.get("total_sigma_rules", 0)
        start = campaign_record.sigma_rule_history[0] if campaign_record.sigma_rule_history else 0
        
        return (
            "## 7. SIGMA Rule Evolution Log\n"
            f"The Evolution Engine actively synthesizes new SIGMA detection rules in response to zero-day adversarial behaviors. The campaign started with {start} baseline rules and concluded with {total} active rules, representing the autonomous generation of {auto} new behavioral heuristics over the course of the live operations.\n"
        )

"""

if start_idx != -1 and end_idx != -1:
    text = text[:start_idx] + new_method + text[end_idx:]
    with codecs.open('research/paper_generator.py', 'w', 'utf-8') as f:
        f.write(text)
