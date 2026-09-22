import codecs
import re

with codecs.open('integrations/network_graph.py', 'r', 'utf-8') as f:
    text = f.read()

# Change the laser trace dash to a custom signature string so CSS can perfectly target it
old_laser = 'line=dict(width=5.0, color=color, dash="solid"),'
new_laser = 'line=dict(width=5.0, color=color, dash="1000px,1px"),  # CSS signature target'

text = text.replace(old_laser, new_laser)

with codecs.open('integrations/network_graph.py', 'w', 'utf-8') as f:
    f.write(text)
