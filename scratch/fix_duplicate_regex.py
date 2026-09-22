import codecs
import re

with codecs.open('integrations/network_graph.py', 'r', 'utf-8') as f:
    text = f.read()

# Duplicate the attack trace using regex
# We capture the hovertemplate part so we can safely inject the dual trace
text = re.sub(
    r'attack_traces\.append\(go\.Scatter\(\s*x=\[x0, mx, x1, None\], y=\[y0, my, y1, None\],\s*mode="lines",\s*line=dict\(width=3\.5, color=color, dash="dash"\),\s*name=f"\{attacker\} -> \{host\}",\s*hovertemplate=f"<b>\{attacker\}</b><br>Technique: \{technique\}<br>Target: \{host\}<extra></extra>",\s*\)\)',
    r'''# 1. The Laser Projectile (Solid, but with CSS signature)
        attack_traces.append(go.Scatter(
            x=[x0, mx, x1, None], y=[y0, my, y1, None],
            mode="lines",
            line=dict(width=5.0, color=color, dash="1000px,1px"),
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
        ))''',
    text
)

with codecs.open('integrations/network_graph.py', 'w', 'utf-8') as f:
    f.write(text)
