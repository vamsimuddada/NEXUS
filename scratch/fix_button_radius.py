import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Change the heavy border-radius of the buttons to a tighter, more rectangular shape
text = text.replace(
    "border-radius: 16px !important;",
    "border-radius: 6px !important;"
)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
