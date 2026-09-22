import sys
import os
import time
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from dashboard.app_dash import update_dashboard

print("--- DASHBOARD LIVE VERIFICATION ---")
print("Monitoring Dashboard UI values as the simulation runs...\n")

for i in range(5):
    try:
        kpis = update_dashboard(1)
        print(f"[Dashboard Poll {i+1}]")
        print(f"Total Events: {kpis[5]}")
        print(f"Active Attackers: {kpis[2]}")
        print(f"Detection Rate: {kpis[0]}")
        events_data = kpis[9]
        print(f"Rows in Event Table: {len(events_data)}")
        print("-" * 30)
    except Exception as e:
        print(f"Dashboard crashed: {e}")
    time.sleep(2)
