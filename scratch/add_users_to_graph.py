import codecs

with codecs.open('integrations/network_graph.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Update ROLE_COLORS to include "user"
if '"user":' not in text:
    text = text.replace('"db":          "#f59e0b",   # amber\n}', '"db":          "#f59e0b",   # amber\n    "user":        "#8b5cf6",   # purple\n}')

# 2. Add users to the graph in build_graph_from_siem_logs
user_extract = """
                    outcome = log.get("event", {}).get("outcome", "unknown")
                    
                    user_info = log.get("user", {})
                    user_name = user_info.get("name", "Unknown")
                    if user_name and user_name != "Unknown":
                        if user_name not in hosts:
                            hosts[user_name] = HostObj(user_name, "user")
                            G.add_node(user_name, role="user")
                        G.add_edge(user_name, hostname)
"""
text = text.replace('outcome = log.get("event", {}).get("outcome", "unknown")', user_extract)

with codecs.open('integrations/network_graph.py', 'w', 'utf-8') as f:
    f.write(text)
