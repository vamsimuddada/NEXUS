import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

text = text.replace(
    "target_str = targets[0] if isinstance(targets, list) else targets",
    "target_str = ', '.join(targets) if isinstance(targets, list) else targets"
)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
