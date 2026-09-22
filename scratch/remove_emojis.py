import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Strip the emojis from the buttons
text = text.replace('"🚀 START CAMPAIGN"', '"START CAMPAIGN"')
text = text.replace('"🛑 HALT CAMPAIGN"', '"HALT CAMPAIGN"')

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
