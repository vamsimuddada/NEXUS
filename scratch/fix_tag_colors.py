import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

old_span = "<span style='background:rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); color:#ef4444;"
new_span = "<span style='background:#f1f5f9; border: 1px solid #e2e8f0; color:#334155;"

text = text.replace(old_span, new_span)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
