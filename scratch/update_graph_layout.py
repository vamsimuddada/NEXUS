import codecs

with codecs.open('integrations/network_graph.py', 'r', 'utf-8') as f:
    text = f.read()

# Replace the spring_layout with a structured multipartite layout
old_layout = "pos = nx.spring_layout(G, seed=42, k=2.5)"
new_layout = """
    # Assign hierarchical layers for a clean, structured topology design
    for node, data in G.nodes(data=True):
        role = data.get("role", "").lower()
        if role == "attacker":
            data["layer"] = 0  # Top: External Threat Actors
        elif role == "webserver":
            data["layer"] = 1  # Perimeter: Web Facing
        elif role in ["dc", "fileserver", "db"]:
            data["layer"] = 2  # Core: Internal Servers
        elif role == "workstation":
            data["layer"] = 3  # Endpoints: Workstations
        elif role == "user":
            data["layer"] = 4  # Bottom: Human Users
        else:
            data["layer"] = 5
            
    try:
        import networkx as nx
        pos = nx.multipartite_layout(G, subset_key="layer", align="horizontal")
        
        # Scale the layout to spread it out beautifully
        for k in pos:
            pos[k] = (pos[k][0] * 2.5, pos[k][1] * 1.5)
            
    except Exception:
        pos = nx.spring_layout(G, seed=42, k=2.5)
"""

text = text.replace(old_layout, new_layout)

with codecs.open('integrations/network_graph.py', 'w', 'utf-8') as f:
    f.write(text)
