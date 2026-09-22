import codecs
import re

with codecs.open('integrations/network_graph.py', 'r', 'utf-8') as f:
    text = f.read()

# Put back the 1000px dash signature
old_laser = 'line=dict(width=5.0, color=color, dash="solid"),\n            legendgroup="laser",'
new_laser = 'line=dict(width=5.0, color=color, dash="1000px,1px"),'

text = text.replace(old_laser, new_laser)

with codecs.open('integrations/network_graph.py', 'w', 'utf-8') as f:
    f.write(text)
