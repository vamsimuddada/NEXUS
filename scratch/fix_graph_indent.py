import codecs

with codecs.open('integrations/network_graph.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Fix the bad global indent
text = text.replace("    import codecs\nimport networkx", "import codecs\nimport networkx")

# 2. Add it inside the function
text = text.replace("import networkx as nx\n    import plotly.graph_objects as go\n", "import networkx as nx\n    import plotly.graph_objects as go\n    import codecs\n")

with codecs.open('integrations/network_graph.py', 'w', 'utf-8') as f:
    f.write(text)
