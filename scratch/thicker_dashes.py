import codecs

with codecs.open('integrations/network_graph.py', 'r', 'utf-8') as f:
    text = f.read()

# Change the dash pattern from "dot" to "dash" and increase width
old_line = 'line=dict(width=2.5, color=color, dash="dot"),'
new_line = 'line=dict(width=3.5, color=color, dash="dash"),'

text = text.replace(old_line, new_line)

with codecs.open('integrations/network_graph.py', 'w', 'utf-8') as f:
    f.write(text)
