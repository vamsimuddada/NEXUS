import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the mismatched quotes in the style attributes!
text = re.sub(
    r'(style="font-family:[^>]+?)\'>',
    r'\1">',
    text
)

# And fix any that have single quotes on the outside but double quotes on the inside
text = re.sub(
    r'(style=\'font-family:[^>]+?)\">',
    r"\1'>",
    text
)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
