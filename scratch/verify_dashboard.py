import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from dashboard.app_dash import update_dashboard

# Simulate a callback trigger (n_intervals=1)
kpis = update_dashboard(1)

print("--- DASHBOARD INTERNAL STATE CHECK ---")
print(f"Detection Rate: {kpis[0]}")
print(f"Defense Actions: {kpis[1]}")
print(f"Active Attackers: {kpis[2]}")
print(f"Rules Generated: {kpis[3]}")
print(f"GNN Retrains: {kpis[4]}")
print(f"Total Events: {kpis[5]}")

events_data = kpis[9]
print(f"\nNumber of events in table: {len(events_data)}")
if events_data:
    print(f"Sample Event 1: {events_data[0]}")
    if len(events_data) > 1:
        print(f"Sample Event 2: {events_data[1]}")

print("\n--- TRI-BRAIN STATS ---")
print(kpis[12]) # SIGMA
print(kpis[13]) # GNN
