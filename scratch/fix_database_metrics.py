import codecs

with codecs.open('research/pdf_generator.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the Database Metrics to pull the TRUE number of historical battles from SQLite
old_db_metrics = """            try:
                import glob, json
                total_battles = len(glob.glob("data/reports/battle_*.json"))
                pdf.set_font("SpaceGrotesk", "B", 10)
                pdf.set_text_color(99, 102, 241) # Indigo
                pdf.cell(0, 8, f"DATABASE METRICS: {total_battles} HISTORICAL BATTLES LOGGED ACROSS ALL CAMPAIGNS", 0, 1)
                pdf.ln(5)
            except:
                pass"""

new_db_metrics = """            try:
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

text = text.replace(old_db_metrics, new_db_metrics)

with codecs.open('research/pdf_generator.py', 'w', 'utf-8') as f:
    f.write(text)


with codecs.open('research/paper_generator.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the table header to clarify it only shows the latest operations with full telemetry, not all 1377 battles
old_header = """            "## A. GLOBAL AGENT PERFORMANCE (ALL OPERATIONS)\\n",
            "This table aggregates detection performance across all recorded engagements.\\n","""

new_header = """            "## A. RECENT AGENT PERFORMANCE (TELEMETRY EXTRACTS)\\n",
            "This table details detection performance for the most recent operations with full JSON telemetry exports.\\n","""

text = text.replace(old_header, new_header)

with codecs.open('research/paper_generator.py', 'w', 'utf-8') as f:
    f.write(text)
