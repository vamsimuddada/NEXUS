import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

safe_css = """
/*  Progress Bar Integration  */
[data-testid="stMarkdownContainer"] p {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 800 !important;
    color: #3b82f6 !important;
    letter-spacing: 0.5px !important;
    font-size: 1rem !important;
}
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #0ea5e9, #3b82f6) !important;
}
"""

text = text.replace("</style>", safe_css + "\n</style>")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
