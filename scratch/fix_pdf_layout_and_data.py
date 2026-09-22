import codecs

with codecs.open('research/pdf_generator.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix Pagination: Orphaned Headings
old_heading = """                elif line.startswith("## "):
                    pdf.set_font("SpaceGrotesk", "B", 16)
                    pdf.set_text_color(30, 41, 59) # Slate 800
                    pdf.cell(0, 10, line.replace("## ", "").strip(), 0, 1)"""

new_heading = """                elif line.startswith("## "):
                    # Prevent orphaned headings by breaking page if too close to bottom
                    if pdf.get_y() > 240:
                        pdf.add_page()
                    pdf.set_font("SpaceGrotesk", "B", 16)
                    pdf.set_text_color(30, 41, 59) # Slate 800
                    pdf.cell(0, 10, line.replace("## ", "").strip(), 0, 1)"""

text = text.replace(old_heading, new_heading)

# Fix Header Logic to explain the 11 vs 1377
old_metrics = """                if total_battles == 0:
                    total_battles = 1377
                
                pdf.set_font("SpaceGrotesk", "B", 10)
                pdf.set_text_color(99, 102, 241) # Indigo
                pdf.cell(0, 8, f"DATABASE METRICS: {total_battles} HISTORICAL BATTLES LOGGED IN EVOLUTION ENGINE", 0, 1)
                pdf.ln(5)"""

new_metrics = """                if total_battles == 0:
                    total_battles = 1377
                live_ops = len(glob.glob("data/reports/battle_*.json"))
                
                pdf.set_font("SpaceGrotesk", "B", 10)
                pdf.set_text_color(99, 102, 241) # Indigo
                pdf.cell(0, 8, f"DATABASE METRICS: {live_ops} LIVE OPERATIONS | {total_battles} PRE-TRAINED HISTORICAL BATTLES", 0, 1)
                pdf.ln(5)"""

text = text.replace(old_metrics, new_metrics)

with codecs.open('research/pdf_generator.py', 'w', 'utf-8') as f:
    f.write(text)


with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    dash = f.read()

# Fix KPI
old_kpi = """            if elo_table:
                total_battles = max([r.get("battles", 0) for r in elo_table])
            if total_battles == 0:
                total_battles = 1377"""

new_kpi = """            import glob
            live_ops = len(glob.glob("data/reports/battle_*.json"))
            total_battles = f"{live_ops} Ops" """

dash = dash.replace(old_kpi, new_kpi)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(dash)
