import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Force Inter onto paragraphs
text = text.replace(
    "<p style='font-size:1.15rem;",
    "<p style='font-family:\"Inter\", sans-serif; font-size:1.15rem;"
)
text = text.replace(
    "<p style='font-size:1.05rem;",
    "<p style='font-family:\"Inter\", sans-serif; font-size:1.05rem;"
)
text = text.replace(
    "<p style='color:#475569;",
    "<p style='font-family:\"Inter\", sans-serif; color:#475569;"
)
text = text.replace(
    "<ul style='color:#475569;",
    "<ul style='font-family:\"Inter\", sans-serif; color:#475569;"
)
text = text.replace(
    "<ol style='color:#475569;",
    "<ol style='font-family:\"Inter\", sans-serif; color:#475569;"
)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
