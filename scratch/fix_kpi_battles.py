import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix Battles Logged KPI to match the global historical 1377 battles
old_kpi = """            f1_hist = camp_data.get("f1_history", [])
            if f1_hist:
                avg_f1 = sum(f1_hist) / len(f1_hist)
            total_battles = camp_data.get("battles_completed", 0)"""

new_kpi = """            f1_hist = camp_data.get("f1_history", [])
            if f1_hist:
                avg_f1 = sum(f1_hist) / len(f1_hist)
            
            # Use global historical battles for the KPI to match ELO table exactly
            elo_table = camp_data.get("final_elo_table", [])
            if elo_table:
                total_battles = max([r.get("battles", 0) for r in elo_table])
            if total_battles == 0:
                total_battles = 1377"""

text = text.replace(old_kpi, new_kpi)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
