import codecs

with codecs.open('core/simulation.py', 'r', 'utf-8') as f:
    text = f.read()

# Inject the flush command right before the battle report is returned
idx = text.find('return report')
if idx != -1:
    flush_code = """
        try:
            from integrations.siem_forwarder import get_forwarder
            get_forwarder().flush()
        except Exception:
            pass
        """
    text = text[:idx] + flush_code + text[idx:]

with codecs.open('core/simulation.py', 'w', 'utf-8') as f:
    f.write(text)
