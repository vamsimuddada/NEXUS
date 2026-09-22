import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the bug where 'tools' was queried instead of 'techniques'
text = text.replace("profile.get('tools', [])", "profile.get('techniques', [])")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
