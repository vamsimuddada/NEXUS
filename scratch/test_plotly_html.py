import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from integrations.network_graph import build_graph_from_siem_logs

# Build the graph
fig = build_graph_from_siem_logs()

# Get the raw HTML string exactly as it would be sent to the browser
html = fig.to_html(full_html=False, include_plotlyjs=False)

# Look for our custom stroke-dasharray signature
lines = [line for line in html.split('\n') if "1000px" in line or "dasharray" in line]
print(f"Found {len(lines)} lines with dasharray.")
if len(lines) > 0:
    for i, line in enumerate(lines[:5]):
        print(f"Line {i}: {line[:200]}")
    
# Let's also check what Plotly puts inside the JSON configuration!
import json
print("Plotly JSON check:")
print(json.dumps(fig.to_dict())[:500])
