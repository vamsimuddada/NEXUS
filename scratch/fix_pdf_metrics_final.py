import codecs

with codecs.open('research/pdf_generator.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix Database Metrics to successfully pull the historical battles from the ELO JSON payload
old_metrics = """            try:
                import sqlite3
                total_battles = 0
                if os.path.exists("data/simulation_results.db"):
                    with sqlite3.connect("data/simulation_results.db") as conn:
                        total_battles = conn.execute("SELECT COUNT(DISTINCT battle_id) FROM simulation_results").fetchone()[0]
                pdf.set_font("SpaceGrotesk", "B", 10)
                pdf.set_text_color(99, 102, 241) # Indigo
                pdf.cell(0, 8, f"DATABASE METRICS: {total_battles} HISTORICAL BATTLES LOGGED IN SQLITE INTELLIGENCE VAULT", 0, 1)
                pdf.ln(5)
            except:
                pass"""

new_metrics = """            try:
                import json, glob, os
                total_battles = 0
                reports = glob.glob("data/reports/battle_*.json")
                if reports:
                    latest = max(reports, key=os.path.getctime)
                    with codecs.open(latest, 'r', 'utf-8') as rf:
                        rep_data = json.load(rf)
                    elo_table = rep_data.get("final_elo_table", [])
                    if elo_table:
                        total_battles = max([r.get('battles', 0) for r in elo_table])
                
                pdf.set_font("SpaceGrotesk", "B", 10)
                pdf.set_text_color(99, 102, 241) # Indigo
                pdf.cell(0, 8, f"DATABASE METRICS: {total_battles} HISTORICAL BATTLES LOGGED IN EVOLUTION ENGINE", 0, 1)
                pdf.ln(5)
            except:
                pass"""

text = text.replace(old_metrics, new_metrics)

with codecs.open('research/pdf_generator.py', 'w', 'utf-8') as f:
    f.write(text)
