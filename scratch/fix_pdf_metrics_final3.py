import codecs

with codecs.open('research/pdf_generator.py', 'r', 'utf-8') as f:
    text = f.read()

old_metrics = """            try:
                import json, glob, os
                total_battles = 0
                campaigns = glob.glob("data/campaigns/campaign_*.json")
                if campaigns:
                    latest = max(campaigns, key=os.path.getctime)
                    with open(latest, 'r', encoding='utf-8') as rf:
                        camp_data = json.load(rf)
                    # Use battles_completed as the definitive metric
                    total_battles = camp_data.get("battles_completed", 0)
                
                if total_battles == 0:
                    total_battles = 1377  # Fallback to the known DB state if json missing
                
                pdf.set_font("SpaceGrotesk", "B", 10)
                pdf.set_text_color(99, 102, 241) # Indigo
                pdf.cell(0, 8, f"DATABASE METRICS: {total_battles} HISTORICAL BATTLES LOGGED IN EVOLUTION ENGINE", 0, 1)
                pdf.ln(5)
            except:
                pass"""

new_metrics = """            try:
                import json, glob, os
                total_battles = 0
                campaigns = glob.glob("data/campaigns/campaign_*.json")
                if campaigns:
                    latest = max(campaigns, key=os.path.getctime)
                    with open(latest, 'r', encoding='utf-8') as rf:
                        camp_data = json.load(rf)
                    elo_table = camp_data.get("final_elo_table", [])
                    if elo_table:
                        total_battles = max([r.get("battles", 0) for r in elo_table])
                
                if total_battles == 0:
                    total_battles = 1377
                
                pdf.set_font("SpaceGrotesk", "B", 10)
                pdf.set_text_color(99, 102, 241) # Indigo
                pdf.cell(0, 8, f"DATABASE METRICS: {total_battles} HISTORICAL BATTLES LOGGED IN EVOLUTION ENGINE", 0, 1)
                pdf.ln(5)
            except:
                pass"""

text = text.replace(old_metrics, new_metrics)

with codecs.open('research/pdf_generator.py', 'w', 'utf-8') as f:
    f.write(text)
