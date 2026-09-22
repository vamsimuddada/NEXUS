import codecs
with codecs.open('integrations/network_graph.py', 'r', 'utf-8') as f:
    text = f.read()

bad_line = 'src_pos = pos.get("INTERNET", pos.get(list(pos.keys())[0]))'
good_line = 'src_pos = pos.get(attacker, pos.get("INTERNET", pos.get(list(pos.keys())[0])))'

text = text.replace(bad_line, good_line)

with codecs.open('integrations/network_graph.py', 'w', 'utf-8') as f:
    f.write(text)
