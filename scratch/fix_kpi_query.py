import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Replace the SQLite query logic for battles and win rate with SIEM logic
old_kpi_query = """            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM simulation_results WHERE event_type='battle_result'")
            total_battles = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM simulation_results WHERE event_type='battle_result' AND data LIKE '%defender%'")
            defender_wins = c.fetchone()[0]
    except Exception as e: pass"""

new_kpi_query = """            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM simulation_results WHERE event_type='round_end'")
            total_battles = c.fetchone()[0]
            
            # Since mock doesn't log battle_result, calculate defender wins from SIEM logs
            import os, json
            defender_wins = 0
            if os.path.exists("data/siem/nexus_events.ndjson"):
                with codecs.open("data/siem/nexus_events.ndjson", 'r', 'utf-8') as sf:
                    for line in sf:
                        if line.strip():
                            try:
                                if json.loads(line).get("event", {}).get("outcome") == "failure":
                                    defender_wins += 1
                            except: pass
    except Exception as e: pass"""

text = text.replace(old_kpi_query, new_kpi_query)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
