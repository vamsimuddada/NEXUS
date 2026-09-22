import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

text = text.replace('get("outcome") == "failure":', 'get("outcome") == "success":')

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
