import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

text = text.replace("'Inter'", "'Space Grotesk'")
text = text.replace('"Inter"', '"Space Grotesk"')

# Except for the import URL, but that's fine, we can leave it importing both.
text = text.replace("family=Space Grotesk", "family=Inter") # just fix the import if we broke it
text = text.replace("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk", "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
