import codecs
with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

text = text.replace('font-family: "Google Sans", sans-serif;', "font-family: 'Google Sans', sans-serif;")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
