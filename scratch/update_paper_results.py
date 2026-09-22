import codecs

with codecs.open('research/paper_generator.py', 'r', 'utf-8') as f:
    text = f.read()

start_idx = text.find('    def results')
end_idx = text.find('    def discussion')

new_results = """    def results(self, campaign_record) -> str:
        cr = campaign_record
        
        # Aggregate ALL historical battles instead of just this campaign
        import glob, json
        battle_files = glob.glob("data/reports/battle_*.json")
        historical_battles = []
        for bf in battle_files:
            try:
                bdata = json.load(open(bf, 'r', encoding='utf-8'))
                historical_battles.append(bdata)
            except: pass
            
        historical_battles.sort(key=lambda x: x.get('battle_id', ''))
        
        # We will show the last 15 battles in the detailed F1 table so it fits nicely
        display_battles = historical_battles[-15:] if len(historical_battles) > 0 else []
        
        f1_rows = []
        for i, bdata in enumerate(display_battles):
            m = bdata.get("metrics", {})
            f1 = m.get("f1_score", 0.0)
            p = m.get("precision", 0.0)
            r = m.get("recall", 0.0)
            f1_rows.append([f"Op {i+1}", f"{f1:.2f}", f"{p:.2f}", f"{r:.2f}", str(bdata.get("total_attacks", 0))])
            
        if not f1_rows:
            f1_rows = [["None", "0.0", "0.0", "0.0", "0"]]
            
        f1_table = _fmt_table(
            ["Operation", "F1", "Precision", "Recall", "Total Attacks"],
            f1_rows
        )

        # ELO table (from current campaign record which already pulls from DB)
        elo_rows = [[r["rank"], r["entity"], int(r["elo"]), int(r["peak_elo"]),
                     r["battles"], f"{r['win_rate']:.1%}", f"{r['evasion_rate']:.1%}"]
                    for r in cr.final_elo_table]
        elo_table = _fmt_table(
            ["Rank", "Entity", "ELO", "Peak ELO", "Battles", "Win Rate", "Evasion Rate"],
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
            "## A. GLOBAL AGENT PERFORMANCE (ALL OPERATIONS)\\n",
            "This table aggregates detection performance across all recorded engagements.\\n",
            f1_table + "\\n",
            "\\n## B. ELO THREAT INTELLIGENCE LEADERBOARD\\n",
            elo_table + "\\n",
            "\\n## C. MITRE ATT&CK TACTIC EFFECTIVENESS\\n",
            tech_table + "\\n"
        ]
        return "\\n".join(lines)

"""

text = text[:start_idx] + new_results + text[end_idx:]

with codecs.open('research/paper_generator.py', 'w', 'utf-8') as f:
    f.write(text)
