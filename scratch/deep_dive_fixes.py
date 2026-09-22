import codecs

with codecs.open('integrations/network_graph.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix 1: _render_figure looks for wrong dictionary keys for technique
old_tech_parsing = 'technique = log.get("technique_id", log.get("attack_technique", ""))'
new_tech_parsing = 'technique = log.get("technique", log.get("technique_id", log.get("attack_technique", "Unknown")))'

text = text.replace(old_tech_parsing, new_tech_parsing)

# Fix 2: _graph_from_logs unconditionally adds everything to compromised
old_comp_parsing = 'G.add_node(host, role=role)\n        compromised.add(host)'
new_comp_parsing = 'G.add_node(host, role=role)\n        if log.get("success") == False: compromised.add(host) # Assuming success=Defender success in this pipeline'

text = text.replace(old_comp_parsing, new_comp_parsing)

with codecs.open('integrations/network_graph.py', 'w', 'utf-8') as f:
    f.write(text)
