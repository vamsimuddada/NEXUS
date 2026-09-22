import codecs

with codecs.open('integrations/network_graph.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the compromised logic so that a host is only marked as Compromised (red) 
# if the SIEM failed to detect the attack (outcome == "failure")
old_logic = 'if outcome == "success":\n                        compromised.add(hostname)'
new_logic = 'if outcome == "failure":\n                        compromised.add(hostname)'

text = text.replace(old_logic, new_logic)

with codecs.open('integrations/network_graph.py', 'w', 'utf-8') as f:
    f.write(text)
