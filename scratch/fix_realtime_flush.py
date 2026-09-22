import codecs

with codecs.open('integrations/siem_forwarder.py', 'r', 'utf-8') as f:
    text = f.read()

# Change the auto-flush threshold from 50 to 1 so the dashboard updates in real-time
text = text.replace("if len(self._buffer) >= 50:", "if len(self._buffer) >= 1:")

with codecs.open('integrations/siem_forwarder.py', 'w', 'utf-8') as f:
    f.write(text)
