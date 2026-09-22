import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

text = text.replace('family="Inter"', 'family="Google Sans"')
text = text.replace("family='Inter'", "family='Google Sans'")

# Just to be completely clean, replace the google fonts import too
text = text.replace("@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700;800&display=swap');", "")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
