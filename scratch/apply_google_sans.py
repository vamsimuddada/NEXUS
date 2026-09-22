import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Replace Inter and Space Grotesk with Google Sans
text = text.replace("'Inter', sans-serif", "'Google Sans', sans-serif")
text = text.replace("'Space Grotesk', sans-serif", "'Google Sans', sans-serif")
text = text.replace('"Space Grotesk", sans-serif', "'Google Sans', sans-serif")
text = text.replace("'Inter', sans-serif !important", "'Google Sans', sans-serif !important")

# Some inline styles might just say font-family:'Space Grotesk'
text = re.sub(r"font-family:\s*\\?['\"]Space Grotesk\\?['\"]", "font-family: 'Google Sans'", text)
text = re.sub(r"font-family:\s*\\?['\"]Inter\\?['\"]", "font-family: 'Google Sans'", text)

# Just to be extremely thorough, also replace Open Sans if it exists
text = text.replace("'Open Sans', sans-serif", "'Google Sans', sans-serif")

# We can also add a small CSS block to define a @font-face for Google Sans if they don't have it locally,
# but it's safer to just let it fallback to sans-serif if not found.
# Many users asking for "Google Sans" just want the font-family rule applied.

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
