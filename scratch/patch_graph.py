import codecs

with codecs.open('integrations/network_graph.py', 'r', 'utf-8') as f:
    text = f.read()

new_graph_func = """

def build_graph_from_siem_logs(ndjson_path="data/siem/nexus_events.ndjson") -> go.Figure:
    import json
    import os
    import networkx as nx
    import plotly.graph_objects as go
    
    if not os.path.exists(ndjson_path):
        return _demo_graph()
        
    G = nx.Graph()
    compromised = set()
    hosts = {}
    attack_logs = []
    
    class HostObj:
        def __init__(self, hostname, role):
            self.hostname = hostname
            self.role = role
            self.ip = "10.0.0.x"
            self.is_domain_controller = ("DC" in hostname.upper())

    try:
        with codecs.open(ndjson_path, 'r', 'utf-8') as f:
            for line in f:
                if not line.strip(): continue
                try:
                    log = json.loads(line)
                    host_info = log.get("host", {})
                    hostname = host_info.get("name", "Unknown")
                    role = host_info.get("type", "workstation")
                    attacker = log.get("labels", {}).get("nexus_attacker", "ATTACKER")
                    technique = log.get("threat", {}).get("technique", {}).get("name", "Unknown")
                    outcome = log.get("event", {}).get("outcome", "unknown")
                    
                    if hostname not in hosts:
                        hosts[hostname] = HostObj(hostname, role)
                        G.add_node(hostname, role=role)
                    
                    if attacker not in hosts:
                        hosts[attacker] = HostObj(attacker, "attacker")
                        G.add_node(attacker, role="attacker")
                        
                    if outcome == "success":
                        compromised.add(hostname)
                    
                    # Create an edge for the attack
                    G.add_edge(attacker, hostname)
                    
                    # The _render_figure expects dicts with "host", "attacker", "technique"
                    attack_logs.append({
                        "host": hostname,
                        "attacker": attacker,
                        "technique": technique,
                        "success": (outcome == "success")
                    })
                except:
                    pass
    except Exception as e:
        print(f"SIEM parse error: {e}")
        return _demo_graph()

    if not G.nodes:
        return _demo_graph()
        
    return _render_figure(G, list(hosts.values()), attack_logs, compromised)
"""

if "build_graph_from_siem_logs" not in text:
    with codecs.open('integrations/network_graph.py', 'w', 'utf-8') as f:
        f.write(text + new_graph_func)

# Now modify dashboard.py to use this function
with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    dash = f.read()

dash = dash.replace("from integrations.network_graph import build_graph_from_db", "from integrations.network_graph import build_graph_from_siem_logs")
dash = dash.replace("fig2 = build_graph_from_db()", "fig2 = build_graph_from_siem_logs()")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(dash)
