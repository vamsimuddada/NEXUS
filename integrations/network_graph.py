"""
NEXUS — Live Network Graph
Builds an animated Plotly network graph from DigitalTwin state and live battle events.
Shows hosts as nodes, attack paths as animated edges, compromised nodes in red.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
import plotly.graph_objects as go
import codecs
import networkx as nx
import random
import sqlite3

# ── Role colours ─────────────────────────────────────────────────────────────
ROLE_COLORS = {
    "dc":          "#ef4444",   # red   — domain controller
    "fileserver":  "#3b82f6",   # blue
    "workstation": "#64748b",   # grey
    "webserver":   "#10b981",   # green
    "db":          "#f59e0b",   # amber
    "user":        "#8b5cf6",   # purple
}
COMPROMISED_COLOR  = "#ff0000"
ATTACKER_COLORS = {
    "VIPER":  "#8b5cf6",
    "KRAKEN": "#ef4444",
    "GHOST":  "#06b6d4",
    "HYDRA":  "#f59e0b",
    "NOVA":   "#ec4899",
    "CIPHER": "#10b981",
}

NEXUS_BG = "#ffffff"
NEXUS_PAPER = "#ffffff"


def build_graph_from_twin(twin, attack_logs: list[dict] | None = None,
                          compromised: list[str] | None = None) -> go.Figure:
    """
    Build an animated network graph from a live DigitalTwin object.

    Args:
        twin: DigitalTwin instance
        attack_logs: list of attack log dicts (optional)
        compromised: list of compromised hostnames (optional)
    Returns:
        Plotly Figure
    """
    G = nx.Graph()
    compromised = set(compromised or [])

    # Add nodes
    for host in twin.hosts:
        G.add_node(host.hostname, role=host.role, ip=host.ip,
                   is_dc=host.is_domain_controller)

    # Add edges (network topology)
    for (a, b) in twin.edges:
        src = twin.hosts[a].hostname if isinstance(a, int) else a
        dst = twin.hosts[b].hostname if isinstance(b, int) else b
        G.add_edge(src, dst)

    return _render_figure(G, twin.hosts, attack_logs or [], compromised)


def build_graph_from_db(db_path: str = "data/simulation_results.db",
                        battle_id: str | None = None) -> go.Figure:
    """
    Build a network graph from saved simulation results in SQLite.
    Falls back to a demo graph if no data found.
    """
    try:
        path = Path(db_path)
        if not path.exists():
            return _demo_graph()

        with sqlite3.connect(str(path)) as conn:
            conn.row_factory = sqlite3.Row
            # Get latest battle_id if not specified
            if not battle_id:
                row = conn.execute(
                    "SELECT sim_id FROM simulation_results ORDER BY id DESC LIMIT 1"
                ).fetchone()
                if not row:
                    return _demo_graph()
                battle_id = row["sim_id"]

            logs = conn.execute(
                "SELECT data FROM simulation_results WHERE sim_id=? AND event_type='attack_log'",
                (battle_id,)
            ).fetchall()

        attack_logs = []
        for row in logs:
            try:
                attack_logs.append(json.loads(row["data"]))
            except Exception:
                pass

        if not attack_logs:
            return _demo_graph()

        # Build synthetic graph from log data
        return _graph_from_logs(attack_logs)

    except Exception as e:
        print(f"[NetworkGraph] DB error: {e}")
        return _demo_graph()


def _graph_from_logs(attack_logs: list[dict]) -> go.Figure:
    """Build graph purely from attack log entries."""
    G = nx.Graph()
    compromised = set()
    hosts_seen = {}
    role_map = {}

    for log in attack_logs:
        host = log.get("host", "UNKNOWN")
        role = log.get("host_role", "workstation")
        src  = log.get("attacker", "ATTACKER")
        if host not in hosts_seen:
            hosts_seen[host] = len(hosts_seen)
            role_map[host] = role
            G.add_node(host, role=role)
        if log.get("success") == False: compromised.add(host) # Assuming success=Defender success in this pipeline

    # Add attacker node
    G.add_node("INTERNET", role="internet")

    # Connect attacker -> hosts
    for host in hosts_seen:
        G.add_edge("INTERNET", host)

    # Connect hosts to each other (star topology fallback)
    host_list = list(hosts_seen.keys())
    for i in range(len(host_list) - 1):
        G.add_edge(host_list[i], host_list[i + 1])

    # Build fake host objects for rendering
    class FakeHost:
        def __init__(self, hostname, role):
            self.hostname = hostname
            self.role = role
            self.ip = f"10.0.1.{random.randint(2,254)}"
            self.is_domain_controller = role == "dc"

    hosts = [FakeHost(h, role_map.get(h, "workstation")) for h in G.nodes
             if h != "INTERNET"]
    hosts.append(FakeHost("INTERNET", "internet"))

    return _render_figure(G, hosts, attack_logs, compromised)


def _render_figure(G: nx.Graph, hosts, attack_logs: list[dict],
                   compromised: set) -> go.Figure:
    """Core rendering function — builds the Plotly figure."""
    
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
        pass
        
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



    # Build host lookup
    host_map = {h.hostname: h for h in hosts}

    # --- Edges ---
    edge_traces = []
    for (u, v) in G.edges():
        x0, y0 = pos.get(u, (0, 0))
        x1, y1 = pos.get(v, (0, 0))
        edge_traces.append(go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            mode="lines",
            line=dict(width=1, color="#1e293b"),
            hoverinfo="none",
            showlegend=False,
        ))

    # --- Attack path edges (highlighted) ---
    attack_traces = []
    for log in attack_logs[-10:]:  # last 10 attacks
        host = log.get("host", "")
        attacker = log.get("attacker", "")
        technique = log.get("technique", log.get("technique_id", log.get("attack_technique", "Unknown")))
        color = ATTACKER_COLORS.get(attacker, "#ef4444")

        # Draw from INTERNET/attacker to target
        src_pos = pos.get(attacker, pos.get("INTERNET", pos.get(list(pos.keys())[0])))
        dst_pos = pos.get(host)
        if dst_pos is None:
            continue

        x0, y0 = src_pos
        x1, y1 = dst_pos
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2  # midpoint

        # 1. The Laser Projectile (Solid, but with CSS signature)
        attack_traces.append(go.Scatter(
            x=[x0, mx, x1, None], y=[y0, my, y1, None],
            mode="lines",
            line=dict(width=5.0, color=color, dash="1000px,1px"),
            hoverinfo="skip",
            opacity=0.9,
            showlegend=False
        ))
        
        # 2. The Data Flow (Dashed)
        attack_traces.append(go.Scatter(
            x=[x0, mx, x1, None], y=[y0, my, y1, None],
            mode="lines",
            line=dict(width=3.5, color=color, dash="dash"),
            name=f"{attacker} -> {host}",
            hovertemplate=f"<b>{attacker}</b><br>Technique: {technique}<br>Target: {host}<extra></extra>",
            opacity=0.8,
            showlegend=False
        ))

    # --- Nodes ---
    node_x, node_y, node_colors, node_sizes, node_text, node_hover = \
        [], [], [], [], [], []
    node_border_colors = []

    for node in G.nodes():
        if node not in pos:
            continue
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        host = host_map.get(node)
        role  = host.role if host else "workstation"
        is_comp = node in compromised

        # Color
        if is_comp:
            color = COMPROMISED_COLOR
            border = "#ff6b6b"
            size = 28
        elif role == "internet":
            color = "#334155"
            border = "#64748b"
            size = 22
        else:
            color = ROLE_COLORS.get(role, "#64748b")
            border = "white"
            size = 22 if role == "dc" else 18

        node_colors.append(color)
        node_border_colors.append(border)
        node_sizes.append(size)

        ip_str = f"<br>IP: {host.ip}" if host else ""
        comp_str = "<br><b style='color:#ef4444'>COMPROMISED</b>" if is_comp else ""
        node_hover.append(
            f"<b>{node}</b><br>Role: {role}{ip_str}{comp_str}<extra></extra>"
        )
        label = node[:8] if len(node) > 8 else node
        node_text.append(label)

    node_trace = go.Scatter(
        x=node_x, y=node_y, mode="markers+text",
        text=node_text, textposition="bottom center",
        textfont=dict(color="#94a3b8", size=10),
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(color=node_border_colors, width=2),
            symbol="circle",
        ),
        hovertemplate=node_hover,
        showlegend=False,
        name="Hosts",
    )

    # --- Legend traces (dummy) ---
    legend_traces = []
    for role, color in ROLE_COLORS.items():
        legend_traces.append(go.Scatter(
            x=[None], y=[None], mode="markers",
            marker=dict(size=10, color=color),
            name=role.title(), showlegend=True,
        ))
    legend_traces.append(go.Scatter(
        x=[None], y=[None], mode="markers",
        marker=dict(size=10, color=COMPROMISED_COLOR),
        name="Compromised", showlegend=True,
    ))

    fig = go.Figure(
        data=edge_traces + attack_traces + [node_trace] + legend_traces
    )
    fig.update_layout(
        height=550,
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(color="#3c4043", family="Open Sans"),
        showlegend=True,
        legend=dict(
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#dadce0", borderwidth=1,
            x=1.01, y=1,
        ),
        margin=dict(t=20, b=20, l=20, r=120),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        hoverlabel=dict(bgcolor="#ffffff", bordercolor="#dadce0", font_size=12, font_color="#202124"),
    )
    return fig


def _demo_graph() -> go.Figure:
    """Return a styled demo graph when no data is available."""
    G = nx.barabasi_albert_graph(8, 2, seed=42)
    roles = ["dc", "fileserver", "workstation", "workstation",
             "webserver", "workstation", "db", "workstation"]
    class FakeHost:
        def __init__(self, i):
            self.hostname = ["DC-001","FS-001","WS-001","WS-002",
                             "WEB-001","WS-003","DB-001","WS-004"][i]
            self.role = roles[i]
            self.ip = f"10.0.1.{10+i}"
            self.is_domain_controller = i == 0
    hosts = [FakeHost(i) for i in range(8)]
    mapping = {i: hosts[i].hostname for i in range(8)}
    G = nx.relabel_nodes(G, mapping)
    return _render_figure(G, hosts, [], set())


def build_graph_from_siem_logs(ndjson_path="data/siem/nexus_events.ndjson") -> go.Figure:
    import json
    import os
    import networkx as nx
    import plotly.graph_objects as go
    import codecs
    import codecs
    
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
                    if role == "workstation":
                        if hostname.startswith("DC"): role = "dc"
                        elif hostname.startswith("FS"): role = "fileserver"
                        elif hostname.startswith("DB"): role = "db"
                        elif hostname.startswith("WEB"): role = "webserver"
                    
                    attacker = log.get("labels", {}).get("nexus_attacker", "ATTACKER")
                    technique = log.get("threat", {}).get("technique", {}).get("name", "Unknown")
                    
                    
                    outcome = log.get("event", {}).get("outcome", "unknown")
                    
                    user_info = log.get("user", {})
                    user_name = user_info.get("name", "Unknown")
                    if user_name and user_name != "Unknown":
                        if user_name not in hosts:
                            hosts[user_name] = HostObj(user_name, "user")
                            G.add_node(user_name, role="user")
                        G.add_edge(user_name, hostname)

                    
                    user_info = log.get("user", {})
                    user_name = user_info.get("name", "Unknown")
                    if user_name and user_name != "Unknown":
                        if user_name not in hosts:
                            hosts[user_name] = HostObj(user_name, "user")
                            G.add_node(user_name, role="user")
                        G.add_edge(user_name, hostname)

                    
                    if hostname not in hosts:
                        hosts[hostname] = HostObj(hostname, role)
                        G.add_node(hostname, role=role)
                    
                    if attacker not in hosts:
                        hosts[attacker] = HostObj(attacker, "attacker")
                        G.add_node(attacker, role="attacker")
                        
                    if outcome == "failure":
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
