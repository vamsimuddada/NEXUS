import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

old_call = """            from integrations.network_graph import build_graph_from_siem_logs
            fig2 = build_graph_from_siem_logs()"""

new_call = """            import importlib
            import integrations.network_graph
            importlib.reload(integrations.network_graph)
            from integrations.network_graph import build_graph_from_siem_logs
            fig2 = build_graph_from_siem_logs()"""

text = text.replace(old_call, new_call)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
