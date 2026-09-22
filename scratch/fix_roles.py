import codecs

with codecs.open('integrations/network_graph.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the role parsing logic in build_graph_from_siem_logs
old_role_parsing = """                    role = host_info.get("type", "workstation")
                    attacker = log.get("labels", {}).get("nexus_attacker", "ATTACKER")"""

new_role_parsing = """                    role = host_info.get("type", "workstation")
                    if role == "workstation":
                        if hostname.startswith("DC"): role = "dc"
                        elif hostname.startswith("FS"): role = "fileserver"
                        elif hostname.startswith("DB"): role = "db"
                        elif hostname.startswith("WEB"): role = "webserver"
                    
                    attacker = log.get("labels", {}).get("nexus_attacker", "ATTACKER")"""

text = text.replace(old_role_parsing, new_role_parsing)

with codecs.open('integrations/network_graph.py', 'w', 'utf-8') as f:
    f.write(text)
