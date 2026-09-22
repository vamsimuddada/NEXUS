import codecs
import re

with codecs.open('integrations/network_graph.py', 'r', 'utf-8') as f:
    text = f.read()

old_trace = """        attack_traces.append(go.Scatter(
            x=[x0, mx, x1, None], y=[y0, my, y1, None],
            mode="lines",
            line=dict(width=3.5, color=color, dash="dash"),
            name=f"{attacker} -> {host}",
            hovertemplate=f"<b>{attacker}</b><br>Technique: {technique}<br>Target: {host}<extra></extra>",
            opacity=0.8
        ))"""

# We add a SOLID laser trace first, then the DASHED flow trace on top of it.
new_trace = """        # 1. The Laser Projectile (Solid)
        attack_traces.append(go.Scatter(
            x=[x0, mx, x1, None], y=[y0, my, y1, None],
            mode="lines",
            line=dict(width=5.0, color=color, dash="solid"),
            hoverinfo="skip",
            opacity=0.9
        ))
        
        # 2. The Data Flow (Dashed)
        attack_traces.append(go.Scatter(
            x=[x0, mx, x1, None], y=[y0, my, y1, None],
            mode="lines",
            line=dict(width=3.5, color=color, dash="dash"),
            name=f"{attacker} -> {host}",
            hovertemplate=f"<b>{attacker}</b><br>Technique: {technique}<br>Target: {host}<extra></extra>",
            opacity=0.8
        ))"""

text = text.replace(old_trace, new_trace)

with codecs.open('integrations/network_graph.py', 'w', 'utf-8') as f:
    f.write(text)
