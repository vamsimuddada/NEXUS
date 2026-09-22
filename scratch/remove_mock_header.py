import codecs

with codecs.open('research/pdf_generator.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the header to only show live operations
old_metrics = """                live_ops = len(glob.glob("data/reports/battle_*.json"))
                
                pdf.set_font("SpaceGrotesk", "B", 10)
                pdf.set_text_color(99, 102, 241) # Indigo
                pdf.cell(0, 8, f"DATABASE METRICS: {live_ops} LIVE OPERATIONS | {total_battles} PRE-TRAINED HISTORICAL BATTLES", 0, 1)"""

new_metrics = """                live_ops = len(glob.glob("data/reports/battle_*.json"))
                
                pdf.set_font("SpaceGrotesk", "B", 10)
                pdf.set_text_color(99, 102, 241) # Indigo
                pdf.cell(0, 8, f"DATABASE METRICS: {live_ops} LIVE OPERATIONS LOGGED", 0, 1)"""

text = text.replace(old_metrics, new_metrics)

with codecs.open('research/pdf_generator.py', 'w', 'utf-8') as f:
    f.write(text)
