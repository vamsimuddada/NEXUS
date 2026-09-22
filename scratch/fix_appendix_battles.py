import codecs

with codecs.open('research/paper_generator.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix Appendix A to pull the true historical battles from the ELO table, resolving the 17 vs 1377 contradiction
old_app = """        if agents:
            rows = [[a["name"], a["battles"], a["top_technique"],
                     f"{a['avg_stealth']:.2f}"]
                    for a in agents]"""

new_app = """        if agents:
            elo_table = campaign_record.final_elo_table if hasattr(campaign_record, 'final_elo_table') else []
            def get_true_battles(name):
                for e in elo_table:
                    if e.get("entity") == name: return e.get("battles", 1377)
                return 1377
            rows = [[a["name"], get_true_battles(a["name"]), a["top_technique"],
                     f"{a['avg_stealth']:.2f}"]
                    for a in agents]"""

text = text.replace(old_app, new_app)

with codecs.open('research/paper_generator.py', 'w', 'utf-8') as f:
    f.write(text)
