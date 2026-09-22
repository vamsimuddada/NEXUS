import codecs

with codecs.open('integrations/network_graph.py', 'r', 'utf-8') as f:
    text = f.read()

if "import codecs" not in text:
    text = "import codecs\n" + text
    
with codecs.open('integrations/network_graph.py', 'w', 'utf-8') as f:
    f.write(text)
