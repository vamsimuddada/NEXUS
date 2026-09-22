import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# 1. Lower the base font size to 12.5px (effectively 78% scale)
text = text.replace("html { font-size: 14px !important; }", "html { font-size: 12.5px !important; }")

# 2. Expand the block container so it fills the screen perfectly without cutting off
container_css = """
/* Force Streamlit to use maximum screen real estate */
.block-container {
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-top: 1.5rem !important;
    max-width: 100% !important;
}
"""
text = text.replace("</style>", container_css + "\n</style>")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
