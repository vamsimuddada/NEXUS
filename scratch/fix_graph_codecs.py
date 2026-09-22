import codecs

with codecs.open('integrations/network_graph.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Remove the bad import codecs from the very top that broke __future__
if text.startswith("import codecs\n"):
    text = text.replace("import codecs\n", "", 1)

# 2. Add import codecs INSIDE the build_graph_from_siem_logs function
text = text.replace(
    "import plotly.graph_objects as go",
    "import plotly.graph_objects as go\n    import codecs"
)

with codecs.open('integrations/network_graph.py', 'w', 'utf-8') as f:
    f.write(text)
