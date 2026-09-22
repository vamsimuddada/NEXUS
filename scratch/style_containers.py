import codecs
with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

container_css = """
/* Enhance Streamlit native containers (st.container(border=True)) */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 20px !important;
    border: 1px solid rgba(226, 232, 240, 0.8) !important;
    background: #ffffff !important;
    box-shadow: 0 4px 15px rgba(15, 23, 42, 0.02) !important;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 10px 25px rgba(15, 23, 42, 0.04) !important;
    border-color: rgba(148, 163, 184, 0.3) !important;
}
"""

text = text.replace('</style>', container_css + '\n</style>')

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
