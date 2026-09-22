import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Append a timestamp to the downloaded PDF filename to forcefully bypass browser caching
old_button = 'file_name="NEXUS_Executive_Report.pdf"'
new_button = 'file_name=f"NEXUS_Executive_Report_{int(time.time())}.pdf"'
text = text.replace(old_button, new_button)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
