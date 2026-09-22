import codecs

with codecs.open('scripts/dashboard.py', 'r', 'utf-8') as f:
    text = f.read()

# Fix the broken string exactly
text = text.replace(
"""table_html = "<style>.fw-row { background-color: #ffffff; box-shadow: 0 1px 2px rgba(15,23,42,0.04); transition: all 0.2s ease; } .fw-row:hover { transform: translateX(4px); box-shadow: 0 4px 12px rgba(15,23,42,0.08); border-left-color: #0f172a !important; }
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

</style>\"""", """table_html = "<style>.fw-row { background-color: #ffffff; box-shadow: 0 1px 2px rgba(15,23,42,0.04); transition: all 0.2s ease; } .fw-row:hover { transform: translateX(4px); box-shadow: 0 4px 12px rgba(15,23,42,0.08); border-left-color: #0f172a !important; }</style>\"""")

with codecs.open('scripts/dashboard.py', 'w', 'utf-8') as f:
    f.write(text)
