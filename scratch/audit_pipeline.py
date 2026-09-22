import sys
import os
import sqlite3
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from nexus.simulation import BattleEngine
from nexus.utils import get_logger

print("--- FULL PIPELINE AUDIT ---")

engine = BattleEngine()
print(f"Engine initialized. sim_id={engine.sim_id}")

engine.setup_simulation(num_employees=5, num_subnets=2)
print("Enterprise setup complete.")

print("Verifying DB Paths...")
print("Results:", engine.results_collector.db_path)
print("ELO:", engine.elo_system.db_path)

# Let's forcefully execute one round
action = {'action': 'scan_network', 'technique_id': 'T1046', 'target': '10.0.0.1'}
result = engine.attackers[0].execute_action(action, engine.environment)
print("Attacker execution:", result.get("success"))

if result.get("success"):
    logs = result.get('logs_generated', [])
    print(f"Generated logs: {len(logs)}")
    
    # Save to results
    engine.results_collector.record(engine.sim_id, 0, "attacker_action", result)
    
    # Tri brain evaluate
    if logs:
        eval_res = engine.tri_brain.evaluate(logs[0], None)
        print("Tri-Brain Verdict:", eval_res.get('verdict'))
        
        # Evolution Engine gap analysis
        if hasattr(engine, 'evolution_engine'):
            engine.evolution_engine.analyze_gap(logs[0], eval_res)
            print("Gap Analysis triggered.")

print("\n--- CHECKING DATABASES AFTER TEST ---")

def check_table(db, query):
    try:
        with sqlite3.connect(db) as conn:
            c = conn.cursor()
            c.execute(query)
            print(f"[{db}] {query} -> {c.fetchone()[0]} rows")
    except Exception as e:
        print(f"[{db}] ERROR: {e}")

check_table("data/simulation_results.db", "SELECT count(*) FROM simulation_results")
check_table("data/nexus_elo.db", "SELECT count(*) FROM elo_ratings")
check_table("data/nexus_gaps.db", "SELECT count(*) FROM gap_analysis")
check_table("data/nexus_training.db", "SELECT count(*) FROM training_history")

print("Audit Complete.")
