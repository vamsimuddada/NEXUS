import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Apply the premium cyber button CSS to download buttons as well
text = text.replace(
    '.stButton > button {',
    '.stButton > button, .stDownloadButton > button {'
)
text = text.replace(
    '.stButton > button:hover {',
    '.stButton > button:hover, .stDownloadButton > button:hover {'
)

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
