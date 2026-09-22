import codecs

with codecs.open('research/paper_generator.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the chart fonts to Arial (since Kaleido doesn't have system access to Space Grotesk) and fix the legend label
old_elo = 'fig_elo.update_layout(font_family="Space Grotesk", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", xaxis_title="Simulation Time", yaxis_title="ELO Rating")'
new_elo = 'fig_elo.update_layout(font_family="Arial", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", xaxis_title="Simulation Time", yaxis_title="ELO Rating")'

old_tech = 'fig_tech = px.bar(df_tech, x="technique", y=["detected", "evaded"], title="MITRE ATT&CK Effectiveness", barmode="stack", color_discrete_sequence=["#3b82f6", "#ef4444"])'
new_tech = 'fig_tech = px.bar(df_tech, x="technique", y=["detected", "evaded"], title="MITRE ATT&CK Effectiveness", barmode="stack", color_discrete_sequence=["#3b82f6", "#ef4444"], labels={"variable": "Outcome", "value": "Usages"})'

old_tech_layout = 'fig_tech.update_layout(font_family="Space Grotesk", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", xaxis_title="ATT&CK Technique", yaxis_title="Total Usages")'
new_tech_layout = 'fig_tech.update_layout(font_family="Arial", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", xaxis_title="ATT&CK Technique", yaxis_title="Total Usages")'

text = text.replace(old_elo, new_elo).replace(old_tech, new_tech).replace(old_tech_layout, new_tech_layout)

with codecs.open('research/paper_generator.py', 'w', 'utf-8') as f:
    f.write(text)
