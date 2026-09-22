import codecs
import re

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the broken quotes
text = text.replace(
    'st.markdown("<p style=\'font-family:"Inter", sans-serif; color:#475569; line-height:1.6;\'>Powered by intelligent agents',
    'st.markdown("<p style=\'font-family:\\\'Inter\\\', sans-serif; color:#475569; line-height:1.6;\'>Powered by intelligent agents'
)
text = text.replace(
    'st.markdown("<p style=\'font-family:"Inter", sans-serif; color:#475569; line-height:1.6;\'>The Blue Team monitors',
    'st.markdown("<p style=\'font-family:\\\'Inter\\\', sans-serif; color:#475569; line-height:1.6;\'>The Blue Team monitors'
)
text = text.replace(
    'st.markdown("""\n        <p style=\'font-family:"Inter", sans-serif; color:#475569; line-height:1.6;\'>\n        The core reasoning engine',
    'st.markdown("""\n        <p style=\'font-family:\\\'Inter\\\', sans-serif; color:#475569; line-height:1.6;\'>\n        The core reasoning engine'
)

# And fix the ones inside """ multiline strings where we can just use regular single quotes without escaping
text = text.replace(
    "<p style='font-family:\"Inter\", sans-serif; font-size:1.15rem;",
    "<p style='font-family:\\'Inter\\', sans-serif; font-size:1.15rem;"
)
text = text.replace(
    "<p style='font-family:\"Inter\", sans-serif; font-size:1.05rem;",
    "<p style='font-family:\\'Inter\\', sans-serif; font-size:1.05rem;"
)
text = text.replace(
    "<ul style='font-family:\"Inter\", sans-serif; color:#475569;",
    "<ul style='font-family:\\'Inter\\', sans-serif; color:#475569;"
)
text = text.replace(
    "<ol style='font-family:\"Inter\", sans-serif; color:#475569;",
    "<ol style='font-family:\\'Inter\\', sans-serif; color:#475569;"
)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
