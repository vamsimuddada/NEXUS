import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Strip out the escaping backslashes that are breaking the CSS font-family in the browser!
text = text.replace('font-family:\\\'Inter\\\'', "font-family:'Inter'")
text = text.replace('font-family:\\\'JetBrains Mono\\\'', "font-family:'JetBrains Mono'")
text = text.replace('font-family:\\"Inter\\"', "font-family:'Inter'")

# And for those still stuck with broken single-quoted style attributes:
text = text.replace("style='font-family:\\'Inter\\',", "style=\"font-family:'Inter',")
text = text.replace('style=\'font-family:\\\'Inter\\\',', 'style="font-family:\'Inter\',')

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
